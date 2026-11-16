// Sesion exploratoria automatizada: recorre la app con cada usuario y guarda observaciones crudas.
// Uso: node tools/exploracion.mjs   (guarda capturas y exploracion.json en evidencias/exploracion)
import { chromium } from '@playwright/test';
import fs from 'fs';

const BASE = process.env.BASE_URL || 'https://www.saucedemo.com';
const OUT = 'evidencias/exploracion';
fs.mkdirSync(OUT, { recursive: true });
const out = { fecha: new Date().toISOString() };
const browser = await chromium.launch();

async function nueva(user) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  const log = { console: [], pageerror: [], http: [], dialogs: [] };
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') log.console.push(`${m.type()}: ${m.text()}`.slice(0, 300)); });
  page.on('pageerror', e => log.pageerror.push(e.message));
  page.on('response', r => { if (r.status() >= 400) log.http.push(`${r.status()} ${r.url()}`); });
  page.on('dialog', d => { log.dialogs.push(d.message()); d.accept(); });
  await page.goto(BASE);
  const t0 = Date.now();
  if (user) {
    await page.fill('[data-test="username"]', user);
    await page.fill('[data-test="password"]', 'secret_sauce');
    await page.click('[data-test="login-button"]');
    await page.waitForURL(/inventory/, { timeout: 15000 }).catch(() => {});
    await page.locator('[data-test="inventory-list"]').waitFor({ timeout: 15000 }).catch(() => {});
  }
  log.loginMs = Date.now() - t0;
  return { ctx, page, log };
}

async function catalogo(page) {
  return page.$$eval('[data-test="inventory-item"]', els => els.map(e => ({
    name: e.querySelector('[data-test="inventory-item-name"]')?.textContent,
    price: e.querySelector('[data-test="inventory-item-price"]')?.textContent,
    img: e.querySelector('img')?.getAttribute('src'),
    btn: e.querySelector('button')?.textContent,
    nameClass: e.querySelector('[data-test="inventory-item-name"]')?.className,
    btnClass: e.querySelector('button')?.className,
  })));
}

const slug = n => n.toLowerCase().replace(/\s+/g, '-');

for (const user of ['standard_user', 'problem_user', 'error_user', 'visual_user', 'performance_glitch_user', 'locked_out_user']) {
  const r = {};
  const { ctx, page, log } = await nueva(user);
  r.url = page.url();
  r.loginMs = log.loginMs;
  if (!/inventory/.test(page.url())) {
    r.error = await page.textContent('[data-test="error"]').catch(() => null);
    await page.screenshot({ path: `${OUT}/${user}-login.png` });
    out[user] = { ...r, ...log };
    await ctx.close();
    continue;
  }
  r.catalogo = await catalogo(page);
  r.carritoIconClass = await page.getAttribute('[data-test="shopping-cart-link"]', 'class').catch(() => null);
  await page.screenshot({ path: `${OUT}/${user}-inventario.png`, fullPage: true });

  // ordenamientos
  r.orden = {};
  for (const op of ['za', 'lohi', 'hilo', 'az']) {
    await page.selectOption('[data-test="product-sort-container"]', op).catch(e => { r.orden[op + '_err'] = e.message; });
    await page.waitForTimeout(300);
    r.orden[op] = (await catalogo(page)).map(i => `${i.name}|${i.price}`);
  }

  // agregar todos
  const nombres = r.catalogo.map(i => i.name);
  r.add = {};
  for (const n of nombres) {
    const b = page.locator(`[data-test="add-to-cart-${slug(n)}"]`);
    if (await b.count()) { await b.click(); await page.waitForTimeout(150); }
    r.add[n] = (await page.locator(`[data-test="remove-${slug(n)}"]`).count()) > 0;
  }
  r.badgeTrasAgregar = await page.locator('[data-test="shopping-cart-badge"]').textContent({ timeout: 1000 }).catch(() => null);
  // quitar todos
  r.remove = {};
  for (const n of nombres) {
    const b = page.locator(`[data-test="remove-${slug(n)}"]`);
    if (await b.count()) {
      await b.click(); await page.waitForTimeout(150);
      r.remove[n] = (await page.locator(`[data-test="add-to-cart-${slug(n)}"]`).count()) > 0;
    }
  }
  r.badgeTrasQuitar = await page.locator('[data-test="shopping-cart-badge"]').textContent({ timeout: 1000 }).catch(() => null);

  // detalle de producto
  await page.goto(BASE + '/inventory.html');
  const primero = await page.locator('[data-test="inventory-item-name"]').first().textContent();
  await page.locator('[data-test="inventory-item-name"]').first().click();
  await page.waitForTimeout(400);
  r.detalle = { clic: primero, url: page.url(), mostrado: await page.textContent('[data-test="inventory-item-name"]', { timeout: 2000 }).catch(() => null) };
  await page.screenshot({ path: `${OUT}/${user}-detalle.png` });

  // checkout con la mochila (id 4)
  await page.goto(BASE + '/inventory.html');
  await page.evaluate(() => localStorage.removeItem('cart-contents'));
  await page.reload();
  await page.click('[data-test="add-to-cart-sauce-labs-backpack"]').catch(() => {});
  await page.click('[data-test="shopping-cart-link"]');
  r.carrito = await page.$$eval('[data-test="inventory-item-name"]', e => e.map(x => x.textContent));
  await page.click('[data-test="checkout"]');
  await page.locator('[data-test="firstName"]').pressSequentially('Ana');
  await page.locator('[data-test="lastName"]').pressSequentially('Perez');
  await page.locator('[data-test="postalCode"]').pressSequentially('110111');
  r.form = {
    first: await page.inputValue('[data-test="firstName"]'),
    last: await page.inputValue('[data-test="lastName"]'),
    postal: await page.inputValue('[data-test="postalCode"]'),
  };
  await page.screenshot({ path: `${OUT}/${user}-checkout1.png` });
  await page.click('[data-test="continue"]');
  await page.waitForTimeout(400);
  r.paso2Url = page.url();
  r.paso2Error = await page.textContent('[data-test="error"]', { timeout: 1000 }).catch(() => null);
  if (/step-two/.test(page.url())) {
    r.resumen = {
      sub: await page.textContent('[data-test="subtotal-label"]').catch(() => null),
      tax: await page.textContent('[data-test="tax-label"]').catch(() => null),
      total: await page.textContent('[data-test="total-label"]').catch(() => null),
    };
    await page.screenshot({ path: `${OUT}/${user}-checkout2.png` });
    await page.click('[data-test="finish"]');
    await page.waitForTimeout(600);
    r.finishUrl = page.url();
    r.completo = await page.textContent('[data-test="complete-header"]', { timeout: 1000 }).catch(() => null);
    r.badgeTrasCompra = await page.locator('[data-test="shopping-cart-badge"]').textContent({ timeout: 1000 }).catch(() => null);
    await page.screenshot({ path: `${OUT}/${user}-finish.png` });
  }

  // menu
  await page.goto(BASE + '/inventory.html');
  await page.click('#react-burger-menu-btn');
  await page.waitForTimeout(500);
  r.aboutHref = await page.getAttribute('[data-test="about-sidebar-link"]', 'href').catch(() => null);
  r.menuIconClass = await page.getAttribute('[data-test="open-menu"]', 'class').catch(() => null);
  await page.screenshot({ path: `${OUT}/${user}-menu.png` });
  out[user] = { ...r, ...log };
  await ctx.close();
}

// medicion de login, 5 repeticiones
out.tiempos = {};
for (const user of ['standard_user', 'performance_glitch_user']) {
  out.tiempos[user] = [];
  for (let i = 0; i < 5; i++) {
    const { ctx, log } = await nueva(user);
    out.tiempos[user].push(log.loginMs);
    await ctx.close();
  }
}

// validaciones generales con standard_user
{
  const g = {};
  const { ctx, page } = await nueva('standard_user');
  await page.click('[data-test="shopping-cart-link"]');
  await page.click('[data-test="checkout"]');
  await page.fill('[data-test="firstName"]', 'A'.repeat(300));
  await page.fill('[data-test="lastName"]', 'B');
  await page.fill('[data-test="postalCode"]', 'abc!@#');
  g.largoNombre = (await page.inputValue('[data-test="firstName"]')).length;
  g.maxlength = await page.getAttribute('[data-test="firstName"]', 'maxlength');
  await page.click('[data-test="continue"]');
  await page.waitForTimeout(400);
  g.vacioPaso2 = page.url();
  g.vacioResumen = await page.textContent('[data-test="total-label"]', { timeout: 1000 }).catch(() => null);
  await page.click('[data-test="finish"]', { timeout: 2000 }).catch(() => {});
  await page.waitForTimeout(400);
  g.vacioFinish = page.url();
  g.vacioHeader = await page.textContent('[data-test="complete-header"]', { timeout: 1000 }).catch(() => null);
  await page.screenshot({ path: `${OUT}/general-carrito-vacio-finish.png` });

  // reset app state con producto agregado
  await page.goto(BASE + '/inventory.html');
  await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
  await page.click('#react-burger-menu-btn');
  await page.click('[data-test="reset-sidebar-link"]');
  await page.waitForTimeout(400);
  g.resetBadge = await page.locator('[data-test="shopping-cart-badge"]').count();
  g.resetBotonRemove = await page.locator('[data-test="remove-sauce-labs-backpack"]').count();
  await page.screenshot({ path: `${OUT}/general-reset.png` });

  // persistencia tras logout y boton Back
  await page.reload();
  await page.click('[data-test="add-to-cart-sauce-labs-bike-light"]');
  await page.click('#react-burger-menu-btn');
  await page.click('[data-test="logout-sidebar-link"]');
  await page.waitForURL(BASE + '/');
  await page.goBack();
  await page.waitForTimeout(500);
  g.backTrasLogout = page.url();
  g.backError = await page.textContent('[data-test="error"]', { timeout: 1000 }).catch(() => null);
  await page.screenshot({ path: `${OUT}/general-back-logout.png` });
  await page.goto(BASE + '/checkout-step-two.html');
  g.directoSinSesion = page.url();
  g.directoError = await page.textContent('[data-test="error"]', { timeout: 1000 }).catch(() => null);
  await page.fill('[data-test="username"]', 'visual_user');
  await page.fill('[data-test="password"]', 'secret_sauce');
  await page.click('[data-test="login-button"]');
  await page.waitForURL(/inventory/);
  g.badgeOtroUsuario = await page.locator('[data-test="shopping-cart-badge"]').textContent({ timeout: 1000 }).catch(() => null);
  g.cookies = (await ctx.cookies()).map(c => `${c.name}=${c.value} exp=${c.expires}`);
  await ctx.close();
  out.general = g;
}

await browser.close();
fs.writeFileSync(`${OUT}/exploracion.json`, JSON.stringify(out, null, 2));
console.log('ok');
