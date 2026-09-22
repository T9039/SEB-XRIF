// SEB-XRIF — Enhancing Digital Education Using VR Technology (Team 3)
//
// The paper's prose lives as Markdown in paper/sections/*.md (source of truth)
// and is rendered here with the `cmarker` package. Build with:
//
//   ./paper/build.sh          (or: make paper)
//
// `build.sh` refreshes paper/sections/results_table.md and paper/assets/ from
// reports/ so the paper's numbers always match the model matrix.
#import "@preview/cmarker:0.1.10" as cmarker

#set page(
  paper: "a4",
  margin: (x: 1.9cm, y: 2.0cm),
  numbering: "1",
)
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true, leading: 0.72em)
#show heading.where(level: 1): set text(size: 14pt, weight: "bold")
#show heading.where(level: 2): set text(size: 12pt, weight: "bold")
#show heading.where(level: 3): set text(size: 11pt, weight: "bold", style: "italic")
#show heading: set block(above: 0.9em, below: 0.4em)
#show raw.where(block: true): set block(fill: luma(247), inset: 8pt, radius: 3pt, width: 100%)

#let md(path) = cmarker.render(read(path))

#align(center)[
  #text(size: 16pt, weight: "bold")[Enhancing Digital Education Using VR Technology]
  #v(0.5em)
  #text(size: 9pt)[Team 3 — PRJT302 — Information Technology, Durban University of Technology]
]
#v(0.3em)
#line(length: 100%, stroke: 0.5pt + luma(180))

#md("sections/00_abstract.md")
#md("sections/01_introduction.md")
#md("sections/02_literature_review.md")
#md("sections/03_methodology.md")
#md("sections/04_technology_description.md")
#md("sections/05_developments.md")
#md("sections/06_results.md")
#md("sections/results_table.md")

#figure(
  image("../reports/figures/model_comparison.png", width: 92%),
  caption: [Model comparison matrix across the 16 estimators (CV macro F1 ± std).],
)

#md("sections/07_business_benefits.md")
#md("sections/08_conclusions.md")
#md("sections/09_acknowledgements.md")
#md("sections/references.md")
