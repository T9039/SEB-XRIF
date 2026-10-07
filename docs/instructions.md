# SEB-XRIF — How to use the framework

This is the operating manual for the SEB-XRIF framework and dashboard. It
explains what the system is for, the data it accepts, what each screen does, the
evaluation it enforces, and the limits you should know before trusting a result.

- New here? Start with **Quickstart** in the [README](../README.md): `make up`.
- Windows? Use `python scripts\run.py` and the README's **Windows setup** section.

---

## 1. What the framework is for

SEB-XRIF is a reusable way of running XR education research, not a single model
or dashboard. It was built to close three gaps found in the literature review:

1. **Small, non-reproducible datasets.** A public dataset and a pinned pipeline
   replace one-off spreadsheets.
2. **No prediction from logged behaviour.** A model turns xAPI behaviour into an
   early, explainable signal for support.
3. **No longitudinal retention measurement.** A fixed T0 / T1 / T2 protocol makes
   retention comparable across institutions.

The framework has four layers — **data, analytics, service, visualization** — plus
an **evaluation** layer. The dashboard is the window onto all of them.

**The honest claim.** The data contract and the evaluation protocol transfer
between sources; **the target does not transfer by itself.** Each source defines
its own features and its own outcome. The bundled Kalboard seed predicts an
academic support band; the ARETE XR pilots predict a derived engagement/drop-off
band. Neither is a claim about XR learning outcomes.

---

## 2. The data it accepts

There are three ways to bring data in.

### 2a. A profile-conformant xAPI statements file (no code)

The framework defines a small xAPI **profile**. A file that follows it is accepted
as-is and can be trained immediately. It uses three statement kinds:

| Purpose | Verb | Carries |
| --- | --- | --- |
| Registration | `http://adlnet.gov/expapi/verbs/registered` | demographics in `context.extensions["http://seb-xrif.dut.ac.za/extensions/demographics"]` |
| Behaviour | `http://adlnet.gov/expapi/verbs/progressed` | one statement per behavioural metric, value in `result.score.raw` |
| Completion | `http://adlnet.gov/expapi/verbs/completed` | the target in `context.extensions["http://seb-xrif.dut.ac.za/extensions/target_class"]` |

The **16 predictors** are 12 categorical columns (gender, NationalITy,
PlaceofBirth, StageID, GradeID, SectionID, Topic, Semester, Relation,
ParentAnsweringSurvey, ParentschoolSatisfaction, StudentAbsenceDays) and 4
behavioural counts (raisedhands, VisITedResources, AnnouncementsView,
Discussion). The target is a class label.

Accepted file formats: `.json` (array) or `.jsonl` (one statement per line).

Check any file before uploading:

```bash
make check-xapi ARGS=path/to/statements.jsonl
```

It reports how many statements and learners it found, the verbs, and whether the
file is conformant — or exactly what is missing. Full detail:
[`docs/xapi_profile.md`](xapi_profile.md).

### 2b. A table adapted with a column mapping (no code)

A plain `.csv` or `.tsv` can be adapted: choose the **target** column and the
**feature** columns, and the delimiter is detected (or set explicitly). The
system suggests a mapping from the file and you can edit it. Adaptation only
**names existing columns** — it never invents a target, and it refuses a file
with no usable target column.

### 2c. A foreign xAPI file, flattened to a table

Valid xAPI that is *not* the framework profile (different verbs, no target) can
be **flattened** to a tidy table, then adapted as in 2b:

```bash
make flatten-xapi ARGS=path/to/foreign.jsonl
```

This reduces every statement to `actor, verb, object, result_*`, `language`,
`extensions` — no assumptions, no fabricated target. You still choose the target.

---

## 3. The dashboard, tab by tab

A persistent header **Data source** selector switches the whole dashboard between
the LMS seed (`Kalboard 360`) and the XR pilots (`ARETE …`); a **light/dark**
toggle is beside it.

| Tab | What it is for |
| --- | --- |
| **Overview** | At-a-glance health: model metrics (accuracy, macro F1, CV macro F1), the support-band distribution, mean behaviour by band, and the longitudinal impact panel (empty until pilot data is imported). |
| **Predict** | Enter a learner's features and get a **support band** with per-class probabilities and a confidence. The form is generated from whichever model is being served, so it adapts to the selected source. |
| **Data** | A paged, sortable, searchable view of the learner records — the LMS table for Kalboard, the per-learner engagement features for an XR pilot. |
| **Diagnostics** | How trustworthy the model is: the full 16-model comparison matrix (accuracy, macro F1, CV macro F1 with 95% CI, ROC-AUC), the confusion matrix and per-class metrics, cross-validation spread, calibration (ROC, PR, calibration curve, expected calibration error), learning curves, and feature importance (native + SHAP). |
| **Explore** | XR and structure: engagement over time for the selected pilot, the XR early-warning risk bands, the LMS→XR feature mapping, correlation matrix, box plots, a PCA embedding and cluster profiles, and partial dependence. |
| **Studio** | Build charts ad hoc: pick a source, metric, and chart type, then export or save the view. |
| **Datasets** | Register new data: **Check** a file, adapt a table with a column mapping, **Flatten to CSV** a foreign xAPI file, and **Train** the resulting source (one model, or the best of the full matrix). Lists every source and whether a model exists. |

---

## 4. The evaluation the framework enforces

Every adopter reports the **same** instruments, so results are comparable.

**Model performance** — accuracy, macro F1, per-class precision/recall/F1,
stratified cross-validation (default 10 folds) with the mean, standard deviation
and a **95% confidence interval**; one-vs-rest ROC-AUC; and **calibration**
(reliability curve, Brier score, and expected calibration error). The published
benchmark for the seed dataset is **0.75–0.83** accuracy.

**Usability** — the **System Usability Scale**, scored 0–100, compared against
**76.6** (the XR-training reference).

**Effect size** — **Cohen's d** with thresholds **0.2 / 0.5 / 0.8**
(small/medium/large), compared against **0.936** for immersive practical
training.

**Longitudinal protocol** — three time points, not two:

- **T0** — baseline test and survey before the module
- **T1** — immediately after the module (learning gain and SUS)
- **T2** — one semester later, no re-teaching (retention)

Effect sizes reported: `d_immediate` (T1 vs T0), `d_delayed` (T2 vs T0), and
`decay` (T2 vs T1) with a retention ratio.

Build and store a report:

```bash
make eval-report ARGS='--input pilot.json --store --source pilot'
```

Example inputs live at `eval/pilot.example.json`. The example is tagged
`source=example` and is **never** presented as a result.

**Support bands.** The model's classes are reported as actionable bands, not
judgements: **priority-support** (L), **monitor** (M), **on-track** (H). A
cost-sensitive rule can flag the priority band at a probability below the argmax
(`decision_thresholds: {L: 0.35}`), trading some precision for recall on the band
that matters for early support.

---

## 5. Step by step: running the framework

1. **Bring it up.**
   ```bash
   make up            # installs if needed, trains if needed, runs api + dashboard
   ```
   Dashboard: http://localhost:5173 · API docs: http://localhost:8000/docs.
2. **Look at the seed.** Overview, Data, Diagnostics — the built-in Kalboard data
   and its model.
3. **Add XR context.** Download the ARETE pilots and switch the header source:
   ```bash
   make fetch-arete
   ```
   Explore shows the engagement trends and the early-warning risk for each pilot.
4. **Register your own data.** In **Datasets**: check a file, adapt a table (or
   flatten a foreign xAPI file), then train it. Train one model, or run the matrix
   and let the system promote the best model for that data:
   ```bash
   make train SOURCE=<name>                  # one model
   make train SOURCE=<name> ARGS='--matrix'  # best of matrix
   ```
5. **Use the model.** Switch the header source to your dataset and use **Predict**
   and **Diagnostics**; the served model is the one trained for that source.
6. **Run the evaluation protocol.** Collect T0/T1/T2 and SUS for your cohort,
   then `make eval-report` and view the **Overview → Longitudinal impact** panel.
7. **Report.** Every adopter reports the same metrics, so results accumulate.

Optional: `make matrix` (full comparison matrix with reports), `make storybook`
(component library), `make repro-check` (verify a clean checkout reproduces).

---

## 6. Limits — what it cannot do

Read these before drawing conclusions.

- **The bundled seed is not XR.** Kalboard 360 is K-12 LMS data. It prototypes the
  pipeline; XR-specific learning outcomes are not claimed from it.
- **The target must be defined by a human.** If a source carries no outcome, the
  system will not invent one. It refuses to train rather than fabricate a label.
  ARETE's target (drop-off vs retained) is a **derived** engagement signal, not an
  academic or XR-learning score.
- **The profile is the framework's own.** "Profile-conformant" means the source
  emits the framework's verbs and extensions. Arbitrary xAPI is not conformant;
  it needs the flatten path (features only) or a small adapter.
- **The statements path has fixed features.** A conformant statements file can
  change the target name and labels, but **not** the 16 feature columns. For a
  different feature set, use the table/mapping path.
- **Small cohorts are reported with their uncertainty, not hidden.** A dataset
  too small to cross-validate (fewer than two members in a class) is refused; a
  single-outcome cohort is reported as "not modelled" rather than scored.
- **It is a prototype, and an unfrozen one.** The schema, split, and metrics are
  pinned for reproducibility, but the software is being tested by beta users and
  will change.
- **Uploads are data only.** No code is executed; files are size- and type-limited
  and validated against the profile before they are stored.
- **One machine, local storage.** This is a single-user development build; data
  lives in `data/raw/uploads/` and models in `models/`.

---

## 7. Reporting an issue (beta testers)

Please include: what you did, what you expected, what happened, and any browser
console errors (F12 → Console), plus your operating system. If the dashboard or
API shows an error message, copy it verbatim — they are written to be actionable.
