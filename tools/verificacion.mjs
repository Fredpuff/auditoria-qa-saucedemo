// Verificacion puntual de hallazgos dudosos (3 repeticiones cada uno).
import { chromium } from '@playwright/test';
const BASE = 'https://www.saucedemo.com';
const browser = await chromium.launch();
const res = { back: [], visualCart: [], problemAbout: [], resetBtn: [] };

async function login(page, user) {
  await page.goto(BASE);
  await page.fill('[data-test="username"]', user);
  await page.fill('[data-test="password"]', 'secret_sauce');
  await page.click('[data-test="login-button"]');
  await page.waitForURL(/inventory/);
}

for (let i = 0; i < 3; i++) {
  // Back despues de logout
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    await login(page, 'standard_user');
    await page.click('#react-burger-menu-btn');
    await page.click('[data-test="logout-sidebar-link"]');
    await page.waitForURL(BASE + '/');
    const cookiesTrasLogout = (await ctx.cookies()).map(c => c.name);
    await page.goBack();
    await page.waitForTimeout(800);
    const url = page.url();
    const productosVisibles = await page.locator('[data-test="inventory-item"]').count();
    const loginVisible = await page.locator('[data-test="login-button"]').count();
    // intenta interactuar
    let agrego = null;
    if (productosVisibles) {
      await page.click('[data-test="add-to-cart-sauce-labs-backpack"]').catch(() => {});
      agrego = await page.locator('[data-test="remove-sauce-labs-backpack"]').count();
      await page.reload();
      await page.waitForTimeout(500);
    }
    res.back.push({ cookiesTrasLogout, url, productosVisibles, loginVisible, agrego, urlTrasRecarga: page.url() });
    await ctx.close();
  }
  // Posicion icono carrito visual_user vs standard_user
  {
    const box = {};
    for (const u of ['standard_user', 'visual_user']) {
      const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
      const page = await ctx.newPage();
      await login(page, u);
      box[u] = await page.locator('[data-test="shopping-cart-link"]').boundingBox();
      await ctx.close();
    }
    res.visualCart.push(box);
  }
  // About de problem_user
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    await login(page, 'problem_user');
    await page.click('#react-burger-menu-btn');
    const [resp] = await Promise.all([
      page.waitForNavigation({ timeout: 20000 }).catch(() => null),
      page.click('[data-test="about-sidebar-link"]'),
    ]);
    res.problemAbout.push({ status: resp ? resp.status() : null, url: page.url(), title: await page.title() });
    await ctx.close();
  }
  // Reset App State deja el boton Remove
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    await login(page, 'standard_user');
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('#react-burger-menu-btn');
    await page.click('[data-test="reset-sidebar-link"]');
    await page.waitForTimeout(500);
    res.resetBtn.push({
      badge: await page.locator('[data-test="shopping-cart-badge"]').count(),
      remove: await page.locator('[data-test="remove-sauce-labs-backpack"]').count(),
      storage: await page.evaluate(() => localStorage.getItem('cart-contents')),
    });
    await ctx.close();
  }
}
await browser.close();
console.log(JSON.stringify(res, null, 1));
