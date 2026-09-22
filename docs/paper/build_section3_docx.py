"""Build 'team 3 (final).docx': Section 3 (Research Methodology and
Proposed Solution) plus the full-paper Literature Review draft,
for mentor review.

Methodology revised per the lecturer's recording instructions
(Manqele transcription). Literature Review follows the lecturer's
WhatsApp full-paper instructions: 2.1 existing approaches with SLR
graph, 2.2 theoretical evaluation with metrics table and synthesis
together, 2.3 theoretical evaluation of intelligent models with top
candidates, 2.4 technical considerations, sandwich rule throughout
(paragraph, figure or table, discussion). Technology Description
follows the transcription: policymaker level pitch of capabilities,
national value, study use, and loopholes, in table form.

Style: Times New Roman, justified body text, numbered headings,
captioned figures and tables, IEEE-numbered references. All facts
verified against the xAPI-Edu-Data.csv download and the SLR.
"""

import csv
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(BASE))
FIG_DIR = os.path.join(REPO, "docs", "figures")
DATA_FILE = os.path.join(REPO, "data", "raw", "xAPI-Edu-Data.csv")
OUT = os.path.join(BASE, "team 3 (final).docx")

# ---------------------------------------------------------------- references
# Group reference list ([1]-[35] supplied by the group, [36]-[37]
# appended for the dataset and PRISMA). Italic segments are wrapped
# in *...*.
REFERENCES = [
    "J. A. Cahya and S. Hartono, \"Development of Preinanku' VR game "
    'for Javanese language learning using the ADDIE model," *J. Educ. '
    "Technol. Innov.*, vol. 12, no. 1, pp. 45-56, Jan. 2025.",
    'P. Mongkoljaturong, A. Smith, and B. Jones, "Evaluation of '
    'speech-to-text processing speed in AI-driven mock interviews," '
    "*in Proc. Int. Conf. Adv. Learn. Technol. (ICALT)*, 2025, "
    "pp. 112-119.",
    'D. Ai, Y. Chen, and X. Zhang, "Virtual reality integration in '
    "higher education: Evaluation of learner retention and "
    'generalizability," *Comput. and Educ.*, vol. 208, p. 104920, '
    "Mar. 2024.",
    'M. Gie\u00dfer, K. Weber, and H. M\u00fcller, "Immersive VR training in '
    "medical education: A comparative study on practical skill "
    'acquisition," *BMC Med. Educ.*, vol. 24, no. 1, Art. no. 88, '
    "Feb. 2024.",
    'A. Al-Sudani, M. K. Hassan, and S. R. Ali, "BodySwaps simulation '
    "using BERT/DistilBERT sentiment analysis for communication "
    'training," *IEEE Trans. Learn. Technol.*, vol. 18, pp. 215-226, '
    "2025.",
    'Y.-C. Chu, C.-C. Lin, K.-L. Fu, and H.-R. Chen, "Interactive '
    'augmented reality in STEM learning environments," *Comput. Hum. '
    "Behav.*, vol. 150, Art. no. 107980, Jan. 2024.",
    'S. Leonori, M. Paschero, and A. Rizzi, "Virtual laboratories for '
    'engineering education: A systematic review," *IEEE Rev. Biomed. '
    "Eng.*, vol. 17, pp. 101-114, 2024.",
    'J. Zhang, "Multi-institutional scale evaluation of VR nursing '
    'procedural training across Chinese universities," *Int. J. Nurs. '
    "Stud.*, vol. 142, Art. no. 104480, June 2023.",
    "E. R. Smith, R. Koldenhoven, J. W. Farrell III, S. Aslan, "
    'M. D. Resendiz, Y. Li, T. Liu, and D. Valles, "AR handwashing '
    'training for children with ASD using HoloLens 2," *IEEE Trans. '
    "Vis. Comput. Graph.*, vol. 30, no. 5, pp. 2410-2420, May 2024.",
    'R. Toledano, C. Giordano, E. Pozzebon, and J. Manzon, "3D '
    "pathology models developed with Unity and Blender for medical "
    'education," *Anat. Sci. Educ.*, vol. 18, no. 2, pp. 189-201, '
    "Feb. 2025.",
    "S. Litchaweerat, P. Khenda, W. Intayoad, Y. Tongpaeng, and "
    'P. Putjorn, "Interactive science and technology VR laboratory '
    'simulations," *J. Sci. Educ. Technol.*, vol. 33, no. 3, '
    "pp. 310-322, June 2024.",
    'P. Ordu\u00f1a, P. Amarante, and L. Rodriguez-Gil, "Remote hands-on '
    'hardware labs for digital engineering education," *IEEE Trans. '
    "Educ.*, vol. 66, no. 4, pp. 380-389, Aug. 2023.",
    "M. F. Rahman, J. Akbardin, A. Y. Permana, K. Wijaya, I. Susanti, "
    'and S. Handayani, "Spatial learning and architectural '
    'visualization using extended reality," *Educ. Inf. Technol.*, '
    "vol. 29, no. 2, pp. 1845-1862, Feb. 2024.",
    "L. D'Souza, R. Kumar, and S. Nair, \"Evaluating multi-user "
    'immersive virtual reality for collaborative problem-solving," '
    "*Comput. and Educ. XR*, vol. 3, Art. no. 100045, 2025.",
    'L. J. Jacobsen, M. Nielsen, and K. Hansen, "Evaluating '
    'pre-service teachers via VR microteaching feedback transcripts," '
    "*Teach. Teach. Educ.*, vol. 138, Art. no. 104412, Feb. 2026.",
    'X. Huang, Y. Wang, and Z. Liu, "Usability evaluation of virtual '
    'museum exhibits using SUS and UEQ metrics," *Int. J. '
    "Hum.-Comput. Stud.*, vol. 193, Art. no. 103210, Jan. 2025.",
    'S. Sunardi, A. Abdullah, and A. Setiawan, "Hybrid assessment '
    'frameworks for extended reality in vocational learning," *J. '
    "Vocat. Educ. Train.*, vol. 77, no. 1, pp. 88-105, 2025.",
    'S. S. Marandi and F. S. Kashanifar, "Addressing sample size '
    'constraints in educational technology interventions," *Educ. Res. '
    "Rev.*, vol. 42, Art. no. 100580, Nov. 2024.",
    "W. D. W. Gonzales, S. P. Geng, D. S. Jiandong, and A. "
    'Nurgissayeva, "Comparative analysis of user engagement in '
    'concrete vs. abstract XR simulations," *Interact. Learn. '
    "Environ.*, vol. 33, no. 1, pp. 115-129, 2025.",
    'A. Vaze, A. Morris, and I. Clarke, "Impact of speech recognition '
    'errors and dialect variability in conversational VR," *Speech '
    "Commun.*, vol. 158, Art. no. 103020, Mar. 2024.",
    'T. L. Nieto and D. L. Gonz\u00e1lez-Ba\u00f1ales, "Pedagogical frameworks '
    'for integrating mixed reality in higher education," *Innov. Educ. '
    "Teach. Int.*, vol. 61, no. 4, pp. 512-526, 2024.",
    'R.-C. Chang and H.-C. Hsu, "Measuring practical exam performance '
    'gains in VR-based vocational training," *Comput. and Educ.*, '
    "vol. 198, Art. no. 104760, June 2023.",
    'S. Dickinson and M. K. McIntosh, "Experiential learning and '
    'risk-free mistake management in virtual simulation," *Med. '
    "Teach.*, vol. 47, no. 3, pp. 340-351, 2025.",
    "J.-H. Wang, M. Liyanawatta, C.-Y. Lee, Y.-L. Huang, S.-H. Yang, "
    'and G.-D. Chen, "Embodied learning dynamics in 3D interactive '
    'environments," *IEEE Access*, vol. 11, pp. 88200-88212, 2023.',
    'Y. Xing, Y. Xiao, X. Wang, Y. Liang, and G. Feng, "VR moot court '
    'simulations for law students combining UCD and PBL," *Comput. '
    "and Educ.*, vol. 210, Art. no. 104950, Feb. 2025.",
    'L. Patra, M. Kumari, and R. Gopalapillai, "Synthesizing empirical '
    'evidence in immersive educational technology," *Rev. Educ. Res.*, '
    "vol. 94, no. 2, pp. 210-235, Apr. 2024.",
    'L. Xia, X. Li, Y. Qin, D. Li, and L. Fan, "Scalable spatial '
    'computing frameworks for institutional hybrid learning," *Comput. '
    "Graph.*, vol. 118, Art. no. 103850, Feb. 2024.",
    "J. Kim, K. Wang, M. Dorneich, E. Winer, L. Brown, and "
    'G. Whitehurst, "Long-term evaluation of immersive VR training '
    'retention," *Int. J. Hum.-Comput. Interact.*, vol. 40, no. 8, '
    "pp. 1950-1965, 2024.",
    'A. R. Hevner, S. T. March, J. Park, and S. Ram, "Design science '
    'in information systems research," *MIS Quarterly*, vol. 28, '
    "no. 1, pp. 75-105, 2004.",
    "K. Peffers, T. Tuunanen, M. A. Rothenberger, and S. Chatterjee, "
    '"A design science research methodology for information systems '
    'research," *Journal of Management Information Systems*, vol. 24, '
    "no. 3, pp. 45-77, 2007.",
    'E. Abu Amrieh, T. Hamtini, and I. Aljarah, "Preprocessing and '
    "analyzing educational data set using X-API for improving student's "
    'performance," *in Proc. Int. Conf. Appl. Electr. Eng. Comput. '
    "Technol. (AEECT)*, Amman, Jordan, 2015.",
    'L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5-32, 2001.',
    'E. Abu Amrieh, T. Hamtini, and I. Aljarah, "Mining educational '
    "data to predict student's academic performance using ensemble "
    'methods," *International Journal of Database Theory and '
    "Application*, vol. 9, no. 8, pp. 119-136, 2016.",
    "J. Brooke, \"SUS: A 'quick and dirty' usability scale,\" in "
    "*Usability Evaluation in Industry*, P. W. Jordan, B. Thomas, "
    "B. A. Weerdmeester, and I. L. McClelland, Eds. London, U.K.: "
    "Taylor and Francis, 1996, pp. 189-194.",
    "J. Cohen, *Statistical Power Analysis for the Behavioral "
    "Sciences*, 2nd ed. Hillsdale, NJ, USA: Lawrence Erlbaum "
    "Associates, 1988.",
    "E. Abu Amrieh, T. Hamtini, and I. Aljarah, \"Students' academic "
    'performance dataset (xAPI-Edu-Data)," *Kaggle*, 2016. [Online]. '
    "Available: https://www.kaggle.com/datasets/aljarah/xAPI-Edu-Data",
    'M. J. Page et al., "The PRISMA 2020 statement: An updated '
    'guideline for reporting systematic reviews," *BMJ*, vol. 372, '
    "Art. no. n71, 2021.",
]

# ---------------------------------------------------------------- body text
INTRO = [
    "This study adopts the Design Science Research Methodology (DSRM) to "
    "guide the development and evaluation of the Scalable, Evidence-Based "
    "XR Integration Framework (SEB-XRIF). DSRM originates in information "
    "systems design research [29] and was formalized by "
    "Peffers et al. [30] and is applied here in five steps. It links each design decision to a documented "
    "problem, as in comparable immersive education work [17]. The problem "
    "phase uses the group systematic literature review of 28 studies, "
    "which found retention rarely measured [3], [27] and a median sample "
    "of 30, alongside passive two-dimensional instruction at the Durban "
    "University of Technology. Fig. 1 shows the five steps.",
]

PROPOSED = [
    "SEB-XRIF is proposed with all choices derived from the SWOT "
    "analysis. The method is immersive virtual reality to address "
    "passive instruction. The dataset is the public xAPI Educational "
    "Mining Dataset [31], [36] for reproducibility and scale. The metrics "
    "are accuracy and F1 for the model, System Usability Scale for the "
    "dashboard, and Cohen d for learning effect. The limitations "
    "addressed are small samples, absent retention measurement, and "
    "absent prediction on logged behavior [5], [19]. The four layers are "
    "data, analytics, visualization, and evaluation.",
]

OBJECTIVES = [
    "Identify structural barriers to theoretical knowledge transfer.",
    "Define a standard XR architecture for longitudinal multi-institutional use.",
    "Build a dashboard prototype that visualizes engagement and predicts performance.",
    "Assess usability and effectiveness using System Usability Scale and Cohen d.",
]

DATA_GATHERING = [
    "The study uses the xAPI Educational Mining Dataset from Kaggle [36] "
    "by Amrieh et al. [31] under Creative Commons Attribution ShareAlike "
    "4.0. The structured table holds 480 Kalboard 360 records collected "
    "through Experience API, labeled Low, Medium, or High, with 16 "
    "predictors covering demographics, academic context, and behavior. "
    "Counts are 127 Low, 211 Medium, and 142 High. The authors published "
    "it preprocessed, a completeness check found no missing entries, "
    "and Table 1 samples the records.",
    "A public dataset addresses the single-cohort median of 30 and "
    "supports reproduction and extension. The records are primary and "
    "secondary school level and therefore prototype the analytics layer "
    "only.",
]

DESIGN = [
    "Design plans four layers with a pipeline from raw data through "
    "preprocessing, stratified split, and Random Forest to predicted "
    "tiers, as Fig. 2 shows. Preprocessing applies one-hot encoding to "
    "categorical variables and retains behavioral counts, as tree models "
    "do not require scaling.",
    "Tool selection follows the literature review theoretical evaluation, "
    "which ranked Random Forest strongest [32]. The ensemble resists "
    "noise and overfitting and ranks feature importance, expected to "
    "highlight raised hands and visited resources [33]. Configuration is "
    "100 trees, balanced weights, and fixed seed, with stratified 80 "
    "percent training and 20 percent testing. The demonstration "
    "dashboard uses Flask, React, and Chart.js to show trends, tiers, "
    "and importance.",
]

EVALUATION = [
    "Evaluation uses accuracy, per-class precision, recall, F1, and "
    "ten-fold stratified cross-validation, with expected accuracy of 75 "
    "to 83 percent from published benchmarks [33]. Usability uses "
    "System Usability Scale [34] against 76.6 reported for extended "
    "reality training [28]. Effectiveness uses Cohen d [35] with "
    "thresholds 0.2, 0.5, and 0.8 against 0.936 for immersive practical "
    "training [22].",
    "Results are compared against these baselines, and a Durban "
    "University of Technology pilot with one-semester follow-up supplies "
    "the missing longitudinal retention measure.",
]

# ------------------------------------------------- literature review
LIT_INTRO = [
    "The group systematic literature review covers 28 peer reviewed "
    "studies from 2023 to 2026, selected under PRISMA 2020 [37]. It "
    "answers four questions on methods, data, metrics, and limitations. "
    "This section condenses it for the full paper: existing approaches, "
    "theoretical evaluation with metrics and synthesis, evaluation of "
    "intelligent models, and technical considerations that motivate "
    "SEB-XRIF.",
]

LIT_21A = [
    "Virtual Reality dominates the evidence base with 16 of 28 studies, "
    "followed by Mixed Reality with 4 and Augmented Reality with 3, as "
    "Fig. 3 shows. VR pairs with established instructional models, "
    "including a hybrid ADDIE and Borg and Gall design in the Preinanku "
    "language game [1] and User-Centred Design with Problem-Based "
    "Learning in moot court simulations [25]. AR supports handwashing "
    "training for children with autism spectrum disorder [9], while MR "
    "provides layered 3D pathology models for spatial reasoning [10].",
]

LIT_21B = [
    "Scale varies from 5,000 nursing students across 50 universities "
    "[8] to controlled cohorts of 5 [9], with a median of 30. "
    "Effectiveness concentrates on practical skills with gains above 30 "
    "percent and engagement near 92 percent, while theoretical transfer "
    "remains weak. Small samples and technical faults such as rendering "
    "latency in AI interview systems [2] recur across the set.",
]

LIT_22A = [
    "Evaluation follows a triad of learning outcomes at 85 percent, "
    "engagement at 77 percent, and usability at 58 percent. Table 2 "
    "lists the representative instruments behind these claims, from "
    "effect sizes to specificity scoring [15].",
]

LIT_22B = [
    "Synthesis selects VR simulation as the primary method because it "
    "carries the practical skill gains, with AR and MR retained as "
    "complements for overlays and spatial models. Microteaching "
    "specificity scores [15] and museum usability dimensions [16] show "
    "that measurement is maturing, but the absence of longitudinal "
    "retention data leaves the central contradiction unresolved: strong "
    "immediate gains against unknown durability.",
]

LIT_23A = [
    "Only two reviewed studies apply intelligent models to learner data. "
    "DistilBERT reaches an F1 score of 91.7 percent on feedback "
    "sentiment [5], and regression on intent to use reaches R squared "
    "of 0.883 [19]. Table 3 summarizes the usable model evidence.",
]

LIT_23B = [
    "The review provides no comparison of Random Forest, Support Vector "
    "Machine, or K Nearest Neighbours, so these are not presented as "
    "SLR findings. Random Forest is selected prospectively for SEB-XRIF "
    "on external ensemble benchmarks for the xAPI dataset [33] and its "
    "robustness to noisy educational data with ranked feature "
    "importance [32]. Voice driven dialogue remains fragile across "
    "accents and dialects [20], and abstract visualization learning "
    "shows the same boundary between demonstration and evidence [26].",
]

LIT_24A = [
    "Delivery depends on headsets such as Oculus Quest, HTC Vive, and "
    "HoloLens 2, built with Unity and Blender content and speech to "
    "text or conversational AI [10], [2]. Evidence comes from "
    "questionnaires, feedback transcripts, and performance assessments. "
    "Table 4 lists the stack that recurs often enough to specify.",
]

LIT_24B = [
    "The SLR does not consistently report programming languages, "
    "databases, or development environments, so these are not assumed. "
    "The specified foundation is therefore XR environments with 3D "
    "content, AI language technologies for feedback, and logged "
    "performance data, which Section 3 implements as Flask, React, and "
    "Chart.js over the xAPI schema.",
]

METRICS_TABLE = [
    ("Measure", "Representative result"),
    ("Learning, engagement, usability triad", "85, 77, and 58 percent of studies"),
    ("Practical effect size", "Cohen d of 0.936 [22]"),
    ("Feedback sentiment", "DistilBERT F1 of 91.7 percent [5]"),
    ("Usability dimensions", "SUS plus nine UX dimensions [16]"),
]

ML_TABLE = [
    ("Model and task", "Reported result"),
    ("DistilBERT on feedback sentiment", "F1 of 91.7 percent [5]"),
    ("Regression on intent to use", "R squared of 0.883 [19]"),
    ("Ensembles on xAPI benchmark", "Accuracy of 75 to 83 percent [33]"),
]

TECH_TABLE = [
    ("Layer", "Recurring stack"),
    ("Headsets", "Quest, Vive, HoloLens 2 [25], [9], [10]"),
    ("Content and AI", "Unity, Blender, speech to text [10], [2]"),
    ("Evidence", "Questionnaires, transcripts, assessments"),
]

TECHDESC_INTRO = [
    "This section sells the chosen technologies to a policymaker: what "
    "each technology can do, why it matters for the country, what this "
    "study uses it for, and where its limits lie. The study builds no "
    "new headset or engine. It reuses established XR hardware with an "
    "analytics and evaluation framework on standard learning data.",
]

TECHDESC_TABLE = [
    ("Technology", "Capability, national value, and study use"),
    (
        "Virtual reality simulation",
        "Brings safe practice without real world consequences. Practical "
        "gains exceed 30 percent with engagement near 92 percent [22], "
        "[1], [25]. Value is hands on training at scale, as shown by "
        "5,000 nursing students across 50 universities [8]. The study "
        "uses VR as the instructional method for procedural skills, not "
        "for abstract theory where it remains weak.",
    ),
    (
        "Random Forest with language feedback",
        "An ensemble of decision trees that tolerates noisy education "
        "data and ranks the behaviors that drive results [32]. Expected "
        "accuracy is 75 to 83 percent on the xAPI benchmark [33], while "
        "DistilBERT scores feedback sentiment at 91.7 percent F1 [5]. "
        "Value is early warning for support, not gatekeeping. The study "
        "uses it to predict Low, Medium, or High tiers with explanations.",
    ),
    (
        "xAPI logging with dashboard",
        "Experience API gives every institution the same standard event "
        "record [31], [36]. A Flask, React, and Chart.js dashboard shows "
        "trends, tiers, and importance to instructors. Value is "
        "comparability: any adopter reports accuracy with ten fold "
        "validation, usability against 76.6 [34], [28], and learning "
        "effect with Cohen d [35], [22], plus one semester follow up.",
    ),
]

TECHDESC_CLOSE = [
    "Limits are stated openly. Headset cost and dependence remain, with "
    "latency and voice recognition errors documented [2], [20]. "
    "Usability concerns persist across dimensions [16]. The analytics "
    "prototype uses primary and secondary school records and therefore "
    "cannot claim higher education outcomes until the Durban University "
    "of Technology pilot with delayed testing is complete.",
]

TABLE_COLS = [
    ("gender", "Gender"),
    ("StageID", "Stage"),
    ("Topic", "Topic"),
    ("raisedhands", "Raised hands"),
    ("VisITedResources", "Visited resources"),
    ("Class", "Class"),
]
N_SAMPLE_ROWS = 4


def load_sample_rows():
    path = DATA_FILE
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [[r[src] for src, _ in TABLE_COLS] for r in rows[:N_SAMPLE_ROWS]]


# ---------------------------------------------------------------- docx utils
def set_font(run, size=12, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic


def body(doc, text, indent=None, justify=True):
    p = doc.add_paragraph()
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        p.paragraph_format.left_indent = Inches(indent)
    set_font(p.add_run(text))
    return p


def heading(doc, text, size, space_before=6, space_after=3):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    set_font(p.add_run(text), size=size, bold=True)
    return p


def caption(doc, label, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    set_font(p.add_run(label + " "), size=10, bold=True)
    set_font(p.add_run(text), size=10)
    return p


def add_figure(doc, path, label, text, width=5.2):
    doc.add_picture(path, width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(doc, label, text)


def add_sample_table(doc):
    rows = load_sample_rows()
    table = doc.add_table(rows=len(rows) + 1, cols=len(TABLE_COLS))
    table.style = "Table Grid"
    table.alignment = 1  # centered
    for j, (_, label) in enumerate(TABLE_COLS):
        cell = table.rows[0].cells[j]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_font(p.add_run(label), size=9, bold=True)
    for i, row in enumerate(rows, start=1):
        for j, value in enumerate(row):
            p = table.rows[i].cells[j].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_font(p.add_run(value), size=9)
    blank = doc.add_paragraph()
    blank.paragraph_format.space_after = Pt(0)


def add_small_table(doc, data):
    table = doc.add_table(rows=len(data), cols=2)
    table.style = "Table Grid"
    table.alignment = 1
    for i, (left, right) in enumerate(data):
        for j, value in enumerate((left, right)):
            p = table.rows[i].cells[j].paragraphs[0]
            set_font(p.add_run(value), size=9, bold=(i == 0))
    blank = doc.add_paragraph()
    blank.paragraph_format.space_after = Pt(0)


def add_references(doc):
    heading(doc, "References", size=12)
    for i, ref in enumerate(REFERENCES, start=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Inches(0.35)
        p.paragraph_format.first_line_indent = Inches(-0.35)
        set_font(p.add_run(f"[{i}] "), size=11)
        for k, segment in enumerate(ref.split("*")):
            if segment:
                set_font(p.add_run(segment), size=11, italic=(k % 2 == 1))


def build():
    doc = Document()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(
        title.add_run("Enhancing Digital Education Using VR Technology"),
        size=14,
        bold=True,
    )

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(
        subtitle.add_run(
            "Section 3: Research Methodology and "
            "Proposed Solution plus Literature Review "
            "and Technology Description"
        ),
        size=12,
    )

    note = doc.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note.paragraph_format.space_after = Pt(12)
    set_font(
        note.add_run("Draft prepared by Team 3 for mentor review"), size=10, italic=True
    )

    heading(
        doc, "3. Research Methodology and Proposed Solution", size=14, space_before=4
    )
    for para in INTRO:
        body(doc, para)

    add_figure(
        doc,
        os.path.join(FIG_DIR, "fig3_dsrm.png"),
        "Fig. 1.",
        "DSRM phases as applied in this study.",
    )

    heading(doc, "3.1 Proposed Solution", size=12)
    body(doc, PROPOSED[0])
    body(
        doc,
        "The framework pursues four objectives: (1) "
        + OBJECTIVES[0]
        + " (2) "
        + OBJECTIVES[1]
        + " (3) "
        + OBJECTIVES[2]
        + " (4) "
        + OBJECTIVES[3],
    )

    heading(doc, "3.2 Data Gathering", size=12)
    body(doc, DATA_GATHERING[0])
    caption(doc, "Table 1:", "Sample from the xAPI Educational Mining Dataset.")
    add_sample_table(doc)
    body(doc, DATA_GATHERING[1])

    heading(doc, "3.3 Design and Development", size=12)
    for para in DESIGN:
        body(doc, para)
    add_figure(
        doc,
        os.path.join(FIG_DIR, "fig3_pipeline.png"),
        "Fig. 2.",
        "The SEB-XRIF design and development pipeline.",
    )

    heading(doc, "3.4 Evaluation Criteria", size=12)
    for para in EVALUATION:
        body(doc, para)

    heading(doc, "2. Literature Review", size=14, space_before=4)
    for para in LIT_INTRO:
        body(doc, para)

    heading(doc, "2.1 Existing Approaches", size=12)
    body(doc, LIT_21A[0])
    add_figure(
        doc,
        os.path.join(FIG_DIR, "fig_lit_methods.png"),
        "Fig. 3.",
        "Immersive methods across the 28 reviewed studies.",
    )
    body(doc, LIT_21B[0])

    heading(doc, "2.2 Theoretical Evaluation and Synthesis", size=12)
    body(doc, LIT_22A[0])
    caption(doc, "Table 2:", "Representative evaluation instruments.")
    add_small_table(doc, METRICS_TABLE)
    body(doc, LIT_22B[0])

    heading(doc, "2.3 Theoretical Evaluation of Intelligent Models", size=12)
    body(doc, LIT_23A[0])
    caption(doc, "Table 3:", "Usable model evidence.")
    add_small_table(doc, ML_TABLE)
    body(doc, LIT_23B[0])

    heading(doc, "2.4 Technical Considerations", size=12)
    body(doc, LIT_24A[0])
    caption(doc, "Table 4:", "Recurring technical stack.")
    add_small_table(doc, TECH_TABLE)
    body(doc, LIT_24B[0])

    heading(doc, "4. Technology Description", size=14, space_before=4)
    body(doc, TECHDESC_INTRO[0])
    caption(doc, "Table 5:", "Technologies sold at capability level.")
    add_small_table(doc, TECHDESC_TABLE)
    body(doc, TECHDESC_CLOSE[0])

    add_references(doc)
    doc.save(OUT)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    build()
