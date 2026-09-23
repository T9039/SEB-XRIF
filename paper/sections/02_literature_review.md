# 2. Literature Review

The group systematic literature review covers 28 peer-reviewed studies from 2023 to 2026,
selected under PRISMA 2020. It answers four questions on methods, data, metrics, and
limitations. This section condenses it for the full paper: existing approaches,
theoretical evaluation with metrics and synthesis, evaluation of intelligent models, and
technical considerations that motivate SEB-XRIF.

## 2.1 Existing Approaches

Virtual Reality dominates the evidence base with 16 of 28 studies, followed by Mixed
Reality with 4 and Augmented Reality with 3. VR pairs with established instructional
models, including a hybrid ADDIE and Borg and Gall design in the Preinanku language game
and User-Centred Design with Problem-Based Learning in moot court simulations. AR supports
handwashing training for children with autism spectrum disorder, while MR provides layered
3D pathology models for spatial reasoning.

Scale varies from 5,000 nursing students across 50 universities to controlled cohorts of
5, with a median of 30. Effectiveness concentrates on practical skills with gains above
30 percent and engagement near 92 percent, while theoretical transfer remains weak. Small
samples and technical faults such as rendering latency in AI interview systems recur
across the set.

## 2.2 Theoretical Evaluation and Synthesis

Evaluation follows a triad of learning outcomes at 85 percent, engagement at 77 percent,
and usability at 58 percent. Representative instruments include effect sizes such as
Cohen's d of 0.936 and sentiment F1 of 91.7 percent from DistilBERT.

Synthesis selects VR simulation as the primary method because it carries the practical
skill gains, with AR and MR retained as complements for overlays and spatial models.
Microteaching specificity scores and museum usability dimensions show that measurement is
maturing, but the absence of longitudinal retention data leaves the central contradiction
unresolved: strong immediate gains against unknown durability.

## 2.3 Theoretical Evaluation of Intelligent Models

Only two reviewed studies apply intelligent models to learner data. DistilBERT reaches an
F1 score of 91.7 percent on feedback sentiment, and regression on intent to use reaches R
squared of 0.883.

The review provides no comparison of Random Forest, Support Vector Machine, or K-Nearest
Neighbours, so these are not presented as SLR findings. Random Forest is selected
prospectively for SEB-XRIF on external ensemble benchmarks for the xAPI dataset and its
robustness to noisy educational data with ranked feature importance. Voice-driven dialogue
remains fragile across accents and dialects, and abstract visualisation learning shows the
same boundary between demonstration and evidence.

## 2.4 Technical Considerations

Delivery depends on headsets such as Oculus Quest, HTC Vive, and HoloLens 2, built with
Unity and Blender content and speech-to-text or conversational AI. Evidence comes from
questionnaires, feedback transcripts, and performance assessments.

The SLR does not consistently report programming languages, databases, or development
environments, so these are not assumed. The specified foundation is therefore XR
environments with 3D content, AI language technologies for feedback, and logged
performance data, which Section 3 implements as FastAPI, React, and Recharts over the xAPI
schema.
