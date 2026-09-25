# 3. Research Methodology

This study adopts the Design Science Research Methodology (DSRM) to guide the
development and evaluation of the Scalable, Evidence-Based XR Integration Framework
(SEB-XRIF). DSRM originates in information systems design research and was formalised by
Peffers et al., and is applied here in five steps. It links each design decision to a
documented problem, as in comparable immersive education work. The problem phase uses the
group systematic literature review of 28 studies, which found retention rarely measured and
a median sample of 30, alongside passive two-dimensional instruction at the Durban
University of Technology.

## 3.1 Proposed Solution

SEB-XRIF is proposed with all choices derived from the SWOT analysis. The method is
immersive virtual reality to address passive instruction. The dataset is the public xAPI
Educational Mining Dataset for reproducibility and scale. The metrics are accuracy and F1
for the model, the System Usability Scale for the dashboard, and Cohen's d for learning
effect. The limitations addressed are small samples, absent retention measurement, and
absent prediction on logged behaviour. The four layers are data, analytics,
visualisation, and evaluation.

The framework pursues four objectives: (1) identify structural barriers to theoretical
knowledge transfer; (2) define a standard XR architecture for longitudinal
multi-institutional use; (3) build a dashboard prototype that visualises engagement and
predicts performance; and (4) assess usability and effectiveness using the System
Usability Scale and Cohen's d.

## 3.2 Data Gathering

The study uses the xAPI Educational Mining Dataset from Kaggle by Amrieh et al. under
Creative Commons Attribution ShareAlike 4.0. The structured table holds 480 Kalboard 360
records collected through Experience API, labelled Low, Medium, or High, with 16
predictors covering demographics, academic context, and behaviour. Counts are 127 Low, 211
Medium, and 142 High. The authors published it preprocessed, a completeness check found no
missing entries.

A public dataset addresses the single-cohort median of 30 and supports reproduction and
extension. The records are primary and secondary school level and therefore prototype the
analytics layer only.

**Scope and transfer.** The bundled dataset is not XR: it is classroom LMS data and the
target is a general academic band. The claim is not that this model predicts XR outcomes,
but that the pipeline is schema-driven: the same analytics run once the feature set is
swapped, because both sources are Experience API statements. To test that, the study also
ingests the public ARETE augmented-reality xAPI pilots and runs the same code on them,
reporting support bands rather than judging the learner. XR outcome validation remains the
DUT pilot.

## 3.3 Design and Development

Design plans four layers with a pipeline from raw data through preprocessing, stratified
split, and Random Forest to predicted support bands. Preprocessing applies one-hot
encoding to categorical variables and retains behavioural counts, as tree models do not
require scaling.

Tool selection follows the literature review theoretical evaluation, which ranked Random
Forest strongest. The ensemble resists noise and overfitting and ranks feature importance,
expected to highlight raised hands and visited resources. Configuration is 100 trees,
balanced weights, and a fixed seed, with stratified 80 percent training and 20 percent
testing. The demonstration dashboard uses FastAPI, React, and the ui design-system chart (Recharts) to show trends, support bands,
and importance, and to switch between the LMS seed and the XR pilots.

## 3.4 Evaluation Criteria

Evaluation uses accuracy, per-class precision, recall, F1, and ten-fold stratified
cross-validation, with expected accuracy of 75 to 83 percent from published benchmarks.
Usability uses the System Usability Scale against 76.6 reported for extended reality
training. Effectiveness uses Cohen's d with thresholds 0.2, 0.5, and 0.8 against 0.936 for
immersive practical training.

Results are compared against these baselines, and a Durban University of Technology pilot
with one-semester follow-up supplies the missing longitudinal retention measure.
