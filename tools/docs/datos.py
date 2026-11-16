# Datos compartidos por todos los generadores de documentos.
# Los estados (Aprobado/Fallido) NO se escriben a mano: se leen del resultado real de Playwright.
import json
import os
import re

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CFG = json.load(open(os.path.join(os.path.dirname(__file__), "config.json"), encoding="utf8"))

FECHA = CFG["fecha_ejecucion"]
INT1 = CFG["integrante_1"]
INT2 = CFG["integrante_2"]

# ---------------------------------------------------------------- requisitos
REQUISITOS = [
    ("RF-01", "Login", "Inicio de sesión con credenciales válidas"),
    ("RF-02", "Login", "Mensajes de error por campos vacíos o credenciales inválidas"),
    ("RF-03", "Login", "Bloqueo del usuario locked_out_user"),
    ("RF-04", "Login", "Tiempo de respuesta del inicio de sesión"),
    ("RF-05", "Catálogo", "Listado de 6 productos con imagen, nombre y precio correctos"),
    ("RF-06", "Catálogo", "Ordenamiento por nombre (A-Z y Z-A)"),
    ("RF-07", "Catálogo", "Ordenamiento por precio"),
    ("RF-08", "Detalle de producto", "Detalle del producto seleccionado"),
    ("RF-09", "Carrito", "Agregar y quitar productos"),
    ("RF-10", "Carrito", "Contador del carrito (badge)"),
    ("RF-11", "Carrito", "Ver el carrito y volver a comprar"),
    ("RF-12", "Checkout", "Formulario de datos del comprador con validaciones"),
    ("RF-13", "Checkout", "Cálculo de subtotal, impuesto (8 %) y total"),
    ("RF-14", "Checkout", "Finalizar la compra y vaciar el carrito"),
    ("RF-15", "Checkout", "Cancelar en cada paso del checkout"),
    ("RF-16", "Menú", "Cerrar sesión (Logout)"),
    ("RF-17", "Menú", "Reset App State"),
    ("RF-18", "Menú", "Enlace About"),
    ("RF-19", "Menú", "Opción All Items"),
    ("RF-20", "Control de acceso", "Protección de páginas internas sin sesión"),
    ("RF-21", "Control de acceso", "Control de transiciones del checkout (no saltar pasos)"),
    ("RF-22", "Visual", "Presentación visual consistente y adaptable a móvil"),
    ("RF-23", "Visual", "Accesibilidad básica (teclado y textos alternativos)"),
    ("RF-24", "Catálogo", "Dynamic Catalog del menú (carga diferida, spinner y slider)"),
]

# ---------------------------------------------------------------- defectos
# id, titulo, modulo, usuario, severidad, prioridad, caso, test
BUGS = json.load(open(os.path.join(os.path.dirname(__file__), "bugs.json"), encoding="utf8"))

# ---------------------------------------------------------------- casos
import sys  # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from casos import CASOS  # noqa: E402


def resultados_playwright(archivo="evidencias/reportes/resultados-ejecucion-3.json"):
    """Devuelve {(proyecto, CP-XX): estado} y estadisticas del JSON real de Playwright."""
    r = json.load(open(os.path.join(RAIZ, archivo), encoding="utf8"))
    estados = {}
    duraciones = {}

    def rec(s):
        for sp in s.get("specs", []):
            m = re.match(r"(CP-\d+)", sp["title"])
            for t in sp["tests"]:
                for res in t["results"]:
                    if m:
                        estados[(t["projectName"], m.group(1))] = res["status"]
                        duraciones[(t["projectName"], m.group(1))] = res["duration"]
        for h in s.get("suites", []):
            rec(h)

    for s in r["suites"]:
        rec(s)
    return estados, r["stats"], duraciones


def estado_caso(caso, estados):
    """Aprobado/Fallido segun la ejecucion real (Chromium). Los manuales usan su estado registrado."""
    if caso["auto"] == "Sí":
        st = estados.get(("chromium", caso["id"]))
        if st is None:
            raise SystemExit(f"No hay resultado automatizado para {caso['id']}")
        return "Aprobado" if st == "passed" else "Fallido"
    return caso["estado_manual"]


def frecuencias():
    """{CP-XX: {'chromium': fallos/3, 'firefox': fallos/3, 'hora': inicio en la ejecucion 3}}"""
    out = {}
    for i in (1, 2, 3):
        r = json.load(open(os.path.join(RAIZ, f"evidencias/reportes/resultados-ejecucion-{i}.json"), encoding="utf8"))

        def rec(s):
            for sp in s.get("specs", []):
                m = re.match(r"(CP-\d+)", sp["title"])
                if not m:
                    continue
                for t in sp["tests"]:
                    for res in t["results"]:
                        d = out.setdefault(m.group(1), {"chromium": 0, "firefox": 0})
                        if res["status"] != "passed":
                            d[t["projectName"]] += 1
                        if i == 3 and t["projectName"] == "chromium":
                            d["hora"] = res["startTime"]
            for h in s.get("suites", []):
                rec(h)

        for s in r["suites"]:
            rec(s)
    return out


def cobertura_codigo():
    p = os.path.join(RAIZ, "coverage", "codigo", "coverage-summary.json")
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf8"))
