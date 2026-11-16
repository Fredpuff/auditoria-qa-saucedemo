# Graficos de resultados (casos aprobados/fallidos por tecnica y por modulo, defectos por severidad).
import os
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datos import CASOS, BUGS, RAIZ, resultados_playwright, estado_caso

AZUL, NARANJA = "#2a78d6", "#eb6834"  # categorico 1 y 2 de la paleta validada
TXT, TXT2, FONDO, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
plt.rcParams.update({"font.family": "Arial", "font.size": 10, "axes.edgecolor": GRID, "text.color": TXT,
                     "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT})
estados, _, _ = resultados_playwright()
OUT = os.path.join(RAIZ, "docs", "img")


def apiladas(clave, orden, archivo, titulo):
    ok = [sum(1 for c in CASOS if c[clave] == k and estado_caso(c, estados) == "Aprobado") for k in orden]
    ko = [sum(1 for c in CASOS if c[clave] == k and estado_caso(c, estados) == "Fallido") for k in orden]
    fig, ax = plt.subplots(figsize=(8.5, 0.5 * len(orden) + 1.3), facecolor=FONDO)
    ax.set_facecolor(FONDO)
    y = range(len(orden))[::-1]
    ax.barh(list(y), ok, height=0.55, color=AZUL, label="Aprobados", edgecolor=FONDO, linewidth=2)
    ax.barh(list(y), ko, left=ok, height=0.55, color=NARANJA, label="Fallidos", edgecolor=FONDO, linewidth=2)
    for yi, a, f in zip(y, ok, ko):
        ax.text(a + f + 0.3, yi, f"{a} aprobados / {f} fallidos", va="center", fontsize=9, color=TXT2)
    ax.set_yticks(list(y))
    ax.set_yticklabels(orden)
    ax.set_xlabel("Número de casos")
    ax.set_xlim(0, max(a + f for a, f in zip(ok, ko)) * 1.55)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="lower right", frameon=False, ncol=2)
    ax.set_title(titulo, loc="left", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, archivo), dpi=160, facecolor=FONDO)
    plt.close(fig)


apiladas("tecnica", ["Positiva", "Negativa", "Valores límite", "Tabla de decisión", "Transición de estados",
                     "Predicción de errores", "Exploratoria (manual)"], "grafico-tecnica.png", "Casos por técnica")
apiladas("modulo", ["Login", "Catálogo", "Detalle de producto", "Carrito", "Checkout", "Menú", "Control de acceso"],
         "grafico-modulo.png", "Casos por módulo")

# defectos por severidad: una sola serie, sin leyenda
orden = ["Crítica", "Alta", "Media", "Baja"]
c = Counter(b["severidad"] for b in BUGS)
fig, ax = plt.subplots(figsize=(6.5, 2.8), facecolor=FONDO)
ax.set_facecolor(FONDO)
y = list(range(len(orden)))[::-1]
ax.barh(y, [c[s] for s in orden], height=0.55, color=AZUL)
for yi, s in zip(y, orden):
    ax.text(c[s] + 0.1, yi, str(c[s]), va="center", fontsize=10, color=TXT)
ax.set_yticks(y)
ax.set_yticklabels(orden)
ax.set_xlim(0, max(c.values()) + 1.5)
ax.xaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.set_title(f"Defectos por severidad (total {len(BUGS)})", loc="left", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "grafico-severidad.png"), dpi=160, facecolor=FONDO)
plt.close(fig)
print("graficos ok")
