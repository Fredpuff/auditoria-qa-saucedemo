# Genera docs/01_Plan_de_pruebas.docx
from doc_base import *  # noqa: F401,F403
from datos import CASOS, BUGS, REQUISITOS, CFG, INT1, INT2
from casos import P, N, VL, TD, TE, PE, EX

ENTORNO = [
    ("Sistema operativo", "Windows 11 Home 10.0.26200 (64 bits)"),
    ("Node.js / npm", "22.18.0 / 10.9.3"),
    ("Playwright (@playwright/test)", "1.65.1"),
    ("TypeScript", "7.0.2"),
    ("Navegadores", "Chromium 159.0.8154.6 y Firefox 159.0 (instalados por Playwright)"),
    ("Resolución", "1280 x 720 (perfil Desktop Chrome / Desktop Firefox); 375 px para la revisión móvil"),
    ("Aplicación", "https://www.saucedemo.com (versión pública del 16-11-2026)"),
    ("Cobertura de código", "saucelabs/sample-app-web, commit d5cd655, Vite 8.3.5 + vite-plugin-istanbul 9.0.1 + nyc 18.0.0"),
    ("Fecha de ejecución", "16 de noviembre de 2026"),
]

doc = nuevo_documento()
portada(doc, "Plan de pruebas", "Entregable 1")

titulo(doc, "Plan de pruebas")
titulo(doc, "1. Objetivo de la auditoría", 2)
parrafo(doc, "El objetivo de esta auditoría es evaluar la calidad funcional de la tienda en línea SauceDemo (Swag Labs) "
        "antes de una posible salida a producción. Queremos saber si un cliente puede iniciar sesión, buscar productos, "
        "armar su carrito y terminar una compra sin errores, y si la aplicación se comporta igual con los distintos tipos de "
        "usuario que trae el sistema. Con los resultados se entregará un concepto final de si la aplicación está lista o no "
        "para producción.")
parrafo(doc, "Como la aplicación no tiene requisitos escritos, tomamos como resultado esperado el comportamiento del usuario "
        "standard_user junto con lo que se deduce de la interfaz (textos de botones, mensajes y flujo de pantallas). "
        "Cualquier diferencia con los demás usuarios se trató como un posible defecto y se verificó antes de reportarlo.")

titulo(doc, "2. Alcance", 2)
parrafo(doc, "Incluido en la auditoría:", sangria=False)
vinetas(doc, [
    "Pruebas funcionales de sistema y de aceptación sobre la interfaz web pública.",
    "Los seis usuarios de prueba: standard_user, locked_out_user, problem_user, performance_glitch_user, error_user y visual_user.",
    "Navegadores Chromium y Firefox en escritorio y una revisión manual en tamaño de celular.",
    "Medición básica del tiempo de inicio de sesión.",
    "Revisión de errores de consola y respuestas HTTP 4xx/5xx que se ven desde el navegador.",
    "Cobertura de código del JavaScript del cliente, medida con el código fuente público de la aplicación.",
])
parrafo(doc, "Excluido de la auditoría:", sangria=False)
tabla(doc, ["Elemento excluido", "Motivo"], [
    ("Pagos reales", "La aplicación es una demo; la tarjeta SauceCard #31337 es ficticia y no hay pasarela de pago."),
    ("Pruebas de carga y estrés", "Es un sitio público de terceros; generar carga masiva no está autorizado y podría afectar a otros usuarios."),
    ("Pruebas de seguridad (pentesting)", "No hay autorización del dueño del sitio para hacer pruebas intrusivas."),
    ("Backend y base de datos", "No hay acceso. SauceDemo guarda todo en el navegador (cookie y localStorage)."),
    ("Safari / WebKit y dispositivos reales", "No se cuenta con equipos Mac ni con celulares físicos para el proyecto."),
], anchos=[5, 11])

titulo(doc, "3. Funcionalidades por evaluar", 2)
tabla(doc, ["Módulo", "Funcionalidad", "Requisitos"], [
    ("Login", "Inicio de sesión, mensajes de error, usuario bloqueado, tiempo de respuesta", "RF-01 a RF-04"),
    ("Catálogo y ordenamiento", "Seis productos, imágenes, precios, orden por nombre y por precio, Dynamic Catalog", "RF-05 a RF-07, RF-24"),
    ("Detalle de producto", "Página de detalle de cada producto", "RF-08"),
    ("Carrito", "Agregar, quitar, contador y página del carrito", "RF-09 a RF-11"),
    ("Checkout", "Información > Resumen > Completado, validaciones, cálculo de impuesto y total, cancelar", "RF-12 a RF-15"),
    ("Menú", "All Items, About, Logout y Reset App State", "RF-16 a RF-19"),
    ("Control de acceso", "URL protegidas sin sesión y transiciones del checkout", "RF-20 y RF-21"),
    ("Visual y accesibilidad", "Presentación consistente, vista móvil, teclado y textos alternativos", "RF-22 y RF-23"),
], anchos=[4, 9, 3.5])

titulo(doc, "4. Estrategia de prueba", 2)
parrafo(doc, "Se usaron técnicas de caja negra vistas en la Clase 7, porque no se trabaja con el código de la aplicación "
        "sino con su comportamiento visible. Cada técnica se aplicó donde tenía más sentido:")
vinetas(doc, [
    ("Pruebas positivas: ", "caminos felices de cada módulo (login, agregar, ordenar, comprar, logout)."),
    ("Pruebas negativas: ", "datos incorrectos o acciones no permitidas (usuario con mayúsculas, checkout sin datos, URL sin sesión, carrito vacío)."),
    ("Valores límite: ", "cantidad de productos en el carrito (0, 1, 5 y 6), longitud del nombre (0, 1, 50 y 255) y cálculo del impuesto con 1 y con 6 productos."),
    ("Tablas de decisión: ", "login (usuario x contraseña, 12 combinaciones reducidas a 6 reglas) y formulario de checkout (3 campos, 8 combinaciones reducidas a 4 reglas)."),
    ("Transición de estados: ", "flujo del checkout (Inventario > Carrito > Información > Resumen > Completado) y ciclo de sesión (Sin sesión > Autenticado > Sesión cerrada), con transiciones válidas e inválidas."),
    ("Predicción de errores: ", "a partir de la exploración se predijeron fallos por tipo de usuario y se diseñaron casos para cada uno."),
    ("Exploratorio basado en sesión: ", "una sesión por cada uno de los seis usuarios con captura de pantallas, consola y red, guiada por el mapa mental."),
])
figura(doc, "docs/img/mapa-mental.png", "Figura 1. Mapa mental de módulos y escenarios", ancho_cm=16)
figura(doc, "docs/img/estados-checkout.png", "Figura 2. Diagrama de transición de estados del checkout", ancho_cm=16)
figura(doc, "docs/img/estados-sesion.png", "Figura 3. Diagrama de transición de estados de la sesión", ancho_cm=14)

titulo(doc, "5. Niveles y tipos de prueba", 2)
vinetas(doc, [
    ("Nivel de sistema: ", "se prueba la aplicación completa desplegada, como la usa un cliente."),
    ("Nivel de aceptación: ", "los flujos de negocio (comprar un producto) se validan contra lo que esperaría el dueño de la tienda."),
    ("Funcionales: ", "todas las funciones listadas en la sección 3."),
    ("Rendimiento básico: ", "tiempo de inicio de sesión con 5 repeticiones por usuario. Se fijó un umbral de 2000 ms porque es un tiempo de espera que un usuario todavía tolera para una acción simple; con standard_user el login tarda menos de 200 ms, así que el umbral es generoso."),
    ("Regresión automatizada: ", "el mismo flujo de compra se repite con cuatro usuarios y toda la suite se ejecuta en cada cambio mediante GitHub Actions."),
])

titulo(doc, "6. Entorno de pruebas", 2)
tabla(doc, ["Elemento", "Detalle"], ENTORNO, anchos=[5, 11])

titulo(doc, "7. Criterios", 2)
tabla(doc, ["Criterio", "Condiciones"], [
    ("Entrada", "Sitio disponible (responde 200 en la página de login); entorno instalado (Node, Playwright y navegadores); plan y casos revisados por los dos integrantes."),
    ("Salida", "100 % de los casos diseñados ejecutados; cada fallo con su bug documentado, evidencia y 3 de 3 reproducciones; cobertura de código mayor al 50 %; informe final entregado."),
    ("Suspensión", "El sitio no responde por más de 30 minutos, cambia la interfaz de forma que los selectores dejan de existir, o más del 50 % de los casos fallan por causas de entorno (no de la aplicación)."),
    ("Reanudación", "El sitio vuelve a estar disponible y la página de login carga; se ajustan los selectores si la interfaz cambió y se vuelven a ejecutar los casos afectados desde el inicio."),
], anchos=[3, 13])

titulo(doc, "8. Riesgos", 2)
tabla(doc, ["Riesgo", "Tipo", "Probabilidad", "Impacto", "Mitigación"], [
    ("La aplicación demo cambia sin aviso (nuevas funciones o selectores)", "Proceso", "Media", "Alto", "Selectores data-test estables, Page Object Model para cambiar en un solo lugar y registro de la fecha de ejecución."),
    ("No hay requisitos formales", "Proceso", "Alta", "Medio", "Se usa standard_user como línea base y se justifica cada resultado esperado."),
    ("Dependencia de internet y del sitio público", "Proceso", "Media", "Alto", "Ejecución repetida 3 veces; copia local del código para la cobertura."),
    ("Los datos no persisten en un servidor (todo vive en el navegador)", "Producto", "Alta", "Medio", "Cada prueba usa un contexto de navegador limpio; se documenta el efecto en BUG-16."),
    ("Defectos en el flujo de compra con ciertos usuarios", "Producto", "Alta", "Alto", "Casos de regresión por usuario y reporte con severidad crítica."),
    ("El código público puede no ser idéntico al desplegado", "Proceso", "Media", "Medio", "Se fija el commit usado y se aclara en el informe de cobertura."),
    ("Tiempo limitado del equipo", "Proceso", "Media", "Medio", "Automatización de los casos repetitivos y reparto de tareas en el cronograma."),
], anchos=[4.5, 1.8, 2, 1.7, 6.5], tam=8)

titulo(doc, "9. Cronograma y roles", 2)
tabla(doc, ["Rol", "Responsable", "Tareas"], [
    ("Líder de pruebas y automatización", INT1, "Plan de pruebas, framework Playwright (POM y datos JSON), tablas de decisión y de estados, cobertura de código, integración continua."),
    ("Analista de pruebas y defectos", INT2, "Mapa mental, diseño y ejecución manual de casos positivos, negativos y de valores límite, reporte de defectos con evidencias, revisión visual y de accesibilidad."),
    ("Ambos", f"{INT1} y {INT2}", "Sesiones exploratorias con los seis usuarios, revisión cruzada de casos y bugs, informe final y sustentación."),
], anchos=[4, 4, 8.5])
tabla(doc, ["Semana", "Actividad", "Responsable"], [
    ("1", "Exploración de la aplicación con los 6 usuarios y lista de hallazgos", "Ambos"),
    ("1", "Plan de pruebas, mapa mental, tablas de decisión y diagramas de estados", INT1),
    ("2", "Diseño de casos de prueba y ejecución manual con capturas", INT2),
    ("2", "Implementación de la automatización y ejecución 3 veces", INT1),
    ("3", "Reporte de defectos con severidad, prioridad y evidencias", INT2),
    ("3", "Cobertura de código y de requisitos", INT1),
    ("4", "Informe final, presentación y ensayo de la sustentación", "Ambos"),
], anchos=[2, 10, 4.5])

titulo(doc, "10. Matriz de trazabilidad", 2)
parrafo(doc, "La matriz relaciona cada requisito identificado con los casos que lo prueban y los defectos encontrados. "
        "La versión completa con todos los casos está en la hoja Trazabilidad del archivo 02_Casos_de_prueba.xlsx.")
filas = []
for rid, mod, desc in REQUISITOS:
    cs = [c for c in CASOS if rid in c["rf"]]
    bugs = sorted({c["bug"] for c in cs if c["bug"]})
    filas.append((rid, mod, desc, ", ".join(c["id"] for c in cs) or "-", ", ".join(bugs) or "-"))
tabla(doc, ["Req.", "Módulo", "Descripción", "Casos", "Bugs"], filas, anchos=[1.5, 2.8, 5.5, 4, 2.7], tam=8)

guardar(doc, "01_Plan_de_pruebas.docx")
