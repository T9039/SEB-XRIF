# 4. Technology Description

This section sells the chosen technologies to a policymaker: what each technology can do,
why it matters for the country, what this study uses it for, and where its limits lie. The
study builds no new headset or engine. It reuses established XR hardware with an analytics
and evaluation framework on standard learning data.

| Technology | Capability, national value, and study use |
| --- | --- |
| Virtual reality simulation | Brings safe practice without real-world consequences. Practical gains exceed 30 percent with engagement near 92 percent. Value is hands-on training at scale, as shown by 5,000 nursing students across 50 universities. The study uses VR as the instructional method for procedural skills, not for abstract theory where it remains weak. |
| Random Forest with language feedback | An ensemble of decision trees that tolerates noisy education data and ranks the behaviours that drive results. Expected accuracy is 75 to 83 percent on the xAPI benchmark, while DistilBERT scores feedback sentiment at 91.7 percent F1. Value is early warning for support, not gatekeeping. The study uses it to predict Low, Medium, or High tiers with explanations. |
| xAPI logging with dashboard | Experience API gives every institution the same standard event record. A FastAPI, React, and Recharts dashboard shows trends, tiers, and importance to instructors. Value is comparability: any adopter reports accuracy with ten-fold validation, usability against 76.6, and learning effect with Cohen's d, plus one-semester follow-up. |

Limits are stated openly. Headset cost and dependence remain, with latency and voice
recognition errors documented. Usability concerns persist across dimensions. The analytics
prototype uses primary and secondary school records and therefore cannot claim higher
education outcomes until the Durban University of Technology pilot with delayed testing is
complete.
