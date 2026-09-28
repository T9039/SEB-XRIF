# The SEB-XRIF xAPI profile

xAPI (the standard) fixes the *shape* of a statement — `actor`, `verb`,
`object`, and optional `result`/`context`/`timestamp` — but not which verbs,
activity ids, or extensions you use. A **profile** is the convention that fills
that in. SEB-XRIF ships its own, defined in `analytics/xapi.py`:

```
BASE             = http://seb-xrif.dut.ac.za
DEMOGRAPHICS_EXT = http://seb-xrif.dut.ac.za/extensions/demographics
TARGET_EXT       = http://seb-xrif.dut.ac.za/extensions/target_class
VERB_REGISTERED  = http://adlnet.gov/expapi/verbs/registered
VERB_PROGRESSED  = http://adlnet.gov/expapi/verbs/progressed
VERB_COMPLETED   = http://adlnet.gov/expapi/verbs/completed
```

## What a conformant learner looks like

Three statement kinds, using exactly these verbs, activity ids, and extensions:

1. **Registration** — verb `registered`, object
   `…/activities/course/{Topic}`, all demographic columns in
   `context.extensions[DEMOGRAPHICS_EXT]`.
2. **Behaviour** — one `progressed` statement per behavioural metric, object
   `…/activities/behaviour/{raisedhands|VisITedResources|AnnouncementsView|Discussion}`,
   numeric value in `result.score.raw`.
3. **Completion** — verb `completed`, target in
   `context.extensions[TARGET_EXT]`.

```json
{"actor": {"mbox": "mailto:l0000@dut4life.ac.za", "name": "L0000"},
 "verb": {"id": "http://adlnet.gov/expapi/verbs/registered"},
 "object": {"id": "http://seb-xrif.dut.ac.za/activities/course/IT"},
 "context": {"extensions": {"http://seb-xrif.dut.ac.za/extensions/demographics":
   {"gender": "M", "Topic": "IT", "...": "..."}}}}

{"actor": {"mbox": "mailto:l0000@dut4life.ac.za"},
 "verb": {"id": "http://adlnet.gov/expapi/verbs/progressed"},
 "object": {"id": "http://seb-xrif.dut.ac.za/activities/behaviour/raisedhands"},
 "result": {"score": {"raw": 15}}}

{"actor": {"mbox": "mailto:l0000@dut4life.ac.za"},
 "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
 "object": {"id": "http://seb-xrif.dut.ac.za/activities/course/IT"},
 "context": {"extensions": {"http://seb-xrif.dut.ac.za/extensions/target_class": "H"}}}
```

A source that emits this shape needs **no new code** — the generic
`xapi-profile` adapter reconstructs features and target. A source that does not
(such as the ARETE pilots, which use different verbs and carry no target) needs
a bespoke adapter and a human-defined target.

## Is a dataset I downloaded conformant?

Run the checker on a statements file (JSON array or JSON Lines):

```bash
make check-xapi ARGS=path/to/statements.jsonl
# or
uv run python -m analytics.xapi check --path path/to/statements.jsonl
```

It prints the statement and learner counts, the verbs and object ids it saw, and
whether the file is conformant — or exactly what is missing:

```json
{
  "statements": 12390,
  "learners": 81,
  "conformant": false,
  "missing": [
    "no registration statement with the demographics extension (…)",
    "no completion statement with the target extension (…)"
  ],
  "verbs": {"http://adlnet.gov/expapi/verbs/selected": 3791, "...": 0},
  "sample_objects": ["http://activitystrea.ms/schema/1.0/task", "..."]
}
```

**Almost every dataset found online will be non-conformant**, because the
profile uses the framework's own IRIs. Non-conformance is not a dead end; it
just means one of:

- **Adapt the data** into the profile (write a small converter), then upload and
  train with no code; or
- **Write a bespoke adapter** (`analytics/datasets/`) that reads the source and
  declares its features and target; or
- **Extend the profile** if a whole class of sources shares a new feature set.

The one thing that cannot be manufactured is a **target**: if the source carries
no outcome, a human has to define one (as with ARETE's derived drop-off band).

## Bridging a non-conformant statements file

A foreign statements file (valid xAPI, different vocabulary) can still be used
without writing an adapter: **flatten it to a tidy table**, then adapt it with a
column mapping.

```bash
uv run python -m analytics.xapi flatten --path foreign.jsonl --out foreign.csv
make flatten-xapi ARGS=foreign.jsonl   # writes foreign.csv alongside it
```

Or, in the dashboard's **Datasets** tab, choose the file and press
**"Flatten to CSV"** (it downloads), then re-upload that CSV as a table and pick
the target/features in the mapping. The API endpoint is `POST /datasets/flatten`.

Flattening makes no assumptions about verbs or activity ids and fabricates no
target — it reduces every statement to
`id, timestamp, actor, verb, object, object_name, result_*` (score, success,
completion, response), `language` and `extensions`. You then choose which of
those columns are features, and define the target (by mapping a column, or, if
there is genuinely no outcome, by deriving one as ARETE does).
