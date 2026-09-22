"""Section 3 figures for the SEB-XRIF full paper (Team 3).

Fig. 1: the five DSRM steps used in this study (adapted from
Peffers et al.).
Fig. 2: the SEB-XRIF design and development pipeline.

Both figures use a wrapped grid layout (3 columns x 2 rows) so text
fits inside the boxes. Single-row horizontal layout was retired because
the boxes were too narrow and titles spilled over the edges.

Style follows make_fig1_methods.py conventions: matplotlib Agg backend,
PNG at 300 dpi plus PDF, printed summary.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import textwrap

FACE = "#E8EEF9"
EDGE = "#4472C4"
TITLE_C = "#1F3864"
DESC_C = "#222222"
ARROW_C = "#555555"

DSRM_PHASES = [
    ("1. Problem identification",
     "SLR gaps, passive 2D, N=30"),
    ("2. Data acquisition",
     "xAPI 480 records, public, complete"),
    ("3. Proposed solution",
     "SEB-XRIF, SWOT, four layers"),
    ("4. Design and development",
     "Random Forest, dashboard"),
    ("5. Evaluation and results communication",
     "Accuracy, SUS, d, report"),
]

PIPELINE_STAGES = [
    ("Raw xAPI data",
     "480 records, 16 features"),
    ("Preprocessing",
     "Complete, one-hot, numeric counts"),
    ("Stratified split",
     "80/20, fixed seed"),
    ("Random Forest",
     "100 trees, balanced weights"),
    ("Model outputs",
     "Tiers, metrics, importance"),
    ("Dashboard",
     "Flask, React, SUS, Cohen d"),
]


def flow_figure(boxes, base_name, iteration_arrow=False, ncols=3):
    n = len(boxes)
    nrows = (n + ncols - 1) // ncols

    # Wrap first so box height fits the longest text block.
    wrapped = []
    for heading, desc in boxes:
        t_lines = textwrap.wrap(heading, width=22)
        d_lines = textwrap.wrap(desc, width=26)
        wrapped.append((t_lines, d_lines))
    max_t = max(len(t) for t, _ in wrapped)
    max_d = max(len(d) for _, d in wrapped)
    line_h, pad_top, gap_mid, pad_bot = 1.35, 1.2, 0.7, 1.1
    box_h = pad_top + max_t * 1.55 + gap_mid + max_d * line_h + pad_bot
    box_w, h_gap, v_gap, margin = 12.0, 3.0, 5.0, 1.0
    x_range = margin * 2 + ncols * box_w + (ncols - 1) * h_gap
    bottom_extra = 3.5 if iteration_arrow else 1.0
    y_range = margin * 2 + nrows * box_h + (nrows - 1) * v_gap + bottom_extra
    fig_w = 7.2
    fig_h = fig_w * y_range / x_range

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, x_range)
    ax.set_ylim(0, y_range)
    ax.axis("off")

    centres = []
    for i, (t_lines, d_lines) in enumerate(wrapped):
        r, c = divmod(i, ncols)
        bx = margin + c * (box_w + h_gap)
        btop = y_range - margin - r * (box_h + v_gap)
        patch = FancyBboxPatch((bx, btop - box_h), box_w, box_h,
                               boxstyle="round,pad=0.18",
                               facecolor=FACE, edgecolor=EDGE, linewidth=1.2)
        ax.add_patch(patch)
        cx = bx + box_w / 2
        ax.text(cx, btop - pad_top, "\n".join(t_lines), ha="center",
                va="top", fontsize=8.5, fontweight="bold", color=TITLE_C,
                linespacing=1.45, wrap=True)
        y_desc = btop - pad_top - len(t_lines) * 1.55 - gap_mid
        ax.text(cx, y_desc, "\n".join(d_lines), ha="center", va="top",
                fontsize=7.5, color=DESC_C, linespacing=1.5, wrap=True)
        centres.append((bx, btop))
        if c > 0:
            pbx, pbtop = centres[i - 1]
            y_mid = btop - box_h / 2
            ax.annotate("", xy=(bx - 0.3, y_mid),
                        xytext=(pbx + box_w + 0.3, y_mid),
                        arrowprops=dict(arrowstyle="-|>", color=ARROW_C,
                                        linewidth=1.5))
        elif r > 0:
            # Elbow connector: down from end of previous row, across,
            # into the top of this row's first box.
            pbx, pbtop = centres[i - 1]
            x_from = pbx + box_w / 2
            y_from = pbtop - box_h - 0.3
            x_to = bx + box_w / 2
            y_to = btop + 0.3
            mid_y = (y_from + y_to) / 2
            ax.plot([x_from, x_from], [y_from, mid_y], color=ARROW_C, lw=1.5)
            ax.plot([x_from, x_to], [mid_y, mid_y], color=ARROW_C, lw=1.5)
            ax.annotate("", xy=(x_to, y_to),
                        xytext=(x_to, mid_y),
                        arrowprops=dict(arrowstyle="-|>", color=ARROW_C,
                                        linewidth=1.5))

    if iteration_arrow:
        y_arc = margin + 0.4
        ax.annotate("", xy=(margin + box_w / 2, y_arc),
                    xytext=(x_range - margin - box_w / 2, y_arc),
                    arrowprops=dict(arrowstyle="-|>", color=ARROW_C,
                                    linewidth=1.2, linestyle="--",
                                    connectionstyle="arc3,rad=-0.12"))
        ax.text(x_range / 2, y_arc + 0.5, "iterative refinement",
                ha="center", va="bottom", fontsize=7.5, style="italic",
                color=ARROW_C)

    fig.savefig(f"{base_name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(f"{base_name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {base_name}.png and {base_name}.pdf "
          f"(wrapped {ncols}x{nrows}, {len(boxes)} stages, {fig_w:.1f} x "
          f"{fig_h:.1f} in)")


if __name__ == "__main__":
    flow_figure(DSRM_PHASES, "fig3_dsrm")
    flow_figure(PIPELINE_STAGES, "fig3_pipeline")
    print("Section 3 figures complete")
