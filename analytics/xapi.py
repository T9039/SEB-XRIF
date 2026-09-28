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
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pandas as pd

from .config import get_settings
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


def read_statements(path: Path | str) -> list[dict[str, Any]]:
    """Read xAPI statements from a JSON array or a JSON Lines file.

    This is how a profile-conformant source is ingested without code: the
    statements are exported from an LRS and dropped in as a file.
    """
    statements = statements_from_text(Path(path).read_text(encoding="utf-8"))
    if not statements:
        raise ValueError(f"No xAPI statements found in {path}")
    return statements


def statements_from_text(text: str) -> list[dict[str, Any]]:
    """Parse a JSON array or JSON Lines string into a statement list."""
    if text.lstrip().startswith("["):
        payload = json.loads(text)
        return list(payload) if isinstance(payload, list) else []
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def to_learner_dict(row: dict[str, Any], external_id: str) -> dict[str, Any]:
    """Map a reconstructed row to application database field names."""
    data = {"external_id": external_id}
    for source, target in FRAME_TO_DB.items():
        if source in row:
            data[target] = row[source]
    return data


#: JSON-path-ish helper keys for the flattened statement table.
STATEMENT_COLUMNS = [
    "id",
    "timestamp",
    "actor",
    "verb",
    "object",
    "object_name",
    "result_score",
    "result_success",
    "result_completion",
    "result_response",
    "language",
    "extensions",
]


def _first_value(mapping: Any) -> Any:
    """Return the first value of a ``{"en-US": ...}`` display mapping."""
    if isinstance(mapping, dict) and mapping:
        return next(iter(mapping.values()))
    return mapping


def flatten_statements(statements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten arbitrary xAPI statements into tidy rows.

    This is the bridge for non-conformant sources: whatever their vocabulary,
    every statement is reduced to identifiable columns (actor, verb, object,
    result fields, language, extensions) that can be exported as a CSV and then
    adapted to features with a column mapping. It makes no assumptions about
    verbs or activity ids, and it never fabricates a target.
    """
    rows: list[dict[str, Any]] = []
    for statement in statements:
        actor = statement.get("actor", {}) or {}
        verb = statement.get("verb", {}) or {}
        obj = statement.get("object", {}) or {}
        result = statement.get("result", {}) or {}
        score = result.get("score", {}) or {}
        definition = obj.get("definition", {}) or {}
        context = statement.get("context", {}) or {}
        extensions = context.get("extensions", {}) or {}

        rows.append(
            {
                "id": statement.get("id"),
                "timestamp": statement.get("timestamp"),
                "actor": actor.get("mbox")
                or actor.get("account", {}).get("name")
                or actor.get("name"),
                "verb": verb.get("id"),
                "object": obj.get("id"),
                "object_name": _first_value(definition.get("name")),
                "result_score": score.get("raw", score.get("scaled")),
                "result_success": result.get("success"),
                "result_completion": result.get("completion"),
                "result_response": result.get("response"),
                "language": context.get("language"),
                "extensions": json.dumps(extensions) if extensions else None,
            }
        )
    return rows


def statements_to_csv(statements: list[dict[str, Any]]) -> str:
    """Return the flattened statement table as CSV text."""
    import csv
    import io

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=STATEMENT_COLUMNS)
    writer.writeheader()
    writer.writerows(flatten_statements(statements))
    return buffer.getvalue()


def ingest_csv(client: LrsClient, limit: int | None = None) -> int:
    """Read the source CSV and post statements for each learner row."""
    from .data import load_raw

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


def inspect_statements(statements: list[dict[str, Any]]) -> dict[str, Any]:
    """Report whether statements follow the framework's xAPI profile.

    The profile is the framework's own convention (see the module constants):
    a ``registered`` statement carrying demographics, ``progressed`` statements
    on ``/activities/behaviour/*`` carrying scores, and a ``completed`` statement
    carrying the target. Only statements that use exactly these verbs, activity
    ids and extensions can be ingested without a bespoke adapter.
    """
    from collections import Counter

    verbs: Counter[str] = Counter()
    objects: Counter[str] = Counter()
    actors: set[str] = set()
    has_demographics = False
    has_target = False
    behaviour_objects = 0

    for statement in statements:
        actor = statement.get("actor", {}) or {}
        identifier = actor.get("mbox") or actor.get("name")
        if identifier:
            actors.add(str(identifier))
        verbs[str(statement.get("verb", {}).get("id", ""))] += 1
        obj = str(statement.get("object", {}).get("id", ""))
        objects[obj] += 1
        extensions = (statement.get("context", {}) or {}).get("extensions", {}) or {}
        if DEMOGRAPHICS_EXT in extensions:
            has_demographics = True
        if TARGET_EXT in extensions:
            has_target = True
        if "/behaviour/" in obj:
            behaviour_objects += 1

    missing: list[str] = []
    if not has_demographics:
        missing.append(
            "no registration statement with the demographics extension "
            f"({DEMOGRAPHICS_EXT})"
        )
    if behaviour_objects == 0:
        missing.append(f"no progressed statements on {BASE}/activities/behaviour/*")
    if not has_target:
        missing.append(
            f"no completion statement with the target extension ({TARGET_EXT})"
        )
    if not actors:
        missing.append("no identifiable actors")

    return {
        "statements": len(statements),
        "learners": len(actors),
        "conformant": not missing,
        "missing": missing,
        "verbs": dict(verbs.most_common(20)),
        "sample_objects": [obj for obj, _ in objects.most_common(10)],
    }


def check_file(path: Path | str) -> dict[str, Any]:
    """Inspect a statements file and report profile conformance."""
    report = inspect_statements(read_statements(path))
    report["path"] = str(path)
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="xAPI ingestion utilities.")
    parser.add_argument(
        "command",
        choices=["ingest", "read", "load-db", "check", "flatten"],
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--endpoint", default=None)
    parser.add_argument("--key", default=None)
    parser.add_argument("--secret", default=None)
    parser.add_argument("--url", default=None, help="Database URL for load-db.")
    parser.add_argument(
        "--path", default=None, help="Statements file (JSON/JSONL) for check/flatten."
    )
    parser.add_argument("--out", default=None, help="Output CSV path for flatten.")
    args = parser.parse_args(argv)

    if args.command == "check":
        if not args.path:
            parser.error("check requires --path <statements file>")
        report = check_file(args.path)
        print(json.dumps(report, indent=2))
        if report["conformant"]:
            print("Conformant: this file can be ingested as an xapi-profile source.")
        else:
            print("Not conformant:")
            for reason in report["missing"]:
                print(f"  - {reason}")
            print("A bespoke adapter (and a target) would be needed.")
        return

    if args.command == "flatten":
        if not args.path:
            parser.error("flatten requires --path <statements file>")
        statements = read_statements(args.path)
        csv_text = statements_to_csv(statements)
        if args.out:
            Path(args.out).write_text(csv_text, encoding="utf-8")
            print(f"Wrote {len(statements)} statements -> {args.out}")
        else:
            print(csv_text)
        return

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
