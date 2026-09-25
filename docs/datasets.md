# Datasets

SEB-XRIF is schema-driven: the analytics layer is demonstrated on one dataset
and transfers to another by swapping the feature set. Two sources are
supported: the bundled non-XR seed and real XR (AR) pilots.

## Bundled seed: xAPI Educational Mining Dataset (Kalboard 360)

- **File:** `data/raw/xAPI-Edu-Data.csv` (committed)
- **Licence:** CC BY-SA 4.0
- **Shape:** 480 records, 16 predictors + a Low/Medium/High `Class`
- **Nature:** primary/secondary school LMS data. It is **not XR** and the
  target is an academic band, not an XR outcome.

It prototypes the analytics layer and lets the full pipeline run offline.

## XR pilots: ARETE (augmented reality in education)

Real xAPI statements from four AR-education pilots, published as Learning
Locker CSV exports.

- **Licence:** CC BY 4.0
- **Paper:** *Dataset of user interactions across four large pilots on the use
  of augmented reality in learning experiences*, Scientific Data (2023),
  DOI [10.1038/s41597-023-02743-6](https://doi.org/10.1038/s41597-023-02743-6)
- **Repository:** Zenodo community [`augmented`](https://zenodo.org/communities/augmented)

| Pilot | Zenodo record | Topics |
| --- | --- | --- |
| `pbis` | [7876959](https://zenodo.org/records/7876959) | Positive Behaviour Intervention and Support, nine AR behavioural lessons |

The remaining pilots (English Literacy, STEM Geometry, STEM Geography, LXD) are
added by the "all pilots" work.

### Fetching

The files are downloaded rather than committed, and verified against a pinned
SHA-256 (recorded in `analytics/xr.py`) so a changed upstream file is rejected.

```bash
make fetch-arete            # all known pilots
make fetch-arete ARGS=pbis  # one pilot
```

They land in `data/raw/arete/` (git-ignored). A small sample is committed under
`tests/fixtures/arete/` so tests run offline.

### Statement schema

Each CSV row is one xAPI statement, flattened by Learning Locker:

`timestamp;lrs_id;actor name;verb_id;verb_display;object id;object name;result_response;result_raw`

The adapter parses `timestamp`, `actor name` (learner), `verb_display` (verb),
`object name` (activity) and `result_raw` (numeric response), then derives one
engagement row per learner (events, active days, distinct verbs/objects,
per-verb counts, responses, span, events per active day).

## LMS feature to XR analogue

The transfer claim is concrete: the same analytics applies to XR behaviour if
the feature set is mapped.

| Kalboard (LMS) | XR analogue | ARETE verb(s) |
| --- | --- | --- |
| `raisedhands` | in-VR help requests | `responded`, `selected` |
| `VisITedResources` | VR/AR content interactions | `accessed`, `found` |
| `AnnouncementsView` | task briefings read | `read` |
| `Discussion` | collaborative VR activity | `joined` |
| `StudentAbsenceDays` | VR session attendance / drop-off | `started` vs `left` |
