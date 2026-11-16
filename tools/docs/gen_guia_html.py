# Genera docs/Guia_de_verificacion.html: un solo archivo, sin internet, con las imagenes embebidas en base64.
# Uso: python tools/docs/gen_guia_html.py
import base64
import io
import json
import os
import re

from PIL import Image

from datos import BUGS, RAIZ

VER = json.load(open(os.path.join(os.path.dirname(__file__), "verificacion_chrome.json"), encoding="utf8"))
COV = json.load(open(os.path.join(RAIZ, "coverage/codigo/coverage-summary.json"), encoding="utf8"))["total"]
TIEMPOS = json.load(open(os.path.join(RAIZ, "evidencias/reportes/tiempos-login.json"), encoding="utf8"))
USUARIOS = ["standard_user", "locked_out_user", "problem_user", "performance_glitch_user", "error_user", "visual_user"]


def img64(ruta, ancho=640, calidad=72):
    im = Image.open(os.path.join(RAIZ, ruta)).convert("RGB")
    if im.width > ancho:
        im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=calidad, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def usuarios_de(texto):
    u = sorted(set(re.findall("|".join(USUARIOS), texto)), key=texto.find)
    return u or ["standard_user"]


bugs = []
for b in BUGS:
    v = VER["bugs"][b["id"]]
    bugs.append(dict(id=b["id"], titulo=b["titulo"], modulo=b["modulo"], usuarios=usuarios_de(b["usuario"]),
                     usuario_txt=b["usuario"], pre=b["precondiciones"], pasos=b["pasos"], esperado=b["esperado"],
                     obtenido=b["obtenido"], reconocer=v["observacion"], consola=v["consola"],
                     severidad=b["severidad"], prioridad=b["prioridad"], justificacion=b["justificacion"],
                     caso=b["caso"], hora=v["hora"], img=img64(v["captura"], 1000, 70),
                     ruta=v["captura"], playwright=f"evidencias/capturas/{b['id']}.png",
                     video=f"evidencias/videos/{b['id']}.webm"))

IMG = {
    "estados": img64("docs/img/estados-checkout.png", 900, 80),
    "reporte": img64("docs/img/reporte-html-general.png", 900, 75),
    "detalle": img64("docs/img/reporte-html-detalle-BUG-10.png", 900, 75),
    "cobertura": img64("docs/img/cobertura-resumen.png", 900, 75),
    "finish": img64("docs/img/cobertura-detalle-Finish.png", 900, 75),
}

DATOS = dict(bugs=bugs, cov={k: COV[k] for k in ("statements", "branches", "functions", "lines")},
             tiempos=TIEMPOS, navegador=VER["navegador"], fecha=VER["fecha"])

plantilla = open(os.path.join(os.path.dirname(__file__), "guia_plantilla.html"), encoding="utf8").read()
html = plantilla.replace("/*DATOS*/null", json.dumps(DATOS, ensure_ascii=False))
for k, v in IMG.items():
    html = html.replace(f"{{{{IMG_{k}}}}}", v)
c = COV
html = (html.replace("{{ST}}", f"{c['statements']['pct']:.2f}").replace("{{BR}}", f"{c['branches']['pct']:.2f}")
        .replace("{{FN}}", f"{c['functions']['pct']:.2f}").replace("{{LN}}", f"{c['lines']['pct']:.2f}")
        .replace("{{ST_N}}", f"{c['statements']['covered']} de {c['statements']['total']}")
        .replace("{{BR_N}}", f"{c['branches']['covered']} de {c['branches']['total']}")
        .replace("{{FN_N}}", f"{c['functions']['covered']} de {c['functions']['total']}")
        .replace("{{LN_N}}", f"{c['lines']['covered']} de {c['lines']['total']}")
        .replace("{{T_STD}}", str(TIEMPOS["promedio_standard"])).replace("{{T_PERF}}", str(TIEMPOS["promedio_performance"])))
assert "{{" not in html, re.findall(r"\{\{\w+\}\}", html)
salida = os.path.join(RAIZ, "docs", "Guia_de_verificacion.html")
open(salida, "w", encoding="utf8").write(html)
print("ok", salida, round(os.path.getsize(salida) / 1e6, 2), "MB")
