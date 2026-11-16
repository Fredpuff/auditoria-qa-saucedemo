# Utilidades comunes para los documentos Word (python-docx).
# Formato: Times New Roman 12, interlineado 1.5, sangria de primera linea, sin adornos.
import os
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from datos import CFG, RAIZ

FUENTE = "Times New Roman"


def nuevo_documento():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)  # carta
    for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, lado, Cm(2.54))
    est = doc.styles["Normal"]
    est.font.name = FUENTE
    est.font.size = Pt(12)
    est.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
    pf = est.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(0)
    pf.space_before = Pt(0)
    for nivel, tam in ((1, 12), (2, 12), (3, 12)):
        h = doc.styles[f"Heading {nivel}"]
        h.font.name = FUENTE
        h.font.size = Pt(tam)
        h.font.bold = True
        h.font.italic = nivel == 3
        h.font.color.rgb = RGBColor(0, 0, 0)
        h.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
        rfonts = h.element.rPr.rFonts
        for att in ("w:ascii", "w:hAnsi", "w:cs"):
            rfonts.set(qn(att), FUENTE)
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.line_spacing = 1.5
        h.paragraph_format.keep_with_next = True
        h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if nivel == 1 else WD_ALIGN_PARAGRAPH.LEFT
    numeracion_paginas(sec)
    return doc


def numeracion_paginas(sec):
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run()
    for tipo, texto in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tipo)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = texto
        run._r.append(el)
    run.font.size = Pt(10)


def portada(doc, titulo, subtitulo=""):
    for _ in range(3):
        doc.add_paragraph()
    for texto, negrita in ((CFG["consultora"], True), ("", False), (titulo, True), (subtitulo, False), ("", False),
                           ("Auditoría de calidad de la aplicación web SauceDemo", False), ("", False), ("", False),
                           ("Presentado por:", False), (CFG["integrante_1"], False), (CFG["integrante_2"], False), ("", False),
                           ("Docente:", False), (CFG["docente"], False), ("", False), ("", False),
                           (CFG["universidad"], False), (CFG["programa"], False), (CFG["asignatura"], False),
                           (f"{CFG['ciudad']}, {CFG['fecha_texto']}", False)):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if texto:
            r = p.add_run(texto)
            r.bold = negrita
    salto(doc)


def salto(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def titulo(doc, texto, nivel=1):
    return doc.add_heading(texto, level=nivel)


def parrafo(doc, texto, sangria=True, negrita_inicio=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if sangria:
        p.paragraph_format.first_line_indent = Cm(1.27)
    if negrita_inicio:
        r = p.add_run(negrita_inicio)
        r.bold = True
    p.add_run(texto)
    return p


def vinetas(doc, items, numerada=False):
    for it in items:
        p = doc.add_paragraph(style="List Number" if numerada else "List Bullet")
        p.paragraph_format.line_spacing = 1.5
        if isinstance(it, tuple):
            r = p.add_run(it[0])
            r.bold = True
            p.add_run(it[1])
        else:
            p.add_run(it)


def _sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def tabla(doc, encabezado, filas, anchos=None, tam=9, titulo_tabla=None, nota=None):
    if titulo_tabla:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(titulo_tabla)
        r.bold = True
        r.font.size = Pt(11)
    t = doc.add_table(rows=1, cols=len(encabezado))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(encabezado):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(str(h))
        r.bold = True
        r.font.size = Pt(tam)
        _sombrear(c, "D9D9D9")
    # repetir encabezado en cada pagina
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    for fila in filas:
        celdas = t.add_row().cells
        for i, v in enumerate(fila):
            celdas[i].text = ""
            r = celdas[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(tam)
    for fila in t.rows:
        for c in fila.cells:
            for p in c.paragraphs:
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.first_line_indent = Cm(0)
    if anchos:
        for fila in t.rows:
            for i, w in enumerate(anchos):
                fila.cells[i].width = Cm(w)
    if nota:
        p = doc.add_paragraph()
        r = p.add_run(nota)
        r.italic = True
        r.font.size = Pt(10)
    else:
        doc.add_paragraph()
    return t


def figura(doc, ruta, titulo_fig, ancho_cm=15.5, nota=None):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    r = p.add_run(titulo_fig)
    r.bold = True
    r.font.size = Pt(11)
    ruta_abs = ruta if os.path.isabs(ruta) else os.path.join(RAIZ, ruta)
    if not os.path.exists(ruta_abs):
        parrafo(doc, f"[Falta la imagen {ruta}]")
        return
    pi = doc.add_paragraph()
    pi.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pi.add_run().add_picture(ruta_abs, width=Cm(ancho_cm))
    if nota:
        pn = doc.add_paragraph()
        rn = pn.add_run(nota)
        rn.italic = True
        rn.font.size = Pt(10)


def horizontal(doc):
    """Agrega una seccion horizontal (para tablas anchas)."""
    from docx.enum.section import WD_SECTION
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Cm(27.94), Cm(21.59)
    return sec


def vertical(doc):
    from docx.enum.section import WD_SECTION
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
    return sec


def guardar(doc, nombre):
    ruta = os.path.join(RAIZ, "docs", nombre)
    doc.save(ruta)
    print("ok", ruta)
    return ruta


REFERENCIAS = [
    "International Software Testing Qualifications Board. (2023). Certified Tester Foundation Level syllabus (Versión 4.0). ISTQB. https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0",
    "Istanbul. (s. f.). Istanbul: JavaScript test coverage made simple. Recuperado el 16 de noviembre de 2026, de https://istanbul.js.org/",
    "Microsoft. (s. f.). Playwright: Fast and reliable end-to-end testing for modern web apps. Recuperado el 16 de noviembre de 2026, de https://playwright.dev/",
    "Microsoft. (s. f.). Page object models. En Playwright documentation. Recuperado el 16 de noviembre de 2026, de https://playwright.dev/docs/pom",
    "Microsoft. (s. f.). Reporters. En Playwright documentation. Recuperado el 16 de noviembre de 2026, de https://playwright.dev/docs/test-reporters",
    "Sauce Labs. (2026). sample-app-web [Código fuente]. GitHub. https://github.com/saucelabs/sample-app-web",
    "Sauce Labs. (s. f.). Swag Labs (SauceDemo) [Aplicación web]. Recuperado el 16 de noviembre de 2026, de https://www.saucedemo.com/",
    "nyc. (s. f.). nyc: The Istanbul command line interface [Código fuente]. GitHub. https://github.com/istanbuljs/nyc",
    "iFaxity. (s. f.). vite-plugin-istanbul [Código fuente]. GitHub. https://github.com/iFaxity/vite-plugin-istanbul",
]


def referencias(doc):
    titulo(doc, "Referencias")
    for ref in sorted(REFERENCIAS):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-1.27)
        p.add_run(ref)
