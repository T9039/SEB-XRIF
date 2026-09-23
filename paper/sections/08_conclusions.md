# 8. Conclusions

This work set out to address three recurring weaknesses in the XR education
literature — small and non-reproducible datasets, an absence of prediction from
logged behaviour, and a lack of longitudinal retention measurement — and
produced the Scalable, Evidence-Based XR Integration Framework to do so.

The framework is delivered as a working system. Its data layer accepts standard
Experience API statements through a Learning Record Store and stores validated
learner records in a relational database; its analytics layer trains and compares
sixteen models and promotes an explainable Random Forest; its service layer
exposes prediction and analytics endpoints; and its visualization layer presents
a side-panel dashboard for prediction, data exploration, and diagnostics. Every
component is covered by tests, and the whole system reproduces from a clean
checkout through versioned data, fixed seeds, and tracked runs.

The comparison matrix shows strong, competitive performance that meets the
published benchmark for the dataset, and the interpretability analysis surfaces
attendance and resource engagement as the most stable drivers of learner
outcomes. The evaluation protocol fixes usability against the System Usability
Scale and learning against Cohen's d, over a baseline, immediate, and delayed
timeline.

**Further work.** The immediate next step is the Durban University of Technology
pilot: run the module with students, report the immediate (T0/T1) results now,
and complete the delayed (T2) measurement one semester later, which upgrades the
claim from immediate learning to measured retention. Beyond that, the framework
should be exercised on a second, higher-education dataset to test transfer, and
the learning-record path extended to live XR sessions. The single supervised
model should also be extended to ensemble and sequence models as data volume
grows.

**Recommendations.** Adopters should commit to the fixed evaluation protocol
before running a module, keep learning data in the xAPI schema rather than in
bespoke spreadsheets, and report effect sizes with confidence intervals so that
small cohorts are interpreted honestly. Used this way, SEB-XRIF turns individual
XR pilots into an accumulating, comparable evidence base.
