"""Lab9 тайлангийн зургууд. Ажиллуулах: python figs.py (Lab9_CubeSpace хавтсаас)"""
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

HERE = Path(__file__).resolve().parent
OUT = HERE / "figs"
OUT.mkdir(exist_ok=True)
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 10


def node(ax, x, y, text, w=1.9, h=0.62, fc="white", ec="black", ls="-", fs=9):
    ax.add_patch(Ellipse((x, y), w, h, fc=fc, ec=ec, lw=1.2, ls=ls))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs)


def arrow(ax, x1, y1, x2, y2, color="black", ls="-"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=0.9, ls=ls,
                                shrinkA=11, shrinkB=11))


# ---------- 1. 4-D lattice ----------
dims4 = ["time", "item", "location", "supplier"]
fig, ax = plt.subplots(figsize=(10, 6))
pos = {}
for k in range(5):
    cs = list(combinations(dims4, k))
    y = 4 - k
    n = len(cs)
    for j, c in enumerate(cs):
        x = (j - (n - 1) / 2) * 2.3
        pos[c] = (x, y * 1.35)
for c, (x, y) in pos.items():
    for d in dims4:
        if d not in c:
            child = tuple(sorted(c + (d,), key=dims4.index))
            x2, y2 = pos[child]
            ax.plot([x, x2], [y, y2], color="gray", lw=0.6, zorder=0)
for c, (x, y) in pos.items():
    lbl = "all" if not c else ",\n".join(c) if len(c) > 2 else ", ".join(c)
    node(ax, x, y, lbl, w=2.05, h=0.75 if len(c) > 2 else 0.55, fs=8)
for k in range(5):
    ax.text(-8.2, (4 - k) * 1.35, f"{k}-D", fontsize=10, fontweight="bold", va="center")
ax.set_xlim(-8.6, 7.6)
ax.set_ylim(-0.6, 6.0)
ax.axis("off")
fig.tight_layout()
fig.savefig(OUT / "fig1_lattice.png", dpi=200)
plt.close(fig)

# ---------- 2. BUC мод (min_sup = 3) ----------
fig, ax = plt.subplots(figsize=(10, 4.6))
H = 0.8
N = {
    "all": (0.5, 3.2, "(*, *)\ncount = 10", "white"),
    "deb": (-4.0, 1.65, "(Дэвтэр, *)\n5", "white"),
    "nom": (-0.2, 1.65, "(Ном, *)\n5", "white"),
    "ub": (2.9, 1.65, "(*, УБ)\n7", "white"),
    "dk": (5.2, 1.65, "(*, Дархан)\n3", "white"),
    "deb_ub": (-5.1, 0.1, "(Дэвтэр, УБ)\n3", "white"),
    "deb_dk": (-2.9, 0.1, "(Дэвтэр, Дархан)\n2", "#e6e6e6"),
    "nom_ub": (-0.9, 0.1, "(Ном, УБ)\n4", "white"),
    "nom_dk": (1.2, 0.1, "(Ном, Дархан)\n1", "#e6e6e6"),
}
E = [("all", "deb"), ("all", "nom"), ("all", "ub"), ("all", "dk"),
     ("deb", "deb_ub"), ("deb", "deb_dk"), ("nom", "nom_ub"), ("nom", "nom_dk")]
for a, b in E:
    pruned = N[b][3] != "white"
    ax.annotate("", xy=(N[b][0], N[b][1] + H / 2), xytext=(N[a][0], N[a][1] - H / 2),
                arrowprops=dict(arrowstyle="-|>", color="gray" if pruned else "black", lw=0.9,
                                ls="--" if pruned else "-", shrinkA=0, shrinkB=0))
for k, (x, y, t, fc) in N.items():
    pruned = fc != "white"
    node(ax, x, y, t, w=2.0, h=H, fc=fc, ec="gray" if pruned else "black",
         ls="--" if pruned else "-", fs=8.5)
ax.text(-1.9, -0.75, "саарал = count < 3, prune хийгдсэн", fontsize=9, ha="center", color="dimgray")
ax.set_xlim(-6.3, 6.4)
ax.set_ylim(-1.0, 3.8)
ax.axis("off")
fig.tight_layout()
fig.savefig(OUT / "fig2_buc.png", dpi=200)
plt.close(fig)

# ---------- 3. Materialization ----------
sales = pd.read_csv(HERE / "cs_sales.csv")
dim_loc = pd.read_csv(HERE / "cs_dim_location.csv")
df = sales.merge(dim_loc, on="district")
df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")
D3 = ["item", "city", "month"]
cuboids = [c for k in range(3, -1, -1) for c in combinations(D3, k)]
sizes = {c: (len(df[list(c)].drop_duplicates()) if c else 1) for c in cuboids}
base = tuple(D3)


def avg_cost(mat):
    return np.mean([min(sizes[m] for m in mat if set(q) <= set(m)) for q in cuboids])


part = [base, ("city", "month"), ("item", "city")]
lab = ["Full", "No", "Partial"]
stor = [sum(sizes.values()), sizes[base], sum(sizes[m] for m in part)]
cost = [avg_cost(cuboids), avg_cost([base]), avg_cost(part)]
fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
for a, vals, t in [(ax[0], stor, "Хадгалалт (мөр)"), (ax[1], cost, "Query-ийн дундаж өртөг (мөр)")]:
    b = a.bar(lab, vals, color=["#9e9e9e", "#d0d0d0", "#4a6fa5"], edgecolor="black", lw=0.6)
    a.bar_label(b, labels=[f"{v:g}" for v in np.round(vals, 1)], fontsize=9)
    a.set_title(t, fontsize=10)
    a.spines[["top", "right"]].set_visible(False)
    a.set_ylim(0, max(vals) * 1.15)
fig.tight_layout()
fig.savefig(OUT / "fig3_materialization.png", dpi=200)
plt.close(fig)

# ---------- 4. SelfExp ба InExp ----------
mo = pd.read_csv(HERE / "cs_monthly_item_city.csv")
nat = mo.pivot_table(index="item", columns="month", values="sales", aggfunc="sum")
chg = ((nat / nat.shift(1, axis=1) - 1) * 100).loc[:, 1:6]
expv = chg.mean(axis=1).to_numpy()[:, None] + chg.mean(axis=0).to_numpy()[None, :] - chg.to_numpy().mean()
resid = chg - expv
z_self = (resid / resid.stack().std()).abs()
cm = mo.pivot_table(index=["item", "city"], columns="month", values="sales", aggfunc="sum")
cchg = ((cm / cm.shift(1, axis=1) - 1) * 100).loc[:, 1:6]
diff = cchg - chg.reindex(cchg.index.get_level_values("item")).to_numpy()
z_in = (diff / diff.stack().std()).abs().groupby(level="item").max()

fig, ax = plt.subplots(1, 2, figsize=(10, 3.2))
for a, m, t, vmax in [(ax[0], z_self, "SelfExp |z|", 3), (ax[1], z_in, "InExp: хотуудын max |z|", 3)]:
    a.imshow(np.minimum(m.to_numpy(), vmax), cmap="Greys", vmin=0, vmax=vmax * 1.3, aspect="auto")
    a.set_xticks(range(6), [f"{c}-р сар" for c in m.columns], fontsize=8)
    a.set_yticks(range(len(m)), m.index)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.iat[i, j]
            a.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8.5,
                   color="white" if v > 2 else "black", fontweight="bold" if v > 2 else "normal")
    a.set_title(t, fontsize=10)
fig.tight_layout()
fig.savefig(OUT / "fig4_exceptions.png", dpi=200)
plt.close(fig)

# ---------- 5. Ховд хотын Принтерийн drill-down ----------
pr = mo[mo["item"] == "Принтер"].pivot_table(index="month", columns="city", values="sales")
idx = pr / pr.loc[0] * 100
fig, ax = plt.subplots(figsize=(7.5, 3.3))
for c in idx.columns:
    hl = c == "Ховд"
    ax.plot(idx.index, idx[c], marker="o", ms=3.5, lw=2.0 if hl else 0.9,
            color="black" if hl else "silver", label=c if hl else None, zorder=3 if hl else 1)
ax.plot(nat.columns, nat.loc["Принтер"] / nat.loc["Принтер", 0] * 100, ls="--", color="#4a6fa5",
        lw=1.4, label="Нийт (улс)")
ax.set_xticks(range(7), ["12-р сар"] + [f"{m}-р сар" for m in range(1, 7)], fontsize=8)
ax.set_ylabel("Индекс (12-р сар = 100)")
ax.legend(fontsize=8.5, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "fig5_printer.png", dpi=200)
plt.close(fig)

print("saved to", OUT)
