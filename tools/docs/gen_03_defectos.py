# Genera docs/03_Reporte_de_defectos.docx
import os
from datetime import datetime, timezone, timedelta
from collections import Counter
from doc_base import *  # noqa: F401,F403
from datos import BUGS, RAIZ, frecuencias
import json

VER = json.load(open(os.path.join(os.path.dirname(__file__), "verificacion_chrome.json"), encoding="utf8"))

freq = frecuencias()
COL = timezone(timedelta(hours=-5))


def hora_local(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(COL).strftime("%d/%m/%Y %I:%M %p")


doc = nuevo_documento()
portada(doc, "Reporte de defectos", "Entregable 3")
titulo(doc, "Reporte de defectos")

titulo(doc, "1. Introducción", 2)
parrafo(doc, f"Este documento reúne los {len(BUGS)} defectos encontrados en SauceDemo durante la auditoría. Todos se "
        "observaron en la sesión exploratoria y se reproducen con una prueba automatizada que afirma el comportamiento esperado y falla mientras "
        "el defecto exista. Cada prueba se ejecutó tres veces en Chromium y tres veces en Firefox; la frecuencia que aparece "
        "en cada ficha sale de esos resultados (archivos resultados-ejecucion-1.json a resultados-ejecucion-3.json).")
parrafo(doc, "El entorno común de todos los defectos es: Windows 11 Home 10.0.26200, Chromium 159.0.8154.6 y Firefox 159.0 "
        "controlados por Playwright 1.65.1, aplicación pública https://www.saucedemo.com y contraseña secret_sauce para "
        "todos los usuarios. La hora indicada en cada ficha es la de la tercera ejecución en Chromium (hora de Colombia).")

titulo(doc, "2. Severidad y prioridad", 2)
parrafo(doc, "La severidad mide qué tanto daño hace el defecto al funcionamiento del sistema: es crítica si bloquea un flujo "
        "de negocio sin alternativa, alta si una función importante no sirve o da datos incorrectos, media si la función "
        "falla pero existe otra forma de lograr el objetivo, y baja si es un problema estético o menor. La prioridad, en "
        "cambio, indica qué tan pronto se debe corregir según el negocio. Por eso no siempre coinciden: el login lento de "
        "BUG-11 tiene severidad media porque la aplicación funciona, pero prioridad alta porque cada cliente lo sufre al "
        "entrar; y un desalineado visual como BUG-13 es de severidad baja y prioridad baja.")

titulo(doc, "3. Fichas de defectos", 2)
for b in BUGS:
    f = freq[b["caso"]]
    v = VER["bugs"][b["id"]]
    titulo(doc, f"{b['id']}. {b['titulo']}", 3)
    filas = [
        ("ID", b["id"]),
        ("Módulo", b["modulo"]),
        ("Usuario y entorno", f"{b['usuario']}. Windows 11, Chromium 159 y Firefox 159 (Playwright 1.65.1). {hora_local(f['hora'])}"),
        ("Descripción", b["descripcion"]),
        ("Precondiciones", b["precondiciones"]),
        ("Pasos para reproducir", " ".join(f"{i}. {p}" for i, p in enumerate(b["pasos"], 1))),
        ("Resultado esperado", b["esperado"]),
        ("Resultado obtenido", b["obtenido"]),
        ("Evidencia", f"evidencias/capturas/{b['id']}.png (defecto marcado en rojo), evidencias/videos/{b['id']}.webm, "
                      "traza y registro de consola/red adjuntos en el reporte HTML de Playwright"),
        ("Severidad", b["severidad"]),
        ("Prioridad", b["prioridad"]),
        ("Justificación", b["justificacion"]),
        ("Frecuencia", f"Chromium {f['chromium']}/3 y Firefox {f['firefox']}/3 ejecuciones automatizadas. También se observó en la sesión exploratoria."),
        ("Reproducción manual",
         f"Verificado en {VER['navegador']} mediante navegación asistida (una IA, Claude, maneja el navegador real con la "
         f"extensión Claude in Chrome; el inicio de sesión lo hace una persona del equipo), {v['hora']}, {v['veces']} "
         f"reproducciones. Evidencia: {os.path.basename(v['captura'])}. Consola: {v['consola']}. {v['observacion']}"),
        ("Verificación por el equipo", "PENDIENTE"),
        ("Caso de prueba", b["caso"]),
        ("Test automatizado", b["test"]),
    ]
    if f["chromium"] != 3 or f["firefox"] != 3:
        raise SystemExit(f"{b['id']} no fallo 3/3: {f}")
    t = tabla(doc, ["Campo", "Detalle"], filas, anchos=[3.5, 13], tam=9)
    cap = os.path.join(RAIZ, "evidencias", "capturas", f"{b['id']}.png")
    figura(doc, cap, f"Evidencia {b['id']} (Playwright, Chromium 159)", ancho_cm=13)
    figura(doc, os.path.join(RAIZ, v["captura"]), f"Evidencia {b['id']} (Brave 157, navegación asistida)", ancho_cm=13)

titulo(doc, "4. Verificación en navegador real", 2)
parrafo(doc, "Además de las pruebas automatizadas, cada defecto se repitió dos veces en un navegador real (Brave 157, basado "
        "en Chromium 157) el 16/11/2026. Para que quede claro quién hizo qué: los pasos los ejecutó una IA (Claude) "
        "manejando el navegador con la extensión Claude in Chrome, y una persona del equipo escribió la contraseña en cada "
        "inicio de sesión y aceptó las alertas nativas. Antes de cada defecto se cerró sesión y se usó Reset App State. "
        "Los 19 defectos se reprodujeron 2 de 2 veces. El registro completo está en evidencias/capturas/manual/registro.txt. "
        "El campo «Verificación por el equipo» queda PENDIENTE hasta que una persona repita los pasos con la Guía de verificación.")
tabla(doc, ["Bug", "¿Se reprodujo?", "Veces", "Errores de consola"],
      [(b["id"], "Sí", VER["bugs"][b["id"]]["veces"], VER["bugs"][b["id"]]["consola"]) for b in BUGS],
      anchos=[2, 2.5, 1.5, 10.5], tam=8, titulo_tabla="Tabla 1. Verificación en Brave 157")
parrafo(doc, "Matices observados: en BUG-18 la página se ve normal porque el servidor responde 404 y luego redirige a "
        "/?/ruta con 200, así que el defecto solo se ve en la pestaña Red; en BUG-11 el tiempo medido fue 5022 ms y 10 039 ms "
        "frente a 18 ms de standard_user; y en la página de confirmación el sitio público ahora muestra el botón "
        "«Generate PDF order», que en la auditoría inicial no aparecía.")

titulo(doc, "5. Hallazgo descartado", 2)
parrafo(doc, "Durante la exploración se observó que, después de recargar la página, cerrar sesión y pulsar el botón Back del "
        "navegador, el catálogo seguía visible. Al repetirlo como prueba formal (CP-36) en Chromium y Firefox la aplicación "
        "regresó siempre al login con el mensaje de acceso restringido, por lo que el comportamiento no se pudo reproducir "
        "de forma consistente. Siguiendo la regla de la auditoría (si no se reproduce, no es bug) no se reporta como defecto "
        "y queda como riesgo para revisar manualmente.")

titulo(doc, "6. Resumen", 2)
orden = ["Crítica", "Alta", "Media", "Baja"]
cs = Counter(b["severidad"] for b in BUGS)
cp = Counter(b["prioridad"] for b in BUGS)
tabla(doc, ["Severidad", "Cantidad", "Bugs"],
      [(s, cs[s], ", ".join(b["id"] for b in BUGS if b["severidad"] == s)) for s in orden] + [("Total", len(BUGS), "")],
      anchos=[3, 2.5, 11], titulo_tabla="Tabla 5. Defectos por severidad")
tabla(doc, ["Prioridad", "Cantidad"], [(p, cp[p]) for p in ["Alta", "Media", "Baja"]] + [("Total", len(BUGS))],
      anchos=[4, 3], titulo_tabla="Tabla 5. Defectos por prioridad")
modulos = ["Login", "Catálogo", "Detalle de producto", "Carrito", "Checkout", "Menú", "Control de acceso"]
filas = []
for m in modulos:
    bm = [b for b in BUGS if b["modulo"] == m]
    c = Counter(b["severidad"] for b in bm)
    filas.append((m, *[c[s] for s in orden], len(bm)))
filas.append(("Total", *[cs[s] for s in orden], len(BUGS)))
tabla(doc, ["Módulo", "Crítica", "Alta", "Media", "Baja", "Total"], filas, anchos=[4.5, 2, 2, 2, 2, 2],
      titulo_tabla="Tabla 5. Defectos por módulo y severidad")
usuarios = Counter("Todos los usuarios" if ("(todos)" in b["usuario"] or " y " in b["usuario"]) else b["usuario"] for b in BUGS)
tabla(doc, ["Usuario", "Defectos"], sorted(usuarios.items(), key=lambda x: -x[1]), anchos=[6, 3],
      titulo_tabla="Tabla 5. Defectos por usuario")

guardar(doc, "03_Reporte_de_defectos.docx")
