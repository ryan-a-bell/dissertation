import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon, Patch, FancyBboxPatch
import numpy as np

# ── Style setup ──────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#333333",
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.color": "#444444",
    "ytick.color": "#444444",
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "figure.dpi": 200,
})

# ── Color palette ────────────────────────────────────────────────────────
C_GREEN  = "#2d936c"   # MCQ-sufficient
C_AMBER  = "#c4820e"   # Dual-modality recommended
C_RED    = "#c0392b"   # Dual-modality required
C_DIAG   = "#555555"   # Diagonal reference
C_BOUND  = "#2d936c"   # x=85 boundary

# ── Figure ───────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xlabel("MCQ Accuracy (%)", fontsize=12, labelpad=10)
ax.set_ylabel("OSQ Accuracy (%)", fontsize=12, labelpad=10)

ax.set_aspect("equal")
ax.set_xticks(np.arange(0, 101, 20))
ax.set_yticks(np.arange(0, 101, 20))

# ── Helper ───────────────────────────────────────────────────────────────
def add_poly(pts, fc, alpha):
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec="none", alpha=alpha))

# ── Thresholds ───────────────────────────────────────────────────────────
D_SMALL, D_MOD, X_MIN = 5, 15, 85

# ── Dual-modality REQUIRED (|Δ| ≥ 15) — drawn first (background) ──────
add_poly([(0, 15), (0, 100), (85, 100)],       fc=C_RED, alpha=0.18)
add_poly([(15, 0), (100, 0),  (100, 85)],      fc=C_RED, alpha=0.18)

# ── Dual-modality RECOMMENDED (5 ≤ |Δ| < 15) ──────────────────────────
add_poly([(0, 5), (0, 15), (85, 100), (95, 100)],     fc=C_AMBER, alpha=0.20)
add_poly([(5, 0), (15, 0), (100, 85), (100, 95)],     fc=C_AMBER, alpha=0.20)

# ── MCQ-sufficient (|Δ| < 5 AND x ≥ 85) ───────────────────────────────
add_poly(
    [(85, 80), (85, 90), (95, 100), (100, 100), (100, 95)],
    fc=C_GREEN, alpha=0.30
)

# ── Boundary lines ───────────────────────────────────────────────────────
line_kw = dict(linewidth=0.9, linestyle="--", zorder=3)
ax.plot([0, 100], [0, 100],     color=C_DIAG,  linewidth=1.1, linestyle="-",  zorder=3, alpha=0.6)
ax.plot([0, 100], [5, 105],     color=C_GREEN,  **line_kw, alpha=0.55)
ax.plot([0, 100], [-5, 95],     color=C_GREEN,  **line_kw, alpha=0.55)
ax.plot([0, 100], [15, 115],    color=C_RED,    **line_kw, alpha=0.55)
ax.plot([0, 100], [-15, 85],    color=C_RED,    **line_kw, alpha=0.55)
ax.axvline(X_MIN, color=C_BOUND, linewidth=1.0, linestyle=":", zorder=3, alpha=0.7)

# ── Labels ───────────────────────────────────────────────────────────────
label_kw = dict(
    fontsize=9, ha="center", va="center", style="italic",
    path_effects=[pe.withStroke(linewidth=3, foreground="white")]
)

ax.text(92.5, 93, "MCQ-sufficient\n($x$ ≥ 85%,  |Δ| < 5)",
        fontsize=8.5, ha="center", va="center", style="italic",
        path_effects=[pe.withStroke(linewidth=3, foreground="white")],
        color="#1a6b4a")
ax.text(30, 78, "Dual-modality\nrequired  (|Δ| ≥ 15)",
        **label_kw, color=C_RED)
ax.text(78, 22, "Dual-modality\nrequired  (|Δ| ≥ 15)",
        **label_kw, color=C_RED)
ax.text(30, 28, "Dual-modality\nrecommended  (5–15%)",
        **label_kw, color="#8a5e00")
ax.text(68, 70, "Dual-modality\nrecommended  (5–15%)",
        **label_kw, color="#8a5e00")

# ── Δ annotation arrows ─────────────────────────────────────────────────
arr_kw = dict(arrowstyle="<->", color="#666666", lw=0.8)
ax.annotate("", xy=(50, 55), xytext=(50, 50),
            arrowprops=arr_kw)
ax.text(52, 52.5, "|Δ| = 5", fontsize=7.5, color="#666666", va="center",
        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])

ax.annotate("", xy=(40, 55), xytext=(40, 40),
            arrowprops=arr_kw)
ax.text(37.5, 47.5, "|Δ| = 15", fontsize=7.5, color="#666666", va="center", ha="right",
        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])

# ── Legend ────────────────────────────────────────────────────────────────
handles = [
    Patch(fc=C_GREEN, alpha=0.30, ec="#1a6b4a", lw=0.6,
          label="MCQ-sufficient  (|Δ| < 5, Acc ≥ 85%)"),
    Patch(fc=C_AMBER, alpha=0.20, ec="#8a5e00", lw=0.6,
          label="Dual-modality recommended  (5% ≤ |Δ| < 15%)"),
    Patch(fc=C_RED,   alpha=0.18, ec=C_RED,     lw=0.6,
          label="Dual-modality required  (|Δ| ≥ 15)"),
]
leg = ax.legend(
    handles=handles, loc="lower right", frameon=True,
    fontsize=9, framealpha=0.92, edgecolor="#cccccc",
    borderpad=0.8, handlelength=1.5
)
leg.get_frame().set_linewidth(0.6)

# ── Grid & cleanup ──────────────────────────────────────────────────────
ax.grid(True, which="major", color="#cccccc")
fig.tight_layout(pad=1.5)
fig.savefig("/home/claude/obj7_classification_regions.png",
            dpi=250, bbox_inches="tight", facecolor="white")
plt.show()
print("Saved.")
