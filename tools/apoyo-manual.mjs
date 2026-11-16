// Apoyo para los casos manuales CP-54 (vista movil) y CP-55 (teclado y textos alternativos).
// Toma las capturas que luego revisa una persona; no decide aprobado/fallido por si solo.
import { chromium } from '@playwright/test';
import fs from 'fs';
const BASE = 'https://www.saucedemo.com';
const OUT = 'evidencias/capturas';
fs.mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();

// CP-54: recorrido en un telefono de 375 px de ancho
{
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  await page.goto(BASE);
  await page.screenshot({ path: `${OUT}/CP-54-login-movil.png` });
  await page.fill('[data-test="username"]', 'standard_user');
  await page.fill('[data-test="password"]', 'secret_sauce');
  await page.click('[data-test="login-button"]');
  await page.waitForURL(/inventory/);
  await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
  await page.screenshot({ path: `${OUT}/CP-54-inventario-movil.png`, fullPage: true });
  await page.click('[data-test="shopping-cart-link"]');
  await page.click('[data-test="checkout"]');
  await page.screenshot({ path: `${OUT}/CP-54-checkout-movil.png` });
  const anchoDoc = await page.evaluate(() => document.documentElement.scrollWidth);
  console.log('CP-54 ancho del documento en movil:', anchoDoc, 'viewport:', page.viewportSize().width);
  await ctx.close();
}

// CP-55: login solo con teclado y revision de textos alternativos
{
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto(BASE);
  await page.keyboard.press('Tab');
  await page.keyboard.type('standard_user');
  await page.keyboard.press('Tab');
  await page.keyboard.type('secret_sauce');
  await page.keyboard.press('Enter');
  await page.waitForURL(/inventory/, { timeout: 10000 }).catch(() => {});
  console.log('CP-55 login con teclado ->', page.url());
  const sinAlt = await page.$$eval('img', (imgs) => imgs.filter((i) => !i.getAttribute('alt')).length);
  const totalImg = await page.$$eval('img', (imgs) => imgs.length);
  console.log(`CP-55 imagenes sin alt: ${sinAlt} de ${totalImg}`);
  await page.screenshot({ path: `${OUT}/CP-55-teclado.png` });
  await ctx.close();
}
await browser.close();
