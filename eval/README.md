# Evaluation layer

The evaluation layer is fixed by the framework: every adopter reports the same
measures so results are comparable across institutions.

| Module | Responsibility |
| --- | --- |
| `sus.py` | System Usability Scale scoring (ten items, 0-100) |
| `effect_size.py` | Cohen's d with a pingouin path and a scipy/NumPy fallback |
| `longitudinal/protocol.py` | T0/T1/T2 summaries and effect sizes |

## Protocol

Three time points, not two:

- **T0** — baseline test and survey before the XR module
- **T1** — immediately after the module; learning gain and SUS
- **T2** — one semester later, no re-teaching; retention

Reported effect sizes:

- `d_immediate = T1 vs T0` — did they learn?
- `d_delayed = T2 vs T0` — did it stick?
- `decay = T2 vs T1` — how much was forgotten?

Reference benchmarks: SUS 76.6 (Kim et al., 2024); Cohen's d 0.936 (Chang and
Hsu, 2023); thresholds 0.2 / 0.5 / 0.8.

## Example

```python
from eval.sus import sus_score
from eval.effect_size import cohens_d
from eval.longitudinal import summarise

sus_score([5, 1, 5, 1, 5, 1, 5, 1, 5, 1])  # 100.0
cohens_d(t1_scores, t0_scores, paired=True)  # immediate effect
summarise(t0=[1, 2, 3], t1=[5, 6, 7], t2=[3, 4, 5])
```

## License note

`pingouin` is GPL-3.0. `effect_size.py` implements the same calculations on
scipy/NumPy so the framework can be redistributed without the copyleft
dependency.
