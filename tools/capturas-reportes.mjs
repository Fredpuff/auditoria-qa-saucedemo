// Toma capturas del reporte HTML de Playwright y del reporte de cobertura (nyc) para los documentos.
// Uso: node tools/capturas-reportes.mjs
import { chromium } from '@playwright/test';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';

const OUT = 'docs/img';
fs.mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

// Reporte de Playwright: se sirve con show-report porque usa recursos locales
const servidor = spawn('npx', ['playwright', 'show-report', 'evidencias/reportes/html', '--port', '9323'], { shell: true });
await new Promise((r) => setTimeout(r, 4000));
await page.goto('http://localhost:9323');
await page.waitForTimeout(1500);
await page.screenshot({ path: `${OUT}/reporte-html-general.png` });
await page.goto('http://localhost:9323/#?q=s:failed');
await page.waitForTimeout(1500);
await page.screenshot({ path: `${OUT}/reporte-html-fallidos.png` });
// detalle de un test fallido
await page.getByText('CP-49 | BUG-10').first().click();
await page.waitForTimeout(1500);
await page.screenshot({ path: `${OUT}/reporte-html-detalle-BUG-10.png`, fullPage: false });
servidor.kill();

// Reporte de cobertura (archivos estaticos)
const cov = path.resolve('coverage/codigo/index.html');
if (fs.existsSync(cov)) {
  await page.goto(pathToFileURL(cov).href);
  await page.screenshot({ path: `${OUT}/cobertura-resumen.png`, fullPage: true });
  await page.goto(pathToFileURL(path.resolve('coverage/codigo/src/pages/index.html')).href);
  await page.screenshot({ path: `${OUT}/cobertura-pages.png`, fullPage: true });
  await page.goto(pathToFileURL(path.resolve('coverage/codigo/src/pages/CheckOutStepOne.jsx.html')).href);
  await page.screenshot({ path: `${OUT}/cobertura-detalle-CheckOutStepOne.png`, clip: { x: 0, y: 0, width: 1400, height: 1500 }, fullPage: true });
  await page.goto(pathToFileURL(path.resolve('coverage/codigo/src/pages/Finish.jsx.html')).href);
  await page.screenshot({ path: `${OUT}/cobertura-detalle-Finish.png`, clip: { x: 0, y: 0, width: 1400, height: 1300 }, fullPage: true });
}
await browser.close();
process.exit(0);
