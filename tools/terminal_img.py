# Convierte la salida real de la consola (archivo de texto) en una imagen tipo terminal para los documentos.
# Uso: python tools/terminal_img.py <entrada.txt> <salida.png> [lineas_finales]
import re
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

entrada, salida = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 45
texto = open(entrada, encoding="utf8", errors="replace").read()
texto = re.sub(r"\x1b\[[0-9;]*m", "", texto)
lineas = [l.rstrip()[:150] for l in texto.splitlines()]
filtro = [l for l in lineas if l.strip()]
# se toman las ultimas lineas (lista de fallidos y totales)
sel = filtro[-n:]
alto = 0.19 * len(sel) + 0.4
fig = plt.figure(figsize=(14, alto))
fig.patch.set_facecolor("#1e1e1e")
for i, l in enumerate(sel):
    color = "#f48771" if ("failed" in l or "✘" in l) else ("#89d185" if ("passed" in l or "✓" in l) else "#d4d4d4")
    fig.text(0.01, 1 - (i + 1) / (len(sel) + 1), l, family="Consolas", fontsize=8.5, color=color, va="center")
fig.savefig(salida, dpi=130, facecolor=fig.get_facecolor())
print("ok", salida)
