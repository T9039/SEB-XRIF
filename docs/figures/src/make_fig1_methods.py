"""Figure 1 (replaces Table 1): immersive methods used across the 28 reviewed studies.

Classification verified against the actual papers in files/:
[4] SkillsLab+ is AR (Magic Leap), [6] is MR (historical sites guide), [14] EDUFUSION is AR,
[21]/[24] use immersive simulators with no XR hardware, [28] is an XR authoring tool.
[7] Leonori et al. is NOT present in files/ and is therefore not plotted.
"""

import matplotlib

matplotlib.use("Agg")
from collections import Counter, defaultdict

import matplotlib.pyplot as plt

studies = [
    # --- VR (16) ---
    ("[1] Cahya & Hartono", "VR"),
    ("[2] Mongkoljaturong et al.", "VR"),
    ("[3] Ai et al.", "VR"),
    ("[5] Al-Sudani et al.", "VR"),
    ("[8] Zhang", "VR"),
    ("[11] Litchaweerat et al.", "VR"),
    ("[12] Hussein et al.", "VR"),
    ("[13] Rahman et al.", "VR"),
    ("[15] Jacobsen et al.", "VR"),
    ("[17] Sunardi et al.", "VR"),
    ("[18] Marandi & Kashanifar", "VR"),
    ("[19] Wong Gonzales et al.", "VR"),
    ("[22] Chang & Hsu", "VR"),
    ("[23] Dickinson & McIntosh", "VR"),
    ("[25] Xing et al.", "VR"),
    ("[26] Patra et al.", "VR"),
    # --- AR (3) ---
    ("[4] Gießer et al. (SkillsLab+)", "AR"),
    ("[9] Smith et al.", "AR"),
    ("[14] D'Souza et al.", "AR"),
    # --- MR (4) ---
    ("[6] Chu et al.", "MR"),
    ("[10] Toledano et al.", "MR"),
    ("[20] Vaze et al.", "MR"),
    ("[27] Xia et al.", "MR"),
    # --- MR/AR (1) ---
    ("[16] Huang et al.", "MR/AR"),
    # --- XR (1) ---
    ("[28] Kim et al.", "XR"),
    # --- Immersive simulation, no XR hardware (2) ---
    ("[21] Nieto & González-Bañales", "Immersive sim."),
    ("[24] Wang et al.", "Immersive sim."),
]

ORDER = ["VR", "AR", "MR", "MR/AR", "XR", "Immersive sim."]
COLORS = {
    "VR": "#4472C4",
    "AR": "#ED7D31",
    "MR": "#70AD47",
    "MR/AR": "#9E6BB5",
    "XR": "#17A2B8",
    "Immersive sim.": "#7F7F7F",
}

counts = Counter(m for _, m in studies)
total = len(studies)
groups = defaultdict(list)
for name, m in studies:
    groups[m].append(name)

fig = plt.figure(figsize=(11, 6.2))
gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1], wspace=0.05)
ax = fig.add_subplot(gs[0])
axl = fig.add_subplot(gs[1])
axl.axis("off")

bars = ax.bar(
    ORDER,
    [counts.get(m, 0) for m in ORDER],
    color=[COLORS[m] for m in ORDER],
    edgecolor="black",
    linewidth=0.8,
)
for bar, m in zip(bars, ORDER):
    n = counts.get(m, 0)
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.2,
        f"{n}\n({n / total:.0%})",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

ax.set_ylabel("Number of studies", fontsize=11)
ax.set_xlabel("Immersive method", fontsize=11)
ax.set_ylim(0, max(counts.values(), default=0) + 2.5)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title(
    "Immersive methods used across the 28 reviewed studies", fontsize=12, pad=12
)
ax.tick_params(axis="x", labelsize=9.5)

# Side panel: every paper, grouped by method
lines = total + len([m for m in ORDER if groups.get(m)]) + 2
step = min(0.032, 0.95 / lines)
y = 1.0
for m in ORDER:
    if not groups.get(m):
        continue
    axl.text(
        0.02,
        y,
        f"{m} ({counts[m]})",
        transform=axl.transAxes,
        fontsize=10,
        fontweight="bold",
        color=COLORS[m],
        va="top",
    )
    y -= step * 1.15
    for nm in sorted(groups[m], key=lambda s: int(s.split("]")[0][1:])):
        axl.text(
            0.06,
            y,
            "\u2022 " + nm,
            transform=axl.transAxes,
            fontsize=9,
            va="top",
            color="#222222",
        )
        y -= step
    y -= step * 0.4

fig.savefig("fig1_methods.png", dpi=300, bbox_inches="tight")
fig.savefig("fig1_methods.pdf", bbox_inches="tight")
print(f"Plotted {total} studies:", dict(counts))
print("Saved fig1_methods.png and fig1_methods.pdf")
