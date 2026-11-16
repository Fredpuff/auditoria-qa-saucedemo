# Genera los diagramas de transicion de estados y el mapa mental (docs/img).
# Uso: python tools/diagramas.py
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = "docs/img"
os.makedirs(OUT, exist_ok=True)
plt.rcParams["font.family"] = "Arial"


def caja(ax, x, y, texto, w=1.9, h=0.7, color="#e8eef7", borde="#2f4b7c"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05",
                                fc=color, ec=borde, lw=1.5))
    ax.text(x, y, texto, ha="center", va="center", fontsize=10)


def flecha(ax, a, b, texto="", color="#333333", estilo="-", rad=0.0, dx=0, dy=0.18, fs=8.5):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14, color=color,
                                 linestyle=estilo, lw=1.3, connectionstyle=f"arc3,rad={rad}"))
    if texto:
        ax.text((a[0] + b[0]) / 2 + dx, (a[1] + b[1]) / 2 + dy, texto, ha="center", va="center",
                fontsize=fs, color=color, bbox=dict(fc="white", ec="none", pad=0.5))


# ---------------- Checkout ----------------
fig, ax = plt.subplots(figsize=(13, 6.2))
ax.set_xlim(0, 13); ax.set_ylim(0, 6.2); ax.axis("off")
P = {"S0": (1.0, 4.2), "S1": (3.4, 4.2), "S2": (5.8, 4.2), "S3": (8.2, 4.2), "S4": (10.6, 4.2),
     "S5": (12.2, 4.2)}
caja(ax, *P["S0"], "Login", w=1.3)
caja(ax, *P["S1"], "S1 Inventario")
caja(ax, *P["S2"], "S2 Carrito")
caja(ax, *P["S3"], "S3 Información\n(step-one)")
caja(ax, *P["S4"], "S4 Resumen\n(step-two)")
caja(ax, 10.6, 1.6, "S5 Completado\n(checkout-complete)")
flecha(ax, (1.65, 4.2), (2.45, 4.2), "login válido")
flecha(ax, (4.35, 4.3), (4.85, 4.3), "icono\ncarrito", dy=0.45)
flecha(ax, (6.75, 4.3), (7.25, 4.3), "Checkout", dy=0.35)
flecha(ax, (9.15, 4.3), (9.65, 4.3), "Continue\n(datos válidos)", dy=0.45)
flecha(ax, (10.6, 3.85), (10.6, 1.95), "Finish", dx=0.45, dy=0)
flecha(ax, (9.65, 1.6), (3.4, 3.85), "Back Home (vacía el carrito)", rad=-0.15, dy=-0.55)
# cancelaciones
flecha(ax, (7.3, 4.0), (6.7, 4.0), "Cancel", color="#8a5a00", dy=-0.3)
flecha(ax, (5.0, 4.0), (4.3, 4.0), "Continue\nShopping", color="#8a5a00", dy=-0.42)
flecha(ax, (10.6, 4.55), (3.4, 4.55), "Cancel en Resumen", color="#8a5a00", rad=0.25, dy=1.25)
# transiciones invalidas
ax.text(0.2, 0.95, "Transiciones inválidas (deben bloquearse):", fontsize=9.5, weight="bold", color="#b00020")
ax.text(0.2, 0.6, "T1: URL directa a /checkout-step-two.html sin sesión -> Login con mensaje (CP-34, se bloquea)", fontsize=9, color="#b00020")
ax.text(0.2, 0.3, "T2: URL directa a /checkout-complete.html con sesión y sin compra -> la app muestra 'Thank you for your order!' (CP-35, BUG-19)", fontsize=9, color="#b00020")
ax.text(0.2, 0.0, "T3: Checkout con el carrito vacío (S2 sin productos -> S3) -> la app lo permite (CP-10, BUG-14)", fontsize=9, color="#b00020")
ax.set_title("Diagrama de transición de estados del checkout", fontsize=13, weight="bold")
fig.savefig(f"{OUT}/estados-checkout.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------- Sesion ----------------
fig, ax = plt.subplots(figsize=(10, 4.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 4.4); ax.axis("off")
caja(ax, 1.5, 2.6, "E0 Sin sesión\n(login)", w=2.2)
caja(ax, 5.0, 2.6, "E1 Autenticado\n(cookie session-username)", w=2.8)
caja(ax, 8.5, 2.6, "E2 Sesión cerrada\n(login)", w=2.2)
flecha(ax, (2.6, 2.75), (3.6, 2.75), "login válido", dy=0.3)
flecha(ax, (6.4, 2.75), (7.4, 2.75), "Logout", dy=0.3)
flecha(ax, (8.5, 3.0), (5.0, 3.0), "login de nuevo", rad=0.35, dy=0.95)
flecha(ax, (1.5, 2.2), (1.5, 1.25), "", color="#8a5a00")
ax.text(1.5, 0.95, "credenciales inválidas / usuario bloqueado\n-> permanece en E0 con mensaje (CP-22 a CP-27)", ha="center", fontsize=8.5, color="#8a5a00")
flecha(ax, (8.5, 2.2), (8.5, 1.25), "", color="#b00020")
ax.text(8.2, 0.95, "URL protegida o botón Back\n-> debe volver al login (CP-08, CP-34, CP-36)", ha="center", fontsize=8.5, color="#b00020")
ax.set_title("Diagrama de transición de estados de la sesión", fontsize=13, weight="bold")
fig.savefig(f"{OUT}/estados-sesion.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------- Mapa mental ----------------
fig, ax = plt.subplots(figsize=(14, 9))
ax.set_xlim(-7, 7); ax.set_ylim(-4.6, 4.6); ax.axis("off")
ax.add_patch(FancyBboxPatch((-1.3, -0.4), 2.6, 0.8, boxstyle="round,pad=0.1", fc="#2f4b7c", ec="#2f4b7c"))
ax.text(0, 0, "SauceDemo\n(auditoría)", ha="center", va="center", fontsize=12, color="white", weight="bold")
ramas = [
    ("Login", (-4.6, 3.3), ["usuario y contraseña", "6 tipos de usuario", "mensajes de error", "usuario bloqueado", "tiempo de respuesta"]),
    ("Catálogo", (0, 3.7), ["6 productos", "imágenes y precios", "ordenar A-Z / Z-A", "ordenar por precio", "alineación visual"]),
    ("Detalle de producto", (4.6, 3.3), ["nombre, precio, imagen", "Add / Remove", "Back to products"]),
    ("Carrito", (-4.9, -0.2), ["Add to cart / Remove", "contador (badge)", "0 a 6 productos", "persistencia", "Continue Shopping"]),
    ("Checkout", (4.9, -0.2), ["datos del comprador", "validaciones de campos", "subtotal, impuesto 8 %, total", "Finish / Cancel", "carrito vacío"]),
    ("Menú", (-3.2, -3.6), ["All Items", "About", "Logout", "Reset App State"]),
    ("Control de acceso", (3.2, -3.6), ["URL protegidas sin sesión", "botón Back tras logout", "URL directa a pasos"]),
]
for nombre, (x, y), hojas in ramas:
    ax.plot([0, x], [0, y], color="#7a8fb3", lw=2, zorder=0)
    ax.add_patch(FancyBboxPatch((x - 1.2, y - 0.28), 2.4, 0.56, boxstyle="round,pad=0.08", fc="#e8eef7", ec="#2f4b7c", lw=1.5))
    ax.text(x, y, nombre, ha="center", va="center", fontsize=11, weight="bold")
    lado = 1 if x >= 0 else -1
    for i, h in enumerate(hojas):
        hy = y - 0.55 - i * 0.36 if y > 0 else y + 0.55 + (len(hojas) - 1 - i) * 0.36 if y < -2 else y - 0.55 - i * 0.36
        hx = x + lado * 0.2 + (1.6 if x == 0 else 0)
        ax.text(hx, hy, "- " + h, ha="center", va="center", fontsize=8.8, color="#333333",
                bbox=dict(fc="white", ec="none", pad=0.3))
ax.set_title("Mapa mental de módulos y escenarios de prueba", fontsize=14, weight="bold")
fig.savefig(f"{OUT}/mapa-mental.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("diagramas generados en", OUT)
