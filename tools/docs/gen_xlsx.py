# Genera docs/02_Casos_de_prueba.xlsx con los estados reales de la ultima ejecucion.
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from datos import CASOS, BUGS, REQUISITOS, CFG, FECHA, INT1, INT2, RAIZ, resultados_playwright, estado_caso
from casos import P, N, VL, TD, TE, PE, EX

estados, stats, _ = resultados_playwright()
bug_por_id = {b["id"]: b for b in BUGS}
MANUAL = {
    "CP-54": "Sin desborde horizontal (ancho del documento 375 px igual al de la pantalla). Botones y textos legibles en login, catálogo y checkout. Ver capturas.",
    "CP-55": "Se entra solo con Tab y Enter. Todas las imágenes de la página tienen texto alternativo.",
}

COLS = ["ID", "Nombre", "Técnica", "Módulo", "Objetivo/descripción", "Precondiciones", "Pasos de ejecución",
        "Datos de prueba", "Resultado esperado", "Resultado obtenido", "Estado", "Bug asociado", "Evidencia",
        "¿Automatizado?", "Ejecutado por", "Fecha"]
ANCHOS = [8, 30, 18, 16, 32, 26, 42, 24, 36, 46, 11, 11, 22, 13, 24, 11]

borde = Border(*(Side(style="thin", color="999999"),) * 4)
cab = PatternFill("solid", fgColor="2F4B7C")
verde = PatternFill("solid", fgColor="D9EAD3")
rojo = PatternFill("solid", fgColor="F4CCCC")
ajuste = Alignment(wrap_text=True, vertical="top")


def fila_caso(c):
    est = estado_caso(c, estados)
    if est == "Fallido":
        obtenido = bug_por_id[c["bug"]]["obtenido"]
    elif c["auto"] == "Sí":
        obtenido = "Igual al esperado (Chromium y Firefox)."
        if c["bug"]:
            raise SystemExit(f"{c['id']} tiene bug pero paso")
    else:
        obtenido = MANUAL[c["id"]]
    if est == "Fallido" and not c["bug"]:
        raise SystemExit(f"{c['id']} fallo sin bug asociado")
    evid = f"{c['bug']}.png; {c['bug']}.webm" if c["bug"] else f"{c['id']}.png"
    if c["id"] == "CP-54":
        evid = "CP-54-login-movil.png; CP-54-inventario-movil.png; CP-54-checkout-movil.png"
    if c["id"] == "CP-55":
        evid = "CP-55-teclado.png"
    quien = INT1 if c["quien"] == 1 else INT2
    if c["auto"] == "Sí":
        quien += " (automatizado)"
    return [c["id"], c["nombre"], c["tecnica"], c["modulo"], c["objetivo"], c["pre"], c["pasos"], c["datos"],
            c["esperado"], obtenido, est, c["bug"] or "-", evid, c["auto"], quien, FECHA]


def hoja_casos(ws, lista):
    ws.append(COLS)
    for i, w in enumerate(ANCHOS, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for cel in ws[1]:
        cel.font = Font(bold=True, color="FFFFFF", name="Arial", size=10)
        cel.fill = cab
        cel.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cel.border = borde
    for c in lista:
        ws.append(fila_caso(c))
        for cel in ws[ws.max_row]:
            cel.alignment = ajuste
            cel.border = borde
            cel.font = Font(name="Arial", size=9)
        est = ws.cell(ws.max_row, 11)
        est.fill = verde if est.value == "Aprobado" else rojo
        est.font = Font(name="Arial", size=9, bold=True)
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLS))}{ws.max_row}"


wb = Workbook()
res = wb.active
res.title = "Resumen"

# hoja con todos los casos (base de las formulas del resumen)
todos = wb.create_sheet("Todos los casos")
hoja_casos(todos, CASOS)
n = len(CASOS) + 1

for nombre, tec in [("Positivas", P), ("Negativas", N), ("Valores límite", VL), ("Tabla de decisión", TD),
                    ("Transición de estados", TE), ("Predicción de errores", PE), ("Exploratorias", EX)]:
    hoja_casos(wb.create_sheet(nombre), [c for c in CASOS if c["tecnica"] == tec])

# ---------------- tablas de decision completas
td = wb.create_sheet("Tablas de decisión")
negr = Font(bold=True, name="Arial", size=10)
td.append(["Tabla 1. Login: Usuario {válido, inválido, vacío, bloqueado} x Contraseña {correcta, incorrecta, vacía} = 12 combinaciones"])
td["A1"].font = Font(bold=True, name="Arial", size=11)
td.append(["Combinación", "Usuario", "Contraseña", "Resultado observado", "Regla reducida", "Caso"])
combos = [
    ("1", "Válido", "Correcta", "Acceso a /inventory.html", "R3", "CP-24"),
    ("2", "Válido", "Incorrecta", "Username and password do not match any user in this service", "R5", "CP-26"),
    ("3", "Válido", "Vacía", "Password is required", "R2", "CP-23"),
    ("4", "Inválido", "Correcta", "Username and password do not match any user in this service", "R6", "CP-27"),
    ("5", "Inválido", "Incorrecta", "Username and password do not match any user in this service", "R6", "CP-27"),
    ("6", "Inválido", "Vacía", "Password is required", "R2", "CP-23"),
    ("7", "Vacío", "Correcta", "Username is required", "R1", "CP-22"),
    ("8", "Vacío", "Incorrecta", "Username is required", "R1", "CP-22"),
    ("9", "Vacío", "Vacía", "Username is required", "R1", "CP-22"),
    ("10", "Bloqueado", "Correcta", "Sorry, this user has been locked out.", "R4", "CP-25"),
    ("11", "Bloqueado", "Incorrecta", "Username and password do not match any user in this service", "R5", "CP-26"),
    ("12", "Bloqueado", "Vacía", "Password is required", "R2", "CP-23"),
]
for c in combos:
    td.append(list(c))
td.append([])
td.append(["Reglas reducidas (combinaciones con el mismo resultado se agrupan; '-' = no importa)"])
td.cell(td.max_row, 1).font = negr
td.append(["Regla", "Usuario", "Contraseña", "Acción / mensaje esperado (prefijo 'Epic sadface: ')", "Combinaciones", "Caso"])
reducidas = [
    ("R1", "Vacío", "-", "Username is required", "7, 8, 9", "CP-22"),
    ("R2", "Válido, inválido o bloqueado", "Vacía", "Password is required", "3, 6, 12", "CP-23"),
    ("R3", "Válido", "Correcta", "Acceso al catálogo", "1", "CP-24"),
    ("R4", "Bloqueado", "Correcta", "Sorry, this user has been locked out.", "10", "CP-25"),
    ("R5", "Válido o bloqueado", "Incorrecta", "Username and password do not match any user in this service", "2, 11", "CP-26"),
    ("R6", "Inválido", "Correcta o incorrecta", "Username and password do not match any user in this service", "4, 5", "CP-27"),
]
for r in reducidas:
    td.append(list(r))
td.append([])
td.append(["Tabla 2. Formulario de checkout: First Name, Last Name y Postal Code (lleno / vacío) = 8 combinaciones"])
td.cell(td.max_row, 1).font = Font(bold=True, name="Arial", size=11)
td.append(["Combinación", "First Name", "Last Name", "Postal Code", "Resultado observado", "Regla", "Caso"])
form = [("1", "Lleno", "Lleno", "Lleno", "Pasa al resumen", "C4", "CP-31"),
        ("2", "Lleno", "Lleno", "Vacío", "Error: Postal Code is required", "C3", "CP-30"),
        ("3", "Lleno", "Vacío", "Lleno", "Error: Last Name is required", "C2", "CP-29"),
        ("4", "Lleno", "Vacío", "Vacío", "Error: Last Name is required", "C2", "CP-29"),
        ("5", "Vacío", "Lleno", "Lleno", "Error: First Name is required", "C1", "CP-28"),
        ("6", "Vacío", "Lleno", "Vacío", "Error: First Name is required", "C1", "CP-28"),
        ("7", "Vacío", "Vacío", "Lleno", "Error: First Name is required", "C1", "CP-28"),
        ("8", "Vacío", "Vacío", "Vacío", "Error: First Name is required", "C1", "CP-28 y CP-09")]
for f in form:
    td.append(list(f))
td.append([])
td.append(["Regla", "First Name", "Last Name", "Postal Code", "Mensaje esperado", "Combinaciones", "Caso"])
for r in [("C1", "Vacío", "-", "-", "Error: First Name is required", "5, 6, 7, 8", "CP-28"),
          ("C2", "Lleno", "Vacío", "-", "Error: Last Name is required", "3, 4", "CP-29"),
          ("C3", "Lleno", "Lleno", "Vacío", "Error: Postal Code is required", "2", "CP-30"),
          ("C4", "Lleno", "Lleno", "Lleno", "Continúa al resumen", "1", "CP-31")]:
    td.append(list(r))
for i, w in enumerate([12, 26, 22, 58, 22, 16, 16], 1):
    td.column_dimensions[get_column_letter(i)].width = w
for row in td.iter_rows(min_row=2):
    for cel in row:
        cel.alignment = ajuste
        if cel.value in ("Combinación", "Regla"):
            for x in row:
                x.font = negr
                x.fill = PatternFill("solid", fgColor="D9E2F3")

# ---------------- tabla de transiciones
tt = wb.create_sheet("Transiciones")
tt.append(["Estado origen", "Evento", "Estado destino esperado", "¿Válida?", "Caso", "Resultado"])
trans = [
    ("Login (E0)", "Login válido", "S1 Inventario (E1)", "Válida", "CP-01"),
    ("S1 Inventario", "Clic en el icono del carrito", "S2 Carrito", "Válida", "CP-32"),
    ("S2 Carrito", "Checkout (con productos)", "S3 Información", "Válida", "CP-32"),
    ("S2 Carrito", "Continue Shopping", "S1 Inventario", "Válida", "CP-33"),
    ("S3 Información", "Continue con datos válidos", "S4 Resumen", "Válida", "CP-32"),
    ("S3 Información", "Continue con datos incompletos", "S3 con mensaje de error", "Válida", "CP-28"),
    ("S3 Información", "Cancel", "S2 Carrito", "Válida", "CP-33"),
    ("S4 Resumen", "Finish", "S5 Completado", "Válida", "CP-32"),
    ("S4 Resumen", "Cancel", "S1 Inventario", "Válida", "CP-33"),
    ("S5 Completado", "Back Home", "S1 Inventario con carrito vacío", "Válida", "CP-32"),
    ("E1 Autenticado", "Logout", "E2 Sesión cerrada (login)", "Válida", "CP-06"),
    ("E0 Sin sesión", "URL /inventory.html", "Login con mensaje", "Inválida (debe bloquearse)", "CP-08"),
    ("E0 Sin sesión", "URL /checkout-step-two.html", "Login con mensaje", "Inválida (debe bloquearse)", "CP-34"),
    ("E2 Sesión cerrada", "Botón Back del navegador", "Login, sin productos", "Inválida (debe bloquearse)", "CP-36"),
    ("S1 Inventario", "URL /checkout-complete.html", "Redirigir (no hay compra)", "Inválida (debe bloquearse)", "CP-35"),
    ("S2 Carrito vacío", "Checkout", "Permanecer en S2", "Inválida (debe bloquearse)", "CP-10"),
    ("Carrito con productos", "Reset App State", "Carrito vacío y botones en Add to cart", "Válida", "CP-37"),
]
caso_id = {c["id"]: c for c in CASOS}
for t in trans:
    est = estado_caso(caso_id[t[4]], estados)
    tt.append(list(t) + [est + (f" ({caso_id[t[4]]['bug']})" if caso_id[t[4]]["bug"] else "")])
for i, w in enumerate([22, 32, 36, 26, 10, 22], 1):
    tt.column_dimensions[get_column_letter(i)].width = w
for cel in tt[1]:
    cel.font = Font(bold=True, color="FFFFFF", name="Arial", size=10)
    cel.fill = cab
for row in tt.iter_rows(min_row=2):
    for cel in row:
        cel.alignment = ajuste
        cel.border = borde
    row[5].fill = verde if row[5].value.startswith("Aprobado") else rojo

# ---------------- trazabilidad
tz = wb.create_sheet("Trazabilidad")
tz.append(["Requisito", "Módulo", "Descripción", "Casos", "Casos ejecutados", "Bugs", "¿Cubierto?"])
for rid, mod, desc in REQUISITOS:
    cs = [c for c in CASOS if rid in c["rf"]]
    bugs = sorted({c["bug"] for c in cs if c["bug"]})
    tz.append([rid, mod, desc, ", ".join(c["id"] for c in cs) or "-", len(cs), ", ".join(bugs) or "-", "Sí" if cs else "No"])
for i, w in enumerate([9, 18, 46, 40, 10, 22, 11], 1):
    tz.column_dimensions[get_column_letter(i)].width = w
for cel in tz[1]:
    cel.font = Font(bold=True, color="FFFFFF", name="Arial", size=10)
    cel.fill = cab
for row in tz.iter_rows(min_row=2):
    for cel in row:
        cel.alignment = ajuste
        cel.border = borde

# ---------------- resumen con formulas sobre "Todos los casos"
T = "'Todos los casos'"
res["A1"] = "Resumen de casos de prueba - Auditoría de calidad de SauceDemo"
res["A1"].font = Font(bold=True, size=13, name="Arial")
res["A2"] = f"Fecha de ejecución: {FECHA}. Estados tomados de la ejecución automatizada (Chromium y Firefox dieron el mismo resultado) y de la ejecución manual."
res.append([])
res.append(["Indicador", "Valor"])
fila_ind = res.max_row
res.append(["Casos diseñados", f"=COUNTA({T}!A2:A{n})"])
res.append(["Casos ejecutados", f"=COUNTIF({T}!K2:K{n},\"Aprobado\")+COUNTIF({T}!K2:K{n},\"Fallido\")"])
res.append(["Aprobados", f"=COUNTIF({T}!K2:K{n},\"Aprobado\")"])
res.append(["Fallidos", f"=COUNTIF({T}!K2:K{n},\"Fallido\")"])
res.append(["% aprobados", f"=B{fila_ind+3}/B{fila_ind+2}"])
res.append(["% fallidos", f"=B{fila_ind+4}/B{fila_ind+2}"])
res.append(["Casos automatizados", f"=COUNTIF({T}!N2:N{n},\"Sí\")"])
res.append(["% automatizados sobre diseñados", f"=B{fila_ind+7}/B{fila_ind+1}"])
for r in (fila_ind + 5, fila_ind + 6, fila_ind + 8):
    res.cell(r, 2).number_format = "0.0%"
res.append([])
res.append(["Por técnica", "Total", "Aprobados", "Fallidos", "% aprobados", "% fallidos"])
f_tec = res.max_row
for tec in [P, N, VL, TD, TE, PE, EX]:
    r = res.max_row + 1
    res.append([tec, f"=COUNTIF({T}!C2:C{n},A{r})", f"=COUNTIFS({T}!C2:C{n},A{r},{T}!K2:K{n},\"Aprobado\")",
                f"=COUNTIFS({T}!C2:C{n},A{r},{T}!K2:K{n},\"Fallido\")", f"=IF(B{r}=0,0,C{r}/B{r})", f"=IF(B{r}=0,0,D{r}/B{r})"])
    res.cell(r, 5).number_format = res.cell(r, 6).number_format = "0.0%"
r = res.max_row + 1
res.append(["Total", f"=SUM(B{f_tec+1}:B{r-1})", f"=SUM(C{f_tec+1}:C{r-1})", f"=SUM(D{f_tec+1}:D{r-1})", f"=C{r}/B{r}", f"=D{r}/B{r}"])
res.cell(r, 5).number_format = res.cell(r, 6).number_format = "0.0%"
res.append([])
res.append(["Por módulo", "Total", "Aprobados", "Fallidos", "% aprobados", "% fallidos"])
f_mod = res.max_row
for mod in ["Login", "Catálogo", "Detalle de producto", "Carrito", "Checkout", "Menú", "Control de acceso"]:
    r = res.max_row + 1
    res.append([mod, f"=COUNTIF({T}!D2:D{n},A{r})", f"=COUNTIFS({T}!D2:D{n},A{r},{T}!K2:K{n},\"Aprobado\")",
                f"=COUNTIFS({T}!D2:D{n},A{r},{T}!K2:K{n},\"Fallido\")", f"=IF(B{r}=0,0,C{r}/B{r})", f"=IF(B{r}=0,0,D{r}/B{r})"])
    res.cell(r, 5).number_format = res.cell(r, 6).number_format = "0.0%"
r = res.max_row + 1
res.append(["Total", f"=SUM(B{f_mod+1}:B{r-1})", f"=SUM(C{f_mod+1}:C{r-1})", f"=SUM(D{f_mod+1}:D{r-1})", f"=C{r}/B{r}", f"=D{r}/B{r}"])
res.cell(r, 5).number_format = res.cell(r, 6).number_format = "0.0%"
res.append([])
res.append(["Suite automatizada (última ejecución)", "Valor"])
fs = res.max_row
res.append(["Pruebas ejecutadas (2 navegadores)", stats["expected"] + stats["unexpected"]])
res.append(["Pasaron", stats["expected"]])
res.append(["Fallaron (todas por defectos reales)", stats["unexpected"]])
res.append(["Duración (s)", round(stats["duration"] / 1000, 1)])
for fila in (fila_ind, f_tec, f_mod, fs):
    for cel in res[fila]:
        if cel.value is not None:
            cel.font = Font(bold=True, color="FFFFFF", name="Arial", size=10)
            cel.fill = cab
res.column_dimensions["A"].width = 40
for col in "BCDEF":
    res.column_dimensions[col].width = 13

salida = os.path.join(RAIZ, "docs", "02_Casos_de_prueba.xlsx")
wb.save(salida)
print("ok", salida, "casos:", len(CASOS))
