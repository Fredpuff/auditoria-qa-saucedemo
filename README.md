# Auditoría de calidad de SauceDemo

Proyecto final de la electiva **Testing y QA** (UNIMINUTO, Tecnología en Desarrollo de Software).
Se audita la tienda de ejemplo [SauceDemo](https://www.saucedemo.com) con pruebas manuales y automatizadas
en **Playwright + TypeScript**, siguiendo el patrón Page Object Model con datos en JSON (enfoque híbrido data-driven).

**Autores:** Frederick Alexandro Abril Mogollón y Santiago Abril
**Docente:** [NOMBRE DOCENTE]

## Dónde está cada cosa

| Qué | Archivo |
|---|---|
| Plan de pruebas | `docs/01_Plan_de_pruebas.docx` |
| Casos de prueba (57) | `docs/02_Casos_de_prueba.xlsx` |
| Reporte de defectos (19 fichas con capturas) | `docs/03_Reporte_de_defectos.docx` |
| Automatización | `docs/04_Automatizacion.docx` |
| Cobertura | `docs/05_Cobertura.docx` |
| Informe final | `docs/06_Informe_final_auditoria.docx` |
| Sustentación | `docs/07_Sustentacion.pptx` |

Las capturas, los videos y el reporte HTML de Playwright **no están en el repositorio** porque pesan más de 100 MB
y las capturas ya aparecen dentro de los documentos. Se vuelven a generar en tu equipo con `npm test`
(y `npm run evidencias` para las capturas). Para regenerar los documentos con `python tools/docs/generar_todo.py` hacen falta esas capturas.

## Requisitos

- Node.js 20 o superior (Playwright 1.65 pide Node 20+; se probó con Node 22.18.0)
- npm 10 o superior
- Git
- Conexión a internet (las pruebas se ejecutan contra https://www.saucedemo.com)

## Instalación

```bash
git clone https://github.com/Fredpuff/auditoria-qa-saucedemo.git
cd auditoria-qa-saucedemo
npm install
npx playwright install chromium firefox
```

## Ejecución

| Acción | Comando |
|---|---|
| Toda la suite (Chromium y Firefox) | `npm test` |
| Solo Chromium | `npm run test:chromium` |
| Solo las pruebas smoke | `npm run test:smoke` |
| Solo las pruebas que reproducen defectos | `npm run test:defectos` |
| Un solo archivo | `npx playwright test tests/login.spec.ts` |
| Un solo caso por su ID | `npx playwright test -g "CP-05"` |
| Con el navegador visible | `npx playwright test --headed --project=chromium` |
| Visible y en cámara lenta (slowMo 500 ms) | `npm run test:lento` |
| Abrir el reporte HTML (después de `npm test`) | `npx playwright show-report evidencias/reportes/html` |
| Ver la traza de un fallo | `npx playwright show-trace evidencias/test-results/<carpeta>/trace.zip` |

En PowerShell, para cambiar la cámara lenta: `$env:SLOWMO=1000; npx playwright test --headed --project=chromium --workers=1`.

> **Importante:** 19 pruebas por navegador fallan **a propósito**. Cada una afirma el comportamiento
> esperado y falla porque la aplicación tiene un defecto real (BUG-01 a BUG-19). Por eso `npm test`
> termina con código de salida 1. El título de cada prueba indica su caso y su bug, por ejemplo
> `CP-44 | BUG-04 | escribir el apellido no debe cambiar el nombre con problem_user`.

## Cobertura de código

La cobertura se mide sobre el código fuente público de SauceDemo
([saucelabs/sample-app-web](https://github.com/saucelabs/sample-app-web)), compilado en local con Istanbul.

```bash
npm run app:prepare   # clona la app (commit fijo), instala, instrumenta y compila (solo la primera vez)
npm run coverage      # corre la suite contra http://localhost:3000 y genera coverage/codigo/index.html
```

`app:prepare` elimina los comentarios `istanbul ignore` que trae el código original para que todo el
código de `src` cuente en el cálculo. Se excluyen solo las pruebas unitarias propias de la app, las
historias de Storybook y los archivos de configuración de Jest.

## Estructura

```
auditoria-qa-saucedemo/
├── playwright.config.ts          configuración (Chromium y Firefox, capturas, video, traza, reportes)
├── .github/workflows/tests.yml   integración continua: suite y cobertura en cada push
├── tests/
│   ├── fixtures.ts               registro de consola, errores y red; recolección de cobertura
│   ├── pages/                    Page Object Model (LoginPage, InventoryPage, CartPage, CheckoutPage)
│   ├── data/                     usuarios, productos y tablas de decisión en JSON
│   ├── login.spec.ts             login, sesión y tabla de decisión del login
│   ├── inventario.spec.ts        ordenamiento y detalle de producto
│   ├── carrito.spec.ts           carrito y valores límite
│   ├── checkout.spec.ts          checkout, tabla de decisión del formulario y transición de estados
│   ├── regresion.spec.ts         mismo flujo de compra parametrizado por usuario
│   └── defectos.spec.ts          pruebas que reproducen los defectos de cada usuario
├── tools/                        scripts de exploración, cobertura, evidencias y documentos
├── coverage/codigo/              reporte de cobertura de código (nyc)
├── evidencias/
│   ├── gifs/                     BUG-10.gif grabado en Brave
│   ├── videos/                   BUG-10.webm (plan B de la demo)
│   └── reportes/                 resultados JSON y JUnit de las 3 corridas, tiempos de login, salida de consola
└── docs/                         plan, casos, defectos, automatización, cobertura, informe y sustentación
```

## Integración continua

El workflow `.github/workflows/tests.yml` corre en cada push. Tiene dos trabajos:
`e2e` (suite completa, publica el artifact `reporte-playwright`) y `cobertura`
(prepara la app local y publica `reporte-cobertura`). El trabajo `e2e` termina en rojo por los
defectos reales de la aplicación; el reporte se publica igual.
