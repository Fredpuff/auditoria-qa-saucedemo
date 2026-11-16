import { test as base, expect, Locator, Page, TestInfo } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// Fixture automatico: registra errores de consola, excepciones de pagina y respuestas HTTP 4xx/5xx
// y los adjunta al reporte. Si COVERAGE=1 tambien recoge window.__coverage__ (Istanbul).

const CLAVE = '__cobertura_acumulada';

// Se ejecuta en cada documento. Antes de salir de una pagina guarda los contadores en sessionStorage
// para no perder la cobertura cuando hay recargas o navegaciones completas.
const scriptCobertura = `(() => {
  const sumar = (a, b) => {
    for (const f in b) {
      if (!a[f]) { a[f] = b[f]; continue; }
      const x = a[f], y = b[f];
      for (const k in y.s) x.s[k] = (x.s[k] || 0) + y.s[k];
      for (const k in y.f) x.f[k] = (x.f[k] || 0) + y.f[k];
      for (const k in y.b) x.b[k] = x.b[k] ? x.b[k].map((v, i) => v + (y.b[k][i] || 0)) : y.b[k];
    }
    return a;
  };
  window.__sumarCobertura = sumar;
  window.addEventListener('pagehide', () => {
    try {
      if (!window.__coverage__) return;
      const previa = JSON.parse(sessionStorage.getItem('${CLAVE}') || '{}');
      sessionStorage.setItem('${CLAVE}', JSON.stringify(sumar(previa, window.__coverage__)));
    } catch (e) {}
  });
})();`;

async function guardarCobertura(page: Page, testInfo: TestInfo) {
  const cobertura = await page
    .evaluate((clave) => {
      const w = window as any;
      const previa = JSON.parse(sessionStorage.getItem(clave) || '{}');
      if (!w.__coverage__) return previa;
      return w.__sumarCobertura(previa, JSON.parse(JSON.stringify(w.__coverage__)));
    }, CLAVE)
    .catch(() => null);
  if (!cobertura || Object.keys(cobertura).length === 0) return;
  fs.mkdirSync('.nyc_output', { recursive: true });
  const nombre = crypto.createHash('md5').update(testInfo.testId + testInfo.retry).digest('hex');
  fs.writeFileSync(path.join('.nyc_output', `${nombre}.json`), JSON.stringify(cobertura));
}

export const test = base.extend<{ registro: string[] }>({
  registro: [
    async ({ page }, use, testInfo) => {
      const errores: string[] = [];
      page.on('console', (m) => { if (m.type() === 'error') errores.push(`[consola] ${m.text()}`); });
      page.on('pageerror', (e) => errores.push(`[excepcion] ${e.message}`));
      page.on('response', (r) => { if (r.status() >= 400) errores.push(`[red ${r.status()}] ${r.url()}`); });
      page.on('dialog', async (d) => { errores.push(`[alerta] ${d.message()}`); await d.accept(); });
      if (process.env.COVERAGE) await page.addInitScript(scriptCobertura);

      await use(errores);

      if (errores.length) {
        await testInfo.attach('errores-consola-y-red.txt', { body: errores.join('\n'), contentType: 'text/plain' });
      }
      if (process.env.COVERAGE) await guardarCobertura(page, testInfo);
    },
    { auto: true },
  ],
});

// Marca un elemento con borde rojo y guarda la captura con el nombre del caso o del bug.
// Solo en Chromium para no sobrescribir la misma evidencia con otro navegador.
export async function evidencia(page: Page, nombre: string, marcar?: Locator) {
  if (test.info().project.name !== 'chromium' || process.env.COVERAGE) return;
  if (marcar) {
    await marcar.evaluateAll((els) =>
      els.forEach((e) => ((e as HTMLElement).style.outline = '4px solid red')),
    ).catch(() => {});
  }
  fs.mkdirSync('evidencias/capturas', { recursive: true });
  await page.screenshot({ path: `evidencias/capturas/${nombre}.png`, fullPage: true });
}

export { expect };
