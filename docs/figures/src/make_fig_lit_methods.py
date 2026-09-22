"""Compact methods graph for the full-paper literature review (Team 3 doc).

Single-panel bar chart reusing make_fig1_methods.py counts:
VR=16, AR=3, MR=4, MR/AR=1, XR=1, immersive sim=2 (27 classified of 28;
Leonori et al. has no file and is excluded).
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ORDER = ["VR", "AR", "MR", "MR/AR", "XR", "Imm. sim."]
COUNTS = [16, 3, 4, 1, 1, 2]
COLORS = ["#4472C4", "#ED7D31", "#70AD47", "#9E6BB5", "#17A2B8", "#7F7F7F"]

fig, ax = plt.subplots(figsize=(5.4, 2.6))
bars = ax.bar(ORDER, COUNTS, color=COLORS, edgecolor="black", linewidth=0.8)
for bar, n in zip(bars, COUNTS):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.15,
        str(n),
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
    )
ax.set_ylabel("Studies", fontsize=9)
ax.set_ylim(0, 18)
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(axis="x", labelsize=8.5)
fig.tight_layout()
fig.savefig("fig_lit_methods.png", dpi=300, bbox_inches="tight")
fig.savefig("fig_lit_methods.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved fig_lit_methods.png and fig_lit_methods.pdf")
