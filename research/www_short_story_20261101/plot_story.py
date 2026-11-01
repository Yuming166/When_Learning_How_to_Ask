"""Conceptual synthesis of existing theorems, not a new numerical experiment."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


OUT = Path(__file__).resolve().parent
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "pdf.fonttype": 42, "ps.fonttype": 42})
fig, ax = plt.subplots(figsize=(11, 6.4))
fig.patch.set_facecolor("white")
ax.set(xlim=(0, 1), ylim=(0, 1))
ax.axis("off")


def box(x, y, w, h, label, fill="#edf3f8", edge="#597488", size=11):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                          linewidth=1.2, edgecolor=edge, facecolor=fill)
    ax.add_patch(rect)
    ax.text(x+w/2, y+h/2, label, ha="center", va="center", fontsize=size,
            linespacing=1.5, color="#182b39")


def arrow(start, end, color="#597488"):
    ax.annotate("", xy=end, xytext=start,
                arrowprops={"arrowstyle": "->", "color": color, "lw": 1.5})


ax.text(.025, .96, "Reliable Web evidence acquisition", fontsize=17,
        weight="bold", color="#182b39")
ax.text(.025, .915, "Source reports and extraction outputs are different evidence units.",
        color="#485e6c", fontsize=11)

box(.03, .64, .17, .12, "Unknown fact\n$\\theta$")
box(.38, .72, .22, .10, "Persistent report\n$V_1$")
box(.38, .49, .22, .10, "Independent report\n$V_2$")
box(.77, .78, .19, .075, "Read $Y_{1,1}$", size=11)
box(.77, .66, .19, .075, "Read $Y_{1,2}$", size=11)
box(.77, .50, .19, .075, "Read $Y_{2,1}$", size=11)

arrow((.21, .72), (.365, .77))
arrow((.21, .67), (.365, .54))
arrow((.615, .785), (.755, .817))
arrow((.615, .755), (.755, .698))
arrow((.615, .54), (.755, .54))
ax.text(.285, .825, "source accuracy $r$", ha="center", fontsize=10)
ax.text(.27, .54, "new root: $c$", ha="center", fontsize=10)
ax.text(.69, .88, "extraction: $p,q$", ha="center", fontsize=10)
ax.text(.69, .615, "each read: $\\ell$", ha="center", fontsize=10)
ax.text(.49, .435, "Repeated reads share one report; a new root supplies another report.",
        ha="center", fontsize=10, color="#485e6c")

ax.text(.025, .365, "What changes the optimal reading depth?", fontsize=13,
        weight="bold", color="#182b39")
box(.03, .135, .285, .18,
    "Perfect sources: $r=1$\nUnknown $p,q$\nMaximum depth $N$ suffices", size=10.5)
box(.355, .135, .285, .18,
    "Imperfect sources\nKnown $p,q$\nA fixed depth suffices", size=10.5)
box(.68, .135, .285, .18,
    "Imperfect sources; unknown $p,q$\nFinite calibration\nMultiple depths can be necessary",
    fill="#fff2df", edge="#ad762e", size=10.0)
ax.text(.50, .075,
        "Completed blocks; known source rate and better format; first-order online cost.",
        ha="center", fontsize=9.5, color="#485e6c")
ax.text(.50, .032,
        "Controls summarize model theorems. Necessity holds in an explicit certified region; no Web/LLM measurements.",
        ha="center", fontsize=8.7, color="#485e6c")

fig.subplots_adjust(left=.01, right=.99, bottom=.01, top=.99)
fig.savefig(OUT / "theory_story.png", dpi=180, facecolor="white")
fig.savefig(OUT / "theory_story.pdf", facecolor="white",
            metadata={"CreationDate": None, "ModDate": None,
                      "Title": "Conceptual summary of existing source-depth results"})
plt.close(fig)
