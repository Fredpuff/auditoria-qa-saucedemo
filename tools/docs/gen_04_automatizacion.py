# Genera docs/04_Automatizacion.docx
import json
import os
from doc_base import *  # noqa: F401,F403
from datos import CASOS, BUGS, RAIZ, resultados_playwright, estado_caso, frecuencias

estados, stats, dur = resultados_playwright()
freq = frecuencias()
corridas = []
for i in (1, 2, 3):
    r = json.load(open(os.path.join(RAIZ, f"evidencias/reportes/resultados-ejecucion-{i}.json"), encoding="utf8"))
    corridas.append((i, r["stats"]["expected"], r["stats"]["unexpected"], r["stats"]["flaky"], round(r["stats"]["duration"] / 1000, 1)))
auto = [c for c in CASOS if c["auto"] == "Sí"]
tiempos = json.load(open(os.path.join(RAIZ, "evidencias/reportes/tiempos-login.json"), encoding="utf8"))

JUSTIF = {
    "@smoke": "Smoke y crítico: verifica que lo básico funciona antes de todo lo demás.",
    "TD": "Muchos datos: una sola prueba recorre todas las reglas leyendo el JSON.",
    "VL": "Repetitivo y propenso a error humano (contar productos, calcular impuestos).",
    "TE": "Crítico y de regresión: protege el flujo de compra y el control de acceso.",
    "PE": "Regresión: el mismo flujo se repite con varios usuarios y detecta el defecto en segundos.",
    "N": "Estable y repetitivo: los mensajes de error no cambian y se verifican igual cada vez.",
    "P": "Regresión de funciones principales; estable.",
}


def justificacion(c):
    if c["id"] in ("CP-01", "CP-05", "CP-02", "CP-38"):
        return JUSTIF["@smoke"]
    return {"Tabla de decisión": JUSTIF["TD"], "Valores límite": JUSTIF["VL"], "Transición de estados": JUSTIF["TE"],
            "Predicción de errores": JUSTIF["PE"], "Negativa": JUSTIF["N"], "Positiva": JUSTIF["P"]}[c["tecnica"]]


doc = nuevo_documento()
portada(doc, "Automatización de pruebas", "Entregable 4")
titulo(doc, "Automatización de pruebas")

titulo(doc, "1. Herramienta y justificación", 2)
parrafo(doc, "Se escogió Playwright (@playwright/test) con TypeScript. En la Clase 8 trabajamos con Puppeteer y Jest; "
        "Playwright viene de la misma familia de herramientas (lo creó el mismo equipo que hizo Puppeteer) y usa ideas "
        "parecidas, pero trae su propio ejecutor de pruebas y más funciones listas para usar. La comparamos con Selenium "
        "y Cypress así:")
tabla(doc, ["Criterio", "Playwright", "Selenium WebDriver", "Cypress"], [
    ("Esperas", "Auto-wait en cada acción y en expect", "Esperas explícitas a mano", "Reintentos automáticos"),
    ("Navegadores", "Chromium, Firefox y WebKit con la misma API", "Todos, con drivers por separado", "Chromium y Firefox; WebKit experimental"),
    ("Evidencias", "Capturas, video y trace viewer integrados", "Requiere librerías extra", "Capturas y video"),
    ("Reportes", "HTML, JSON y JUnit integrados", "Depende del framework", "Requiere plugins"),
    ("Cobertura", "Acceso a page.coverage (V8) y a window.__coverage__", "No integrada", "Plugin de Istanbul"),
    ("Varias pestañas y dominios", "Sí", "Sí", "Limitado"),
    ("Curva de aprendizaje", "Baja (similar a Puppeteer visto en clase)", "Media", "Baja"),
], anchos=[3.5, 4.5, 4.2, 4.2], tam=8)

titulo(doc, "2. Arquitectura del framework", 2)
parrafo(doc, "El framework es híbrido: combina módulos con Page Object Model (POM) y datos externos en JSON "
        "(enfoque data-driven visto en la Clase 8). Cada página de la aplicación tiene una clase con sus selectores y "
        "acciones; las pruebas solo llaman a esos métodos, así que si la interfaz cambia se corrige en un solo lugar. "
        "Los usuarios, productos y tablas de decisión están en archivos JSON y las pruebas se generan recorriéndolos.")
tabla(doc, ["Archivo o carpeta", "Contenido"], [
    ("tests/pages/LoginPage.ts", "Campos de usuario y contraseña, botón y mensaje de error; método loginCompleto()."),
    ("tests/pages/InventoryPage.ts", "Productos, precios, imágenes, ordenamiento, contador del carrito y menú lateral."),
    ("tests/pages/CartPage.ts", "Productos del carrito, Checkout y Continue Shopping."),
    ("tests/pages/CheckoutPage.ts", "Formulario, Continue, Cancel, montos del resumen, Finish y confirmación."),
    ("tests/data/*.json", "usuarios.json, productos.json (precios oficiales), login-decision.json y checkout-decision.json."),
    ("tests/fixtures.ts", "Fixture automático que escucha page.on('console'), page.on('pageerror'), respuestas 4xx/5xx y alertas, y los adjunta al reporte; también recoge la cobertura."),
    ("tests/*.spec.ts", "login, inventario, carrito, checkout, regresion y defectos."),
    ("playwright.config.ts", "Chromium y Firefox, screenshot 'on', video y trace 'retain-on-failure', reportes html + json + junit, slowMo por variable de entorno."),
    (".github/workflows/tests.yml", "Integración continua: corre la suite y la cobertura en cada push y publica los reportes como artifacts."),
], anchos=[5, 11.5], tam=9)
parrafo(doc, "Los selectores usan los atributos data-test de la aplicación (configurados con testIdAttribute para usar "
        "getByTestId), getByRole y getByPlaceholder. No se usó XPath. Cada prueba lleva en el título su caso y, si "
        "aplica, su bug, por ejemplo: CP-44 | BUG-04 | escribir el apellido no debe cambiar el nombre con problem_user.")
parrafo(doc, "Ejemplo del enfoque data-driven (tabla de decisión del login):", sangria=False)
for linea in ["for (const r of reglas) {",
              "  test(`${r.id} | tabla de decision login ${r.regla}: ${r.condicion}`, async ({ page }) => {",
              "    const login = new LoginPage(page);",
              "    await login.abrir();",
              "    await login.ingresar(r.usuario, r.password);",
              "    if (r.esperado === 'acceso') await expect(page).toHaveURL(/inventory/);",
              "    else await expect(login.error).toHaveText(r.mensaje);",
              "  });",
              "}"]:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(linea)
    r.font.name = "Consolas"
    r.font.size = Pt(9)

titulo(doc, "3. Casos automatizados y criterios de selección", 2)
parrafo(doc, f"Se automatizaron {len(auto)} de los {len(CASOS)} casos diseñados. Se aplicaron los criterios de la Clase 8: "
        "automatizar lo repetitivo, lo de regresión, lo estable, lo crítico, lo que maneja muchos datos y las pruebas smoke.")
filas = [(c["id"], c["nombre"], c["tecnica"], c["spec"], estado_caso(c, estados), c["bug"] or "-", justificacion(c)) for c in auto]
tabla(doc, ["Caso", "Nombre", "Técnica", "Archivo", "Resultado", "Bug", "Justificación"], filas,
      anchos=[1.3, 3.8, 2.2, 2.3, 1.7, 1.4, 4.3], tam=7)
parrafo(doc, "Lo que no se automatizó y por qué:", sangria=False)
vinetas(doc, [
    ("Sesiones exploratorias: ", "su valor está en que una persona decide qué probar según lo que va viendo; se apoyaron con el script tools/exploracion.mjs solo para guardar capturas y registros."),
    ("CP-54 revisión visual en celular: ", "decidir si algo se ve bien es subjetivo; el script toma las capturas y una persona las revisa."),
    ("CP-55 accesibilidad con teclado: ", "requiere criterio humano sobre la experiencia; se ejecutó de forma manual con apoyo de capturas."),
    ("Usabilidad de mensajes y textos: ", "no hay un resultado esperado exacto que se pueda comparar."),
])

titulo(doc, "4. Instrucciones de ejecución", 2)
tabla(doc, ["Acción", "Comando"], [
    ("Instalar dependencias", "npm install"),
    ("Instalar navegadores", "npx playwright install chromium firefox"),
    ("Ejecutar toda la suite", "npm test"),
    ("Ver el reporte HTML", "npx playwright show-report evidencias/reportes/html"),
    ("Un solo caso", "npx playwright test -g \"CP-05\""),
    ("Navegador visible", "npx playwright test --headed --project=chromium"),
    ("Cámara lenta (slowMo)", "npm run test:lento   (SLOWMO=500, navegador visible)"),
    ("Solo smoke / solo defectos", "npm run test:smoke   /   npm run test:defectos"),
    ("Cobertura de código", "npm run app:prepare   y luego   npm run coverage"),
], anchos=[5, 11.5], tam=9)
parrafo(doc, "Requisitos: Node.js 20 o superior (Playwright 1.65 lo exige; se probó con Node 22.18.0) y conexión a internet. "
        "El README del repositorio tiene los mismos pasos.")

titulo(doc, "5. Resultados de la ejecución", 2)
parrafo(doc, f"La suite tiene {len(auto)} pruebas que se ejecutan en Chromium y en Firefox, es decir, {len(auto) * 2} "
        "ejecuciones por corrida. Se corrió tres veces seguidas sin reintentos (retries: 0). Los resultados fueron "
        "idénticos en las tres corridas:")
tabla(doc, ["Corrida", "Pasaron", "Fallaron", "Inestables", "Duración (s)"], corridas, anchos=[3, 3, 3, 3, 3])
chrom_ok = sum(1 for c in auto if estados[("chromium", c["id"])] == "passed")
parrafo(doc, f"Por navegador: {chrom_ok} pruebas pasaron y {len(auto) - chrom_ok} fallaron en Chromium, y el mismo "
        f"resultado se obtuvo en Firefox. Las {len(auto) - chrom_ok} pruebas fallidas corresponden una a una con los "
        f"{len(BUGS)} defectos documentados (BUG-01 a BUG-{len(BUGS):02d}); ninguna prueba falló por un error del script.")
figura(doc, "docs/img/terminal-ejecucion.png", "Figura 1. Salida de la terminal al final de la tercera corrida", ancho_cm=16.5)
figura(doc, "docs/img/reporte-html-general.png", "Figura 2. Reporte HTML de Playwright", ancho_cm=16)
figura(doc, "docs/img/reporte-html-detalle-BUG-10.png", "Figura 3. Detalle de una prueba fallida (CP-49 | BUG-10) con su error, captura, video y traza", ancho_cm=16)

titulo(doc, "6. Análisis de los fallos", 2)
filas = []
for b in BUGS:
    f = freq[b["caso"]]
    filas.append((b["caso"], b["id"], b["titulo"], f"{f['chromium']}/3", f"{f['firefox']}/3"))
tabla(doc, ["Caso", "Bug", "Motivo del fallo (defecto de la aplicación)", "Chromium", "Firefox"], filas,
      anchos=[1.5, 1.7, 9.5, 1.9, 1.9], tam=8)
parrafo(doc, "Medición de rendimiento (CP-50, tercera corrida en Chromium):", sangria=False)
tabla(doc, ["Usuario", "Tiempos (ms)", "Promedio (ms)", "Umbral"], [
    ("standard_user", ", ".join(map(str, tiempos["tiempos"]["standard_user"])), tiempos["promedio_standard"], "< 2000 ms"),
    ("performance_glitch_user", ", ".join(map(str, tiempos["tiempos"]["performance_glitch_user"])), tiempos["promedio_performance"], "< 2000 ms"),
], anchos=[4, 6.5, 3, 3])
parrafo(doc, "También se revisaron los registros de consola y red que el fixture adjunta a cada prueba. Con todos los "
        "usuarios aparece el mensaje \"Permissions policy violation: unload is not allowed in this document\" y la "
        "respuesta 404 de las páginas internas (BUG-18). Con error_user aparecen además las excepciones \"Failed to add "
        "item to the cart.\", \"Failed to remove item from cart.\", \"Cannot read properties of undefined (reading 'value')\" "
        "y \"cesetRart is not a function\", que explican los defectos BUG-08, BUG-09 y BUG-10.")

titulo(doc, "7. Integración continua", 2)
parrafo(doc, "El archivo .github/workflows/tests.yml define dos trabajos que corren en cada push: e2e instala las "
        "dependencias y los navegadores, ejecuta npm test y publica la carpeta de reportes como artifact; cobertura prepara "
        "la copia local instrumentada y publica el reporte de nyc. El trabajo e2e termina en rojo a propósito porque la "
        "aplicación tiene defectos reales; eso es justamente lo que debe avisar la integración continua.")

guardar(doc, "04_Automatizacion.docx")
