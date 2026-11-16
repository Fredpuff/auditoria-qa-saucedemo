# Genera docs/07_Sustentacion.pptx (12 diapositivas, notas del orador repartidas entre los 2 integrantes)
import json
import os
from collections import Counter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt
from datos import CASOS, BUGS, REQUISITOS, RAIZ, CFG, INT1, INT2, resultados_playwright, estado_caso, cobertura_codigo

estados, stats, _ = resultados_playwright()
cov = cobertura_codigo()["total"]
est = {c["id"]: estado_caso(c, estados) for c in CASOS}
total, ok = len(CASOS), sum(1 for v in est.values() if v == "Aprobado")
ko = total - ok
sev = Counter(b["severidad"] for b in BUGS)
auto = sum(1 for c in CASOS if c["auto"] == "Sí")
tiempos = json.load(open(os.path.join(RAIZ, "evidencias/reportes/tiempos-login.json"), encoding="utf8"))
N1 = INT1.split(" ")[0]
N2 = INT2

AZUL = RGBColor(0x1E, 0x27, 0x61)
HIELO = RGBColor(0xCA, 0xDC, 0xFC)
ROJO = RGBColor(0xB0, 0x00, 0x20)
GRIS = RGBColor(0x52, 0x51, 0x4E)
NEGRO = RGBColor(0x1A, 0x1A, 0x1A)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
SUAVE = RGBColor(0xF1, 0xF4, 0xFA)
FUENTE = "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
img = lambda p: os.path.join(RAIZ, p)


def texto(sl, x, y, w, h, contenido, tam=16, color=NEGRO, negrita=False, alinear=PP_ALIGN.LEFT, ancla=MSO_ANCHOR.TOP):
    tb = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = ancla
    tf.margin_left = tf.margin_right = Inches(0.05)
    lineas = contenido if isinstance(contenido, list) else [contenido]
    for i, l in enumerate(lineas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinear
        p.space_after = Pt(6)
        r = p.add_run()
        r.text = l
        r.font.size, r.font.color.rgb, r.font.bold, r.font.name = Pt(tam), color, negrita, FUENTE
    return tb


def vinetas(sl, x, y, w, h, items, tam=16, color=NEGRO):
    tb = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(8)
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", "285750")
        pPr.set("indent", "-285750")
        bu = pPr.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}buChar", {"char": "•"})
        pPr.append(bu)
        if isinstance(it, tuple):
            r = p.add_run(); r.text = it[0]; r.font.bold = True
            r.font.size, r.font.color.rgb, r.font.name = Pt(tam), color, FUENTE
            r = p.add_run(); r.text = it[1]
        else:
            r = p.add_run(); r.text = it
        r.font.size, r.font.color.rgb, r.font.name = Pt(tam), color, FUENTE


def caja(sl, x, y, w, h, relleno=SUAVE):
    s = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = 0.08
    s.fill.solid(); s.fill.fore_color.rgb = relleno
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def dato(sl, x, y, w, numero, etiqueta, color=AZUL):
    caja(sl, x, y, w, 1.6)
    texto(sl, x, y + 0.15, w, 0.9, numero, tam=40, color=color, negrita=True, alinear=PP_ALIGN.CENTER)
    texto(sl, x, y + 1.0, w, 0.5, etiqueta, tam=13, color=GRIS, alinear=PP_ALIGN.CENTER)


def diapositiva(titulo, num, notas, oscura=False):
    sl = prs.slides.add_slide(BLANK)
    fondo = sl.background.fill
    fondo.solid(); fondo.fore_color.rgb = AZUL if oscura else BLANCO
    if titulo:
        texto(sl, 0.6, 0.4, 12.1, 0.9, titulo, tam=34, color=BLANCO if oscura else AZUL, negrita=True)
    texto(sl, 12.2, 7.0, 0.9, 0.35, str(num), tam=11, color=HIELO if oscura else GRIS, alinear=PP_ALIGN.RIGHT)
    sl.notes_slide.notes_text_frame.text = notas
    return sl


def foto(sl, ruta, x, y, w=None, h=None):
    if os.path.exists(img(ruta)):
        sl.shapes.add_picture(img(ruta), Inches(x), Inches(y), width=Inches(w) if w else None, height=Inches(h) if h else None)
    else:
        texto(sl, x, y, 4, 0.5, f"[falta {ruta}]", tam=12, color=ROJO)


# 1. Portada
sl = diapositiva("", 1, f"[{N1}] Buenos días. Somos {INT1} y {INT2}, de {CFG['consultora']}. Presentamos la auditoría de calidad "
                 "de la tienda SauceDemo. En diez minutos vamos a mostrar qué probamos, cómo lo probamos, qué defectos "
                 "encontramos, la automatización en vivo y nuestro concepto sobre si la aplicación puede salir a producción. "
                 f"Yo presento la estrategia, la automatización y la cobertura; {N2} presenta la aplicación, los resultados, "
                 "los defectos y el concepto final. (30 segundos)", oscura=True)
texto(sl, 0.8, 1.6, 11.5, 1.2, "Auditoría de calidad de SauceDemo", tam=44, color=BLANCO, negrita=True)
texto(sl, 0.8, 2.8, 11.5, 0.6, f"{CFG['consultora']}  |  Proyecto final - {CFG['asignatura']}", tam=20, color=HIELO)
texto(sl, 0.8, 4.3, 11.5, 1.6, [f"{INT1}", f"{INT2}", f"Docente: {CFG['docente']}"], tam=18, color=BLANCO)
texto(sl, 0.8, 6.2, 11.5, 0.5, f"{CFG['universidad']}  |  {CFG['fecha_texto']}", tam=14, color=HIELO)

# 2. Aplicacion y alcance
sl = diapositiva("La aplicación y el alcance", 2,
                 f"[{N2}] SauceDemo es una tienda de ejemplo de Sauce Labs. Tiene login, catálogo de seis productos, "
                 "ordenamiento, detalle, carrito y un checkout de tres pasos. Lo interesante es que trae seis usuarios de prueba "
                 "y varios tienen fallas reales, lo que nos permitió encontrar defectos sin inventar nada. Probamos siete módulos "
                 "en Chromium y Firefox. Dejamos por fuera pagos reales, carga, seguridad y backend porque no tenemos acceso ni "
                 "autorización. Como no hay requisitos escritos, el resultado esperado es lo que hace standard_user. (1 minuto)")
vinetas(sl, 0.6, 1.5, 5.9, 5.0, [
    ("Qué es: ", "tienda en línea de ejemplo (Swag Labs) con 6 usuarios de prueba"),
    ("Módulos: ", "login, catálogo, detalle, carrito, checkout, menú y control de acceso"),
    ("Navegadores: ", "Chromium 159 y Firefox 159"),
    ("Fuera de alcance: ", "pagos reales, carga, pentesting y backend"),
    ("Línea base: ", "el comportamiento de standard_user"),
], tam=16)
foto(sl, "evidencias/exploracion/standard_user-inventario.png", 6.9, 1.5, w=5.9)

# 3. Estrategia
sl = diapositiva("Estrategia: técnicas de caja negra", 3,
                 f"[{N1}] Usamos las técnicas de caja negra de la Clase 7. Cada cuadro muestra cuántos casos salieron de cada "
                 "técnica. Las tablas de decisión cubren el login y el formulario; la transición de estados cubre el checkout y "
                 "la sesión; la predicción de errores salió de las sesiones exploratorias con cada usuario. En total "
                 f"diseñamos {total} casos. (1 minuto)")
tecnicas = Counter(c["tecnica"] for c in CASOS)
orden = ["Positiva", "Negativa", "Valores límite", "Tabla de decisión", "Transición de estados", "Predicción de errores", "Exploratoria (manual)"]
for i, t in enumerate(orden):
    x = 0.6 + (i % 4) * 3.1
    y = 1.6 + (i // 4) * 2.4
    caja(sl, x, y, 2.85, 2.1)
    texto(sl, x, y + 0.2, 2.85, 0.9, str(tecnicas[t]), tam=40, color=AZUL, negrita=True, alinear=PP_ALIGN.CENTER)
    texto(sl, x, y + 1.15, 2.85, 0.8, t, tam=15, color=GRIS, alinear=PP_ALIGN.CENTER)
caja(sl, 0.6 + 3 * 3.1, 1.6 + 2.4, 2.85, 2.1, relleno=AZUL)
texto(sl, 0.6 + 3 * 3.1, 1.8 + 2.4, 2.85, 0.9, str(total), tam=40, color=BLANCO, negrita=True, alinear=PP_ALIGN.CENTER)
texto(sl, 0.6 + 3 * 3.1, 2.75 + 2.4, 2.85, 0.8, "casos diseñados", tam=15, color=HIELO, alinear=PP_ALIGN.CENTER)

# 4. Escenarios: tablas y estados
sl = diapositiva("Escenarios: tabla de decisión y estados", 4,
                 f"[{N1}] Para el login hicimos la tabla completa de usuario por contraseña: doce combinaciones que se reducen "
                 "a seis reglas, una prueba por regla. Para el checkout dibujamos este diagrama de estados. En rojo están las "
                 "transiciones inválidas: entrar sin sesión se bloquea bien, pero abrir la confirmación de compra por URL y "
                 "hacer checkout con el carrito vacío no se bloquean; esos son BUG-19 y BUG-14. (1 minuto)")
foto(sl, "docs/img/estados-checkout.png", 0.6, 1.4, w=8.2)
caja(sl, 9.2, 1.5, 3.5, 5.3)
texto(sl, 9.4, 1.65, 3.1, 0.5, "Tabla de decisión del login", tam=16, color=AZUL, negrita=True)
vinetas(sl, 9.4, 2.25, 3.2, 4.4, ["12 combinaciones", "6 reglas reducidas", "6 pruebas data-driven desde JSON",
                                  "Formulario de checkout: 8 combinaciones, 4 reglas", "Todas aprobadas"], tam=14)

# 5. Resultados generales
sl = diapositiva("Resultados generales", 5,
                 f"[{N2}] De {total} casos ejecutados, {ok} pasaron y {ko} fallaron, es decir el {ko / total * 100:.0f} % falló. "
                 f"Encontramos {len(BUGS)} defectos reales. La gráfica muestra que los fallos vienen sobre todo de la predicción "
                 "de errores, o sea de los usuarios con defectos, y de las validaciones del checkout. (1 minuto)")
dato(sl, 0.6, 1.5, 2.8, str(total), "casos ejecutados")
dato(sl, 0.6, 3.3, 2.8, str(ok), "aprobados")
dato(sl, 0.6, 5.1, 2.8, str(ko), "fallidos", color=ROJO)
foto(sl, "docs/img/grafico-tecnica.png", 3.8, 1.5, w=8.9)

# 6. Defectos criticos
sl = diapositiva("Defectos críticos: la compra se bloquea", 6,
                 f"[{N2}] Estos son los dos defectos críticos. A la izquierda, BUG-04 con problem_user: al escribir el "
                 "apellido, el texto cae en el nombre y el apellido queda vacío, así que no se puede seguir. A la derecha, "
                 "BUG-10 con error_user: el botón Finish no hace nada y la consola muestra cesetRart is not a function. En los "
                 "dos casos el cliente no puede comprar. Los dos fallaron tres de tres veces en ambos navegadores. (1 minuto)")
for i, b in enumerate(["BUG-04", "BUG-10"]):
    x = 0.6 + i * 6.25
    bug = next(z for z in BUGS if z["id"] == b)
    texto(sl, x, 1.35, 5.9, 0.9, [f"{b}: {bug['titulo']}"], tam=15, color=ROJO, negrita=True)
    foto(sl, f"evidencias/capturas/{b}.png", x, 2.3, h=4.4)

# 7. Otros defectos
sl = diapositiva(f"Defectos por severidad ({len(BUGS)} en total)", 7,
                 f"[{N2}] Además de los dos críticos hay {sev['Alta']} de severidad alta: botones de agregar que no responden "
                 "en la mitad de los productos con problem_user y error_user, detalles de producto equivocados, el apellido "
                 "que no se puede escribir y precios del catálogo que no son los que se cobran con visual_user. También medimos "
                 f"el login: performance_glitch_user tarda {tiempos['promedio_performance']} milisegundos en promedio contra "
                 f"{tiempos['promedio_standard']} de standard_user. (1 minuto)")
foto(sl, "docs/img/grafico-severidad.png", 0.6, 1.5, w=5.6)
altos = [b for b in BUGS if b["severidad"] == "Alta"]
vinetas(sl, 6.6, 1.5, 6.2, 4.0, [(f"{b['id']}: ", b["titulo"]) for b in altos], tam=14)
caja(sl, 6.6, 5.5, 6.1, 1.2)
texto(sl, 6.8, 5.6, 5.8, 1.0, [f"Login de performance_glitch_user: {tiempos['promedio_performance']} ms",
                               f"standard_user: {tiempos['promedio_standard']} ms  (umbral 2000 ms)"], tam=14, color=AZUL, negrita=True)

# 8. Automatizacion
sl = diapositiva("Automatización con Playwright", 8,
                 f"[{N1}] Automatizamos {auto} casos con Playwright y TypeScript usando Page Object Model y datos en JSON, el "
                 "enfoque híbrido de la Clase 8. Escogimos Playwright porque espera solo a los elementos, corre en varios "
                 "navegadores y guarda capturas, video y trazas. DEMO EN VIVO: correr npx playwright test -g \"CP-05|CP-49\" "
                 "--headed --project=chromium. Se ve la compra completa que pasa y la de error_user que falla en Finish. "
                 f"Luego abrir el reporte HTML. En las tres corridas: {stats['expected']} pasaron y {stats['unexpected']} "
                 "fallaron, y cada fallo es un bug. (2 minutos con la demo)")
vinetas(sl, 0.6, 1.5, 5.4, 3.4, [
    ("Framework: ", "POM + datos JSON (data-driven)"),
    ("Suite: ", f"{auto} pruebas x 2 navegadores"),
    ("Resultado (3 corridas iguales): ", f"{stats['expected']} pasan, {stats['unexpected']} fallan"),
    ("Cada fallo = ", "un bug documentado"),
    ("CI: ", "GitHub Actions en cada push"),
], tam=15)
caja(sl, 0.6, 5.1, 5.4, 1.6, relleno=AZUL)
texto(sl, 0.8, 5.2, 5.0, 1.4, ["Demo en vivo:", "npx playwright test -g \"CP-05|CP-49\"", "--headed --project=chromium"],
      tam=14, color=BLANCO)
foto(sl, "docs/img/reporte-html-general.png", 6.4, 1.5, w=6.4)

# 9. Cobertura
sl = diapositiva("Cobertura: tres métricas distintas", 9,
                 f"[{N1}] Medimos tres cosas distintas. Requisitos: los {len(REQUISITOS)} requisitos tienen al menos un caso "
                 f"ejecutado. Casos: ejecutamos todos y automatizamos {auto}. Código: clonamos el código público de SauceDemo, "
                 "lo compilamos con Istanbul y corrimos la misma suite contra esa copia. Llegamos a "
                 f"{cov['lines']['pct']:.1f} % de líneas y {cov['branches']['pct']:.1f} % de ramas, sin excluir código para "
                 "subir el número; al contrario, quitamos los comentarios istanbul ignore del código original. Verde significa "
                 "que la línea se ejecutó, rojo que no, y el 1x indica cuántas veces. (1 minuto)")
dato(sl, 0.6, 1.5, 2.9, f"{len(REQUISITOS)}/{len(REQUISITOS)}", "requisitos cubiertos")
dato(sl, 0.6, 3.3, 2.9, f"{auto}/{total}", "casos automatizados")
dato(sl, 0.6, 5.1, 2.9, f"{cov['lines']['pct']:.1f} %", "líneas de código")
foto(sl, "docs/img/cobertura-resumen.png", 3.9, 1.5, w=8.8)

# 10. Concepto final
sl = diapositiva("Concepto final: NO está lista para producción", 10,
                 f"[{N2}] Nuestro concepto es que no está lista. Hay {sev['Crítica']} defectos críticos y {sev['Alta']} altos, "
                 f"falló el {ko / total * 100:.0f} % de los casos y la compra está bloqueada para dos tipos de usuario. "
                 "Para cambiar el concepto a sí pedimos: cero críticos y cero altos, el flujo de compra en verde con todos los "
                 "usuarios, login en menos de dos segundos y precios iguales a los cobrados. (1 minuto)", oscura=True)
dato(sl, 0.6, 1.6, 2.6, str(sev["Crítica"]), "críticos", color=ROJO)
dato(sl, 3.4, 1.6, 2.6, str(sev["Alta"]), "severidad alta", color=ROJO)
dato(sl, 6.2, 1.6, 2.6, f"{ko / total * 100:.0f} %", "casos fallidos", color=ROJO)
dato(sl, 9.0, 1.6, 3.7, "2 de 6", "usuarios sin poder comprar", color=ROJO)
texto(sl, 0.6, 3.6, 12, 0.5, "Para cambiar el concepto a Sí:", tam=18, color=HIELO, negrita=True)
vinetas(sl, 0.6, 4.2, 12, 2.6, ["Cero defectos críticos y cero de severidad alta",
                                "Flujo de compra (CP-38 a CP-41) aprobado con todos los usuarios en Chromium y Firefox",
                                "Login en menos de 2000 ms y precios del catálogo iguales a los cobrados",
                                "Suite de regresión en verde en la integración continua tres veces seguidas"], tam=16, color=BLANCO)

# 11. Recomendaciones
sl = diapositiva("Recomendaciones priorizadas", 11,
                 f"[{N2}] Las recomendaciones van en orden de impacto en el negocio: primero que todos puedan comprar, luego "
                 "que el carrito funcione con todos los productos, después la información correcta de precios y productos, el "
                 "rendimiento, y al final las validaciones y detalles visuales. Y mantener nuestra suite en la integración "
                 "continua para detectar regresiones. (1 minuto)")
recs = [("1", "Desbloquear la compra", "Formulario y botón Finish (BUG-04, 09, 10)"),
        ("2", "Carrito para todos los productos", "Add to cart y Remove (BUG-03, 08)"),
        ("3", "Información correcta", "Precios y detalle (BUG-05, 12)"),
        ("4", "Login rápido", "Quitar la espera de 5 s (BUG-11)"),
        ("5", "Controlar el flujo", "Carrito vacío, URL directa, sesión (BUG-14, 15, 16, 19)"),
        ("6", "Regresión continua", "Suite Playwright en cada despliegue")]
for i, (n, t, d) in enumerate(recs):
    x = 0.6 + (i % 3) * 4.15
    y = 1.6 + (i // 3) * 2.6
    caja(sl, x, y, 3.9, 2.3)
    texto(sl, x + 0.2, y + 0.15, 0.8, 0.8, n, tam=32, color=AZUL, negrita=True)
    texto(sl, x + 0.2, y + 0.95, 3.5, 0.5, t, tam=17, color=NEGRO, negrita=True)
    texto(sl, x + 0.2, y + 1.45, 3.5, 0.8, d, tam=13, color=GRIS)

# 12. Cierre y preguntas
sl = diapositiva("Gracias. Preguntas", 12,
                 f"[{N1} y {N2}] Cierre: repositorio, documentos y reporte disponibles. Preguntas probables del docente:\n"
                 "1. ¿Por qué hay pruebas que fallan en la suite? Porque cada una afirma el comportamiento esperado y la "
                 "aplicación tiene un defecto real; falló 3 de 3 veces en los dos navegadores y está enlazada a su BUG.\n"
                 "2. ¿Cuál es la diferencia entre severidad y prioridad? Severidad es el daño técnico; prioridad es qué tan "
                 "rápido hay que arreglarlo. BUG-11 es severidad media y prioridad alta.\n"
                 f"3. ¿Cómo midieron la cobertura de código? Con el código público de SauceDemo compilado con Istanbul; la suite "
                 f"corre contra localhost y nyc arma el reporte. Líneas {cov['lines']['pct']:.1f} %, ramas {cov['branches']['pct']:.1f} %.\n"
                 "4. ¿Qué no automatizaron y por qué? La exploración, la revisión visual en celular y la accesibilidad, porque "
                 "requieren criterio humano.\n"
                 "5. ¿Por qué Playwright y no Selenium o Cypress? Auto-wait, varios navegadores con la misma API, trazas, video y "
                 "reportes integrados, y es de la misma familia que Puppeteer, que vimos en la Clase 8.", oscura=True)
texto(sl, 0.8, 2.2, 11.5, 1.0, "Gracias", tam=54, color=BLANCO, negrita=True)
texto(sl, 0.8, 3.4, 11.5, 0.6, "¿Preguntas?", tam=28, color=HIELO)
texto(sl, 0.8, 5.0, 11.5, 1.2, [f"Repositorio: {CFG['repositorio']}", f"{INT1}  |  {INT2}"], tam=16, color=BLANCO)

ruta = os.path.join(RAIZ, "docs", "07_Sustentacion.pptx")
prs.save(ruta)
print("ok", ruta, "diapositivas:", len(prs.slides))
