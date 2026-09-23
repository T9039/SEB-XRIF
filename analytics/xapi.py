"""xAPI ingestion: CSV -> statements -> Learning Record Store -> feature table.

This is the framework's data-layer contract made concrete. Each learner row is
turned into standard xAPI statements (a registration statement carrying the
demographics, one statement per behavioural metric, and a completion statement
carrying the outcome), posted to an LRS, and read back into a feature table that
validates against the same schema as the CSV.

Only the transport changes between the CSV prototype and a real deployment; the
statements and the reconstruction are the standard part.

Examples:
    uv run python -m analytics.xapi ingest --limit 20
    uv run python -m analytics.xapi read --limit 20
    uv run python -m analytics.xapi load-db --limit 20
"""

from __future__ import annotations

import argparse
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx
import pandas as pd

from .config import get_settings
from .data import load_raw
from .db import FRAME_TO_DB, get_engine, session_scope, upsert_learner
from .schema import BEHAVIOURAL, CATEGORICAL

BASE = "http://seb-xrif.dut.ac.za"
DEMOGRAPHICS_EXT = f"{BASE}/extensions/demographics"
TARGET_EXT = f"{BASE}/extensions/target_class"

VERB_REGISTERED = "http://adlnet.gov/expapi/verbs/registered"
VERB_PROGRESSED = "http://adlnet.gov/expapi/verbs/progressed"
VERB_COMPLETED = "http://adlnet.gov/expapi/verbs/completed"

#: Demographic columns carried on the registration statement.
DEMOGRAPHIC_COLUMNS = tuple(CATEGORICAL)

FEATURE_COLUMNS = [*CATEGORICAL, *BEHAVIOURAL, "Class"]


def learner_id(index: int) -> str:
    """Return a stable external identifier for a learner row."""
    return f"L{index:04d}"


def _actor(external_id: str) -> dict[str, Any]:
    return {"mbox": f"mailto:{external_id.lower()}@dut4life.ac.za", "name": external_id}


def _statement(actor: dict, verb: str, obj: str, **extra: Any) -> dict[str, Any]:
    statement = {
        "id": str(uuid.uuid4()),
        "actor": actor,
        "verb": {"id": verb, "display": {"en-US": verb.rsplit("/", 1)[-1]}},
        "object": {"id": obj, "objectType": "Activity"},
        "timestamp": datetime.now(UTC).isoformat(),
    }
    statement.update(extra)
    return statement


def build_statements(row: dict[str, Any], external_id: str) -> list[dict[str, Any]]:
    """Convert one learner row into a list of xAPI statements."""
    actor = _actor(external_id)
    topic = str(row["Topic"])
    course = f"{BASE}/activities/course/{topic}"

    statements = [
        _statement(
            actor,
            VERB_REGISTERED,
            course,
            context={
                "extensions": {
                    DEMOGRAPHICS_EXT: {
                        column: str(row[column]) for column in DEMOGRAPHIC_COLUMNS
                    }
                }
            },
        )
    ]

    for behaviour in BEHAVIOURAL:
        statements.append(
            _statement(
                actor,
                VERB_PROGRESSED,
                f"{BASE}/activities/behaviour/{behaviour}",
                result={"score": {"raw": float(row[behaviour])}},
            )
        )

    statements.append(
        _statement(
            actor,
            VERB_COMPLETED,
            course,
            context={"extensions": {TARGET_EXT: str(row["Class"])}},
        )
    )
    return statements


class LrsClient:
    """Minimal xAPI client for a Learning Record Store."""

    def __init__(
        self,
        endpoint: str | None = None,
        key: str | None = None,
        secret: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        settings = get_settings()
        self.endpoint = (endpoint or settings.lrs_endpoint).rstrip("/")
        self.auth = (key or settings.lrs_key, secret or settings.lrs_secret)
        self.timeout = timeout

    @property
    def statements_url(self) -> str:
        return f"{self.endpoint}/statements"

    def _headers(self) -> dict[str, str]:
        return {
            "X-Experience-API-Version": "1.0.3",
            "Content-Type": "application/json",
        }

    def post_statements(self, statements: list[dict[str, Any]]) -> list[str]:
        """Store statements and return their ids."""
        response = httpx.post(
            self.statements_url,
            json=statements,
            auth=self.auth,
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return list(response.json())

    def get_statements(
        self, limit: int = 100, page_size: int = 50
    ) -> list[dict[str, Any]]:
        """Fetch statements from the LRS, following ``more`` pagination."""
        from urllib.parse import urlsplit

        collected: list[dict[str, Any]] = []
        split = urlsplit(self.endpoint)
        base = f"{split.scheme}://{split.netloc}"
        url: str = self.statements_url
        params: dict[str, Any] | None = {"limit": min(page_size, limit)}

        while True:
            response = httpx.get(
                url,
                params=params,
                auth=self.auth,
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            collected.extend(data.get("statements", []))

            more = data.get("more")
            if not more or len(collected) >= limit:
                break
            url = more if more.startswith("http") else base + more
            params = None

        return collected[:limit]

    def ping(self) -> bool:
        """Return True when the LRS is reachable and authorised."""
        try:
            response = httpx.get(
                self.statements_url,
                params={"limit": 1},
                auth=self.auth,
                headers=self._headers(),
                timeout=self.timeout,
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False


def extract_rows(statements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reconstruct learner feature rows from xAPI statements."""
    grouped: dict[str, dict[str, Any]] = {}
    for statement in statements:
        actor = statement.get("actor", {})
        mbox = actor.get("mbox") or actor.get("name")
        if not mbox:
            continue
        row = grouped.setdefault(mbox, {})
        row["external_id"] = actor.get("name") or mbox
        verb = statement.get("verb", {}).get("id", "")
        obj = str(statement.get("object", {}).get("id", ""))
        extensions = statement.get("context", {}).get("extensions", {}) or {}

        if DEMOGRAPHICS_EXT in extensions:
            row.update(extensions[DEMOGRAPHICS_EXT])
            row["Topic"] = obj.rsplit("/", 1)[-1]
        elif "/behaviour/" in obj:
            behaviour = obj.rsplit("/", 1)[-1]
            score = statement.get("result", {}).get("score", {})
            row[behaviour] = int(score.get("raw", 0))
        elif TARGET_EXT in extensions:
            row["Class"] = extensions[TARGET_EXT]
        _ = verb
    return [row for row in grouped.values() if row]


def frame_from_statements(statements: list[dict[str, Any]]) -> pd.DataFrame:
    """Return a feature DataFrame in the same shape as the source CSV."""
    return pd.DataFrame(extract_rows(statements), columns=FEATURE_COLUMNS)


def to_learner_dict(row: dict[str, Any], external_id: str) -> dict[str, Any]:
    """Map a reconstructed row to application database field names."""
    data = {"external_id": external_id}
    for source, target in FRAME_TO_DB.items():
        if source in row:
            data[target] = row[source]
    return data


def ingest_csv(client: LrsClient, limit: int | None = None) -> int:
    """Read the source CSV and post statements for each learner row."""
    frame = load_raw()
    if limit is not None:
        frame = frame.head(limit)
    posted = 0
    for index, (_, row) in enumerate(frame.iterrows()):
        statements = build_statements(row.to_dict(), learner_id(index))
        posted += len(client.post_statements(statements))
    return posted


def load_rows_into_db(rows: list[dict[str, Any]], url: str | None = None) -> int:
    """Load reconstructed rows into the application database.

    Rows that do not carry every feature (for example statements from another
    actor that do not form a complete learner) are skipped rather than failing
    the whole batch.
    """
    engine = get_engine(url)
    loaded = 0
    with session_scope(engine) as session:
        for index, row in enumerate(rows):
            if not all(column in row for column in FEATURE_COLUMNS):
                continue
            external_id = str(row.get("external_id") or learner_id(index))
            upsert_learner(session, to_learner_dict(row, external_id))
            loaded += 1
    return loaded


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="xAPI ingestion utilities.")
    parser.add_argument("command", choices=["ingest", "read", "load-db"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--endpoint", default=None)
    parser.add_argument("--key", default=None)
    parser.add_argument("--secret", default=None)
    parser.add_argument("--url", default=None, help="Database URL for load-db.")
    args = parser.parse_args(argv)

    client = LrsClient(args.endpoint, args.key, args.secret)

    if args.command == "ingest":
        posted = ingest_csv(client, args.limit)
        print(f"Posted {posted} statements to {client.endpoint}")
        return

    statements = client.get_statements(limit=args.limit or 10000)
    frame = frame_from_statements(statements)
    print(f"Reconstructed {len(frame)} learner rows from {len(statements)} statements")
    print(frame.head().to_string())

    if args.command == "load-db":
        loaded = load_rows_into_db(extract_rows(statements), url=args.url)
        print(f"Loaded {loaded} learners into the database")


if __name__ == "__main__":
    main()
