# Documentation

| Path | Description |
| --- | --- |
| `SEB-XRIF_Technical_Specification.typ` | Typst source for the specification |
| `SEB-XRIF_Technical_Specification.pdf` | Compiled specification (14 pages) |
| `figures/` | Generated figure assets (PNG + PDF) |
| `figures/src/` | Figure generation scripts |
| `paper/` | Paper-build tooling (`build_section3_docx.py`) |

## Rebuild the specification

```bash
typst compile docs/SEB-XRIF_Technical_Specification.typ
```

## Regenerate the figures

```bash
make figures
```

The figure scripts read the dataset from `data/raw/` and write into
`docs/figures/`.
