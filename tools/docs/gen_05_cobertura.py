# Genera docs/05_Cobertura.docx
import json
import os
from doc_base import *  # noqa: F401,F403
from datos import CASOS, REQUISITOS, RAIZ, resultados_playwright, estado_caso, cobertura_codigo

estados, stats, _ = resultados_playwright()
cov = cobertura_codigo()
if cov is None:
    raise SystemExit("Falta coverage/codigo/coverage-summary.json (ejecute npm run coverage)")
tot = cov["total"]

ejecutados = [c for c in CASOS if estado_caso(c, estados) in ("Aprobado", "Fallido")]
automatizados = [c for c in CASOS if c["auto"] == "Sí"]
req_cubiertos = [r for r in REQUISITOS if any(r[0] in c["rf"] and c in ejecutados for c in CASOS)]
pct = lambda a, b: f"{a / b * 100:.1f} %"

doc = nuevo_documento()
portada(doc, "Informe de cobertura", "Entregable 5")
titulo(doc, "Informe de cobertura")

titulo(doc, "1. Tres métricas distintas", 2)
parrafo(doc, "En este informe se reportan tres métricas que miden cosas diferentes y no se deben confundir. La cobertura de "
        "requisitos dice qué parte de lo que la aplicación debe hacer fue probada; la cobertura de casos dice qué parte de "
        "los casos diseñados se ejecutó y se automatizó; y la cobertura de código dice qué parte del código JavaScript de "
        "la aplicación se ejecutó mientras corrían nuestras pruebas.")
tabla(doc, ["Métrica", "Fórmula", "Resultado", "Herramienta / evidencia"], [
    ("a) Cobertura de requisitos", "requisitos con al menos un caso ejecutado / requisitos identificados x 100",
     f"{len(req_cubiertos)} / {len(REQUISITOS)} = {pct(len(req_cubiertos), len(REQUISITOS))}", "Matriz de trazabilidad (plan de pruebas y hoja Trazabilidad del Excel)"),
    ("b1) Casos ejecutados", "casos ejecutados / casos diseñados x 100", f"{len(ejecutados)} / {len(CASOS)} = {pct(len(ejecutados), len(CASOS))}", "02_Casos_de_prueba.xlsx, hoja Resumen"),
    ("b2) Casos automatizados", "casos automatizados / casos diseñados x 100", f"{len(automatizados)} / {len(CASOS)} = {pct(len(automatizados), len(CASOS))}", "Suite Playwright, resultados JSON"),
    ("c) Código: sentencias", "sentencias ejecutadas / sentencias totales", f"{tot['statements']['covered']} / {tot['statements']['total']} = {tot['statements']['pct']:.2f} %", "Istanbul + nyc, coverage/codigo/index.html"),
    ("c) Código: ramas", "ramas ejecutadas / ramas totales", f"{tot['branches']['covered']} / {tot['branches']['total']} = {tot['branches']['pct']:.2f} %", "Istanbul + nyc"),
    ("c) Código: funciones", "funciones llamadas / funciones totales", f"{tot['functions']['covered']} / {tot['functions']['total']} = {tot['functions']['pct']:.2f} %", "Istanbul + nyc"),
    ("c) Código: líneas", "líneas ejecutadas / líneas totales", f"{tot['lines']['covered']} / {tot['lines']['total']} = {tot['lines']['pct']:.2f} %", "Istanbul + nyc"),
], anchos=[3.5, 5, 3.6, 4.4], tam=8)
parrafo(doc, f"Las cuatro medidas de cobertura de código superan el 50 % pedido. La más baja es la de ramas "
        f"({tot['branches']['pct']:.2f} %), porque varias condiciones solo se cumplen en situaciones que las pruebas E2E no "
        "provocan (por ejemplo, el registro del service worker o la generación del recibo en PDF).")

titulo(doc, "2. Cobertura de requisitos", 2)
filas = []
for rid, mod, desc in REQUISITOS:
    cs = [c["id"] for c in CASOS if rid in c["rf"]]
    filas.append((rid, desc, ", ".join(cs), "Sí" if rid in [r[0] for r in req_cubiertos] else "No"))
tabla(doc, ["Req.", "Descripción", "Casos ejecutados", "Cubierto"], filas, anchos=[1.5, 7, 6, 2], tam=8)

titulo(doc, "3. Cobertura de casos", 2)
parrafo(doc, f"Se diseñaron {len(CASOS)} casos y se ejecutaron todos. De ellos {len(automatizados)} están automatizados en "
        f"Playwright y {len(CASOS) - len(automatizados)} son manuales (CP-54 y CP-55, revisión visual y de accesibilidad). "
        f"Las pruebas automatizadas se corrieron en Chromium y Firefox, tres veces cada una.")

titulo(doc, "4. Cobertura de código", 2)
titulo(doc, "4.1 Cómo se obtuvo", 3)
parrafo(doc, "Se usó la opción preferida del enunciado. El código fuente de SauceDemo es público en el repositorio "
        "saucelabs/sample-app-web de GitHub. Se clonó en el commit d5cd655 (5 de noviembre de 2026), se compiló con Vite "
        "agregando vite-plugin-istanbul para que cada sentencia del código lleve un contador, y se levantó en "
        "http://localhost:3000. Luego se ejecutó la misma suite de Playwright apuntando a esa dirección. Al final de cada "
        "prueba un fixture lee el objeto window.__coverage__ del navegador y lo guarda en la carpeta .nyc_output; como "
        "algunas pruebas recargan la página, los contadores se guardan también en sessionStorage antes de cada recarga para "
        "no perderlos. Por último nyc junta todos los archivos y genera el reporte HTML y el resumen.")
tabla(doc, ["Paso", "Comando"], [
    ("1. Clonar, instalar, instrumentar y compilar la app", "npm run app:prepare"),
    ("2. Correr la suite contra localhost y generar el reporte", "npm run coverage"),
    ("3. Abrir el reporte", "coverage/codigo/index.html"),
], anchos=[8.5, 8])
parrafo(doc, "Decisiones para no inflar el número:", sangria=False)
vinetas(doc, [
    "El código original trae 22 comentarios \"istanbul ignore\" (21 en archivos que se miden y 1 en la configuración de Jest) que sacan funciones del cálculo, entre ellas justo las funciones con los defectos de problem_user y error_user. El script de preparación los elimina para que ese código sí cuente.",
    "Los archivos de src que ninguna prueba cargó (src/pdf/OrderReceipt.jsx, src/service-worker.js y src/serviceWorkerRegistration.js) se agregan al reporte con 0 %, igual que hace nyc con la opción --all.",
    "Solo se excluyeron las pruebas unitarias propias de la aplicación (__tests__ y __mocks__), las historias de Storybook y los archivos de configuración de Jest, porque no son código de la aplicación sino herramientas de desarrollo.",
    "No se excluyó ninguna librería de la aplicación ni ningún archivo para subir el porcentaje. Las librerías de node_modules nunca entran porque el plugin solo instrumenta la carpeta src.",
])

titulo(doc, "4.2 Resultados por carpeta y archivo", 3)
filas = []
for ruta, d in sorted(cov.items()):
    if ruta == "total":
        continue
    nombre = ruta.replace("\\", "/").split("/src/")[-1]
    filas.append(("src/" + nombre, f"{d['statements']['pct']:.1f}", f"{d['branches']['pct']:.1f}", f"{d['functions']['pct']:.1f}", f"{d['lines']['pct']:.1f}"))
filas.append(("Total", f"{tot['statements']['pct']:.2f}", f"{tot['branches']['pct']:.2f}", f"{tot['functions']['pct']:.2f}", f"{tot['lines']['pct']:.2f}"))
tabla(doc, ["Archivo", "% Sentencias", "% Ramas", "% Funciones", "% Líneas"], filas, anchos=[7, 2.4, 2.4, 2.4, 2.4], tam=8)
figura(doc, "docs/img/cobertura-resumen.png", "Figura 1. Resumen del reporte de cobertura (nyc)", ancho_cm=16)
figura(doc, "docs/img/cobertura-pages.png", "Figura 2. Cobertura de la carpeta src/pages", ancho_cm=16)

titulo(doc, "4.3 Cómo leer el reporte", 3)
parrafo(doc, "El reporte funciona igual que el de Jest e Istanbul que usamos en el proyecto angular-testing. En la tabla "
        "principal cada barra se pinta de verde cuando el porcentaje es alto, amarillo cuando es medio y rojo cuando es "
        "bajo. Al abrir un archivo se ve su código fuente: las líneas en verde se ejecutaron al menos una vez durante las "
        "pruebas y las líneas en rojo nunca se ejecutaron. El número con una x a la izquierda de cada línea (por ejemplo "
        "\"1x\" o \"25x\") dice cuántas veces se ejecutó esa línea en total. Las marcas amarillas con una I o una E "
        "indican que el camino del if o del else de esa condición nunca se tomó.")
parrafo(doc, "Como ejemplo se abrió el archivo CheckOutStepOne.jsx (formulario del checkout). Allí se ven en verde las "
        "líneas de las validaciones \"First Name is required\", \"Last Name is required\" y \"Postal Code is required\", "
        "porque las tablas de decisión las recorren todas, y también las ramas de problem_user y error_user que causan "
        "BUG-04 y BUG-09. En el archivo Finish.jsx, en cambio, aparece en rojo la función que genera el recibo en PDF, "
        "porque ninguna prueba lo pulsa (en la verificación del 16/11/2026 se comprobó que el sitio público sí muestra el botón «Generate PDF order»).")
figura(doc, "docs/img/cobertura-detalle-CheckOutStepOne.png", "Figura 3. Detalle de CheckOutStepOne.jsx con contadores de ejecución", ancho_cm=16)
figura(doc, "docs/img/cobertura-detalle-Finish.png", "Figura 4. Detalle de Finish.jsx con líneas no cubiertas en rojo", ancho_cm=16)

titulo(doc, "5. Limitaciones", 2)
vinetas(doc, [
    "Se mide el código JavaScript del cliente (React). SauceDemo no tiene backend propio, así que no hay código de servidor que medir.",
    "El código del repositorio público puede no ser idéntico al desplegado en www.saucedemo.com. Por ejemplo, el botón para descargar el recibo en PDF no aparecía en el sitio público al inicio de la auditoría y sí aparece en la verificación del 16/11/2026. Por eso los resultados de las pruebas (pasa o falla) se toman del sitio público y la cobertura de la copia local.",
    "Contra la copia local la prueba de BUG-18 pasa, porque el servidor de Vite responde 200 en todas las rutas; este defecto es propio del servidor del sitio público. Las demás pruebas dan el mismo resultado en los dos entornos.",
    "La cobertura de código mide qué se ejecutó, no qué se verificó. Un porcentaje alto de líneas no significa que ese porcentaje del código esté libre de errores.",
    "La cobertura se midió solo con Chromium, porque el resultado no depende del navegador: el código instrumentado es el mismo.",
])

guardar(doc, "05_Cobertura.docx")
