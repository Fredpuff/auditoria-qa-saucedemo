# Genera docs/06_Informe_final_auditoria.docx
import json
import os
from collections import Counter
from doc_base import *  # noqa: F401,F403
from datos import CASOS, BUGS, REQUISITOS, RAIZ, CFG, resultados_playwright, estado_caso, cobertura_codigo

estados, stats, _ = resultados_playwright()
cov = cobertura_codigo()["total"]
est = {c["id"]: estado_caso(c, estados) for c in CASOS}
total = len(CASOS)
ok = sum(1 for v in est.values() if v == "Aprobado")
ko = sum(1 for v in est.values() if v == "Fallido")
sev = Counter(b["severidad"] for b in BUGS)
auto = [c for c in CASOS if c["auto"] == "Sí"]
pct = lambda a, b: f"{a / b * 100:.1f} %"
tiempos = json.load(open(os.path.join(RAIZ, "evidencias/reportes/tiempos-login.json"), encoding="utf8"))

doc = nuevo_documento()
portada(doc, "Informe final de auditoría de calidad", f"Cliente: Sauce Labs (aplicación SauceDemo / Swag Labs)")
titulo(doc, "Informe final de auditoría de calidad")

titulo(doc, "2. Resumen ejecutivo", 2)
parrafo(doc, f"{CFG['consultora']} realizó una auditoría de calidad funcional a la tienda en línea SauceDemo, con "
        f"ejecución final el {CFG['fecha_texto']}. Se evaluaron siete módulos "
        f"(login, catálogo, detalle de producto, carrito, checkout, menú y control de acceso) con los seis usuarios "
        f"de prueba que ofrece la aplicación, en los navegadores Chromium y Firefox.")
parrafo(doc, f"Se diseñaron y ejecutaron {total} casos de prueba: {ok} aprobados ({pct(ok, total)}) y {ko} fallidos "
        f"({pct(ko, total)}). Se documentaron {len(BUGS)} defectos reales: {sev['Crítica']} críticos, {sev['Alta']} de "
        f"severidad alta, {sev['Media']} de severidad media y {sev['Baja']} de severidad baja. {len(auto)} casos quedaron "
        f"automatizados con Playwright y se ejecutaron tres veces en cada navegador con el mismo resultado. La cobertura "
        f"de código alcanzada por las pruebas es de {cov['lines']['pct']:.2f} % de líneas y {cov['branches']['pct']:.2f} % de ramas.")
parrafo(doc, "El hallazgo más grave es que el flujo de compra, que es la razón de ser de la tienda, queda bloqueado para "
        "dos de los seis tipos de usuario: con problem_user no se puede llenar el apellido (BUG-04) y con error_user el "
        "botón Finish no cierra la compra (BUG-10). A esto se suman productos que no se pueden agregar al carrito, "
        "detalles de producto equivocados y precios mostrados que no coinciden con lo que se cobra.")
parrafo(doc, "Concepto final: la aplicación NO está lista para producción. Las razones y los criterios para cambiar este "
        "concepto se explican en la sección 10.", negrita_inicio="")

titulo(doc, "3. Aplicación y funcionalidades evaluadas", 2)
parrafo(doc, "SauceDemo (Swag Labs) es una tienda de ejemplo publicada por Sauce Labs en https://www.saucedemo.com. "
        "Permite iniciar sesión, ver un catálogo de seis productos, ordenarlos, ver el detalle de cada uno, armar un "
        "carrito y hacer un checkout de tres pasos (información del comprador, resumen con impuesto del 8 % y "
        "confirmación). Tiene un menú lateral con All Items, Dynamic Catalog, About, Logout y Reset App State. Todos los "
        "datos se guardan en el navegador: una cookie con el usuario y el carrito en localStorage.")
tabla(doc, ["Módulo", "Funciones evaluadas", "Casos"], [
    (m, d, sum(1 for c in CASOS if c["modulo"] == m)) for m, d in [
        ("Login", "credenciales, mensajes, bloqueo, tiempo de respuesta"),
        ("Catálogo", "productos, imágenes, precios, ordenamiento, Dynamic Catalog, alineación"),
        ("Detalle de producto", "información del producto seleccionado"),
        ("Carrito", "agregar, quitar, contador, persistencia, Reset App State"),
        ("Checkout", "formulario, validaciones, cálculo, finalizar, cancelar, transiciones"),
        ("Menú", "All Items, About, Logout"),
        ("Control de acceso", "URL protegidas, botón Back, respuestas HTTP"),
    ]], anchos=[4, 10, 2])

titulo(doc, "4. Metodología", 2)
parrafo(doc, "La auditoría se hizo con técnicas de caja negra porque se evaluó la aplicación desde la interfaz, como la "
        "usa un cliente: pruebas positivas y negativas, valores límite, tablas de decisión (login y formulario de "
        "checkout), transición de estados (checkout y sesión), predicción de errores y sesiones exploratorias con cada "
        "tipo de usuario guiadas por un mapa mental. Como no existen requisitos escritos, el resultado esperado se tomó "
        "del comportamiento de standard_user y de lo que indica la propia interfaz.")
tabla(doc, ["Elemento", "Detalle"], [
    ("Herramientas", "Playwright 1.65.1 con TypeScript, Page Object Model y datos en JSON; Istanbul (vite-plugin-istanbul) y nyc para cobertura; GitHub Actions para integración continua."),
    ("Entorno", "Windows 11, Node.js 22.18.0, Chromium 159.0.8154.6 y Firefox 159.0."),
    ("Repetición", "Cada prueba automatizada se ejecutó 3 veces por navegador sin reintentos."),
    ("Evidencias", "Capturas con el defecto marcado, videos, trazas de Playwright y registros de consola y red."),
], anchos=[3.5, 13])

titulo(doc, "5. Resultados generales", 2)
tecnicas = ["Positiva", "Negativa", "Valores límite", "Tabla de decisión", "Transición de estados", "Predicción de errores", "Exploratoria (manual)"]
filas = []
for t in tecnicas:
    cs = [c for c in CASOS if c["tecnica"] == t]
    a = sum(1 for c in cs if est[c["id"]] == "Aprobado")
    filas.append((t, len(cs), a, len(cs) - a, pct(a, len(cs))))
filas.append(("Total", total, ok, ko, pct(ok, total)))
tabla(doc, ["Técnica", "Casos", "Aprobados", "Fallidos", "% aprobados"], filas, anchos=[5, 2.5, 2.5, 2.5, 3],
      titulo_tabla="Tabla 1. Resultados por técnica")
figura(doc, "docs/img/grafico-tecnica.png", "Figura 1. Casos aprobados y fallidos por técnica", ancho_cm=15)
filas = []
for m in ["Login", "Catálogo", "Detalle de producto", "Carrito", "Checkout", "Menú", "Control de acceso"]:
    cs = [c for c in CASOS if c["modulo"] == m]
    a = sum(1 for c in cs if est[c["id"]] == "Aprobado")
    filas.append((m, len(cs), a, len(cs) - a, pct(a, len(cs))))
filas.append(("Total", total, ok, ko, pct(ok, total)))
tabla(doc, ["Módulo", "Casos", "Aprobados", "Fallidos", "% aprobados"], filas, anchos=[5, 2.5, 2.5, 2.5, 3],
      titulo_tabla="Tabla 2. Resultados por módulo")
figura(doc, "docs/img/grafico-modulo.png", "Figura 2. Casos aprobados y fallidos por módulo", ancho_cm=15)
parrafo(doc, "Con standard_user todos los casos funcionales pasaron, salvo los de validación y control de estados "
        "(BUG-14 a BUG-19). Los fallos se concentran en el catálogo y el checkout, y en los usuarios problem_user, "
        "error_user y visual_user.")

titulo(doc, "6. Principales defectos e impacto en el negocio", 2)
figura(doc, "docs/img/grafico-severidad.png", "Figura 3. Defectos por severidad", ancho_cm=12)
top = sorted(BUGS, key=lambda b: (["Crítica", "Alta", "Media", "Baja"].index(b["severidad"]), ["Alta", "Media", "Baja"].index(b["prioridad"])))[:5]
impacto = {
    "BUG-04": "Ningún cliente con este perfil puede comprar. Pérdida total de ventas en ese segmento.",
    "BUG-10": "La compra no se cierra en el último paso; el cliente cree que compró o abandona. Pérdida de ventas y reclamos.",
    "BUG-03": "La mitad del catálogo no se puede comprar o no se puede sacar del carrito.",
    "BUG-05": "El cliente ve la información de otro producto y puede comprar algo que no quería; un producto queda inaccesible.",
    "BUG-08": "La mitad del catálogo no se puede comprar; además hay errores no controlados en el código.",
    "BUG-09": "Se crean pedidos sin el apellido del comprador; los datos de envío quedan incompletos.",
    "BUG-12": "El precio mostrado no es el cobrado; riesgo legal de protección al consumidor y pérdida de confianza.",
}
tabla(doc, ["Bug", "Defecto", "Severidad / prioridad", "Impacto en el negocio"],
      [(b["id"], b["titulo"], f"{b['severidad']} / {b['prioridad']}", impacto.get(b["id"], b["justificacion"])) for b in top],
      anchos=[1.6, 5, 2.6, 7.3], tam=9, titulo_tabla="Tabla 3. Cinco defectos más graves")
for b in top[:2]:
    figura(doc, f"evidencias/capturas/{b['id']}.png", f"Evidencia {b['id']}. {b['titulo']}", ancho_cm=12)

titulo(doc, "7. Resultados de automatización y cobertura", 2)
parrafo(doc, f"Se automatizaron {len(auto)} de {total} casos ({pct(len(auto), total)}). En la última corrida se "
        f"ejecutaron {stats['expected'] + stats['unexpected']} pruebas (las {len(auto)} en dos navegadores): "
        f"{stats['expected']} pasaron y {stats['unexpected']} fallaron, en {stats['duration'] / 1000:.0f} segundos. "
        f"Cada uno de los {len(BUGS)} defectos tiene una prueba que falla por él en los dos navegadores y en las tres "
        f"corridas; no hubo pruebas inestables.")
req_cub = [r for r in REQUISITOS if any(r[0] in c["rf"] for c in CASOS)]
tabla(doc, ["Métrica", "Resultado"], [
    ("Cobertura de requisitos", f"requisitos con al menos un caso ejecutado / requisitos identificados x 100 = "
                                f"{len(req_cub)} / {len(REQUISITOS)} x 100 = {pct(len(req_cub), len(REQUISITOS))}"),
    ("Casos ejecutados / diseñados", f"{total} de {total} (100,0 %)"),
    ("Casos automatizados / diseñados", f"{len(auto)} de {total} ({pct(len(auto), total)})"),
    ("Cobertura de código: sentencias", f"{cov['statements']['pct']:.2f} %"),
    ("Cobertura de código: ramas", f"{cov['branches']['pct']:.2f} %"),
    ("Cobertura de código: funciones", f"{cov['functions']['pct']:.2f} %"),
    ("Cobertura de código: líneas", f"{cov['lines']['pct']:.2f} %"),
    ("Tiempo de login (promedio de 5)", f"standard_user {tiempos['promedio_standard']} ms; performance_glitch_user {tiempos['promedio_performance']} ms"),
    ("Verificación en navegador real", f"{len(BUGS)} de {len(BUGS)} defectos reproducidos 2/2 en Brave 157 (navegación asistida por IA); verificación por el equipo: PENDIENTE"),
], anchos=[7, 9])

titulo(doc, "8. Riesgos pendientes", 2)
vinetas(doc, [
    "No se probaron pagos reales, carga, seguridad ni backend porque están fuera del alcance (ver plan de pruebas).",
    "No se probó en Safari (WebKit) ni en celulares físicos; la vista móvil se revisó con emulación.",
    "El comportamiento del botón Back después de cerrar sesión se vio una vez en la exploración pero no se pudo reproducir de forma consistente; conviene revisarlo con más tiempo.",
    "La reproducción manual de cada defecto en el navegador (3 de 3) queda como tarea del equipo antes de la entrega; la reproducción automatizada sí está completa.",
    "La aplicación es una demo que puede cambiar sin aviso; los resultados corresponden a la versión del 16 de noviembre de 2026.",
    "El código público usado para la cobertura puede diferir del desplegado (por ejemplo, el botón del recibo en PDF apareció en el sitio público después de medir la cobertura).",
])

titulo(doc, "9. Recomendaciones de mejora (priorizadas)", 2)
tabla(doc, ["Prioridad", "Recomendación", "Bugs"], [
    ("1", "Corregir los manejadores del formulario de checkout (Last Name) y la limpieza del carrito al finalizar, para que la compra se pueda completar con todos los usuarios.", "BUG-04, BUG-09, BUG-10"),
    ("2", "Corregir Add to cart y Remove para todos los productos y controlar las excepciones en lugar de dejarlas sin manejar.", "BUG-03, BUG-08"),
    ("3", "Mostrar siempre el precio oficial y el detalle correcto de cada producto.", "BUG-05, BUG-12"),
    ("4", "Eliminar la espera artificial del login y fijar un objetivo de tiempo de respuesta (menos de 2 s).", "BUG-11"),
    ("5", "Validar el estado del flujo: no permitir checkout con carrito vacío ni abrir la confirmación sin compra.", "BUG-14, BUG-19"),
    ("6", "Borrar el carrito al cerrar sesión o asociarlo al usuario; actualizar los botones al usar Reset App State.", "BUG-15, BUG-16"),
    ("7", "Corregir ordenamiento, imágenes y enlace About.", "BUG-01, BUG-02, BUG-06, BUG-07"),
    ("8", "Configurar el servidor para responder 200 en las rutas de la aplicación; validar el formato del código postal; corregir los estilos desalineados.", "BUG-13, BUG-17, BUG-18"),
    ("9", "Mantener la suite automatizada en la integración continua como prueba de regresión antes de cada despliegue.", "Todos"),
], anchos=[1.8, 11, 3.7], tam=9)

titulo(doc, "10. Concepto final", 2)
parrafo(doc, "¿La aplicación está lista para producción? No.", negrita_inicio="Respuesta: ")
parrafo(doc, f"La decisión se basa en los datos de la auditoría: hay {sev['Crítica']} defectos críticos y {sev['Alta']} "
        f"de severidad alta abiertos; el {pct(ko, total)} de los casos ejecutados falló; y el flujo principal de negocio "
        f"(completar una compra) está bloqueado para problem_user y error_user. Además, con visual_user se muestran precios "
        f"distintos a los que se cobran y con performance_glitch_user el ingreso tarda en promedio "
        f"{tiempos['promedio_performance']} ms frente a {tiempos['promedio_standard']} ms de standard_user. Aunque el "
        f"usuario estándar sí puede comprar, una tienda real no puede salir con fallas que impiden vender o que muestran "
        f"precios incorrectos a una parte de sus clientes.")
parrafo(doc, "Criterios de aceptación para cambiar el concepto a \"Sí\":", sangria=False)
vinetas(doc, [
    "Cero defectos críticos y cero defectos de severidad alta abiertos.",
    "El flujo de compra completo (CP-38 a CP-41) pasa con todos los usuarios habilitados para comprar, en Chromium y Firefox.",
    "Al menos el 95 % de los casos ejecutados aprobados y ningún defecto de severidad media sin plan de corrección.",
    "Tiempo promedio de login menor a 2000 ms para todos los usuarios.",
    "Precios del catálogo iguales a los cobrados en el resumen.",
    "La suite de regresión corre en verde en la integración continua en tres ejecuciones seguidas.",
])

referencias(doc)
guardar(doc, "06_Informe_final_auditoria.docx")
