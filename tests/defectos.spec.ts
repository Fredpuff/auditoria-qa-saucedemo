import { test, expect, evidencia } from './fixtures';
import { LoginPage } from './pages/LoginPage';
import { InventoryPage } from './pages/InventoryPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import usuarios from './data/usuarios.json';
import productos from './data/productos.json';

// Pruebas que reproducen defectos reales. Cada una afirma el comportamiento ESPERADO
// (el de standard_user) y por eso falla mientras el defecto exista.

const porNombre = productos.map((p) => p.nombre).sort((a, b) => a.localeCompare(b));

// Hace clic en Add to cart y luego en Remove en cada producto; devuelve los que no respondieron
async function probarBotones(page: any) {
  const inv = new InventoryPage(page);
  const sinRespuesta: string[] = [];
  for (const p of productos) {
    await inv.boton(p.nombre).click();
    if ((await inv.boton(p.nombre).textContent()) !== 'Remove') sinRespuesta.push(`Add to cart: ${p.nombre}`);
  }
  for (const p of productos) {
    if ((await inv.boton(p.nombre).textContent()) !== 'Remove') continue;
    await inv.boton(p.nombre).click();
    if ((await inv.boton(p.nombre).textContent()) !== 'Add to cart') sinRespuesta.push(`Remove: ${p.nombre}`);
  }
  return sinRespuesta;
}

async function irAlCheckout(page: any, producto = 'Sauce Labs Backpack') {
  const inv = new InventoryPage(page);
  await inv.agregar(producto);
  await inv.irAlCarrito();
  await new CartPage(page).irAlCheckout();
}

test.describe('problem_user', () => {
  test.beforeEach(async ({ page }) => {
    await new LoginPage(page).loginCompleto(usuarios.problem);
  });

  test('CP-42 | BUG-02 | ordenar Z-A con problem_user', { tag: '@defecto' }, async ({ page }) => {
    const inv = new InventoryPage(page);
    await inv.ordenar('za');
    await evidencia(page, 'BUG-02', inv.nombres);
    expect(await inv.listaNombres()).toEqual([...porNombre].reverse());
  });

  test('CP-43 | BUG-03 | Add to cart y Remove responden en todos los productos con problem_user', { tag: '@defecto' }, async ({ page }) => {
    const sinRespuesta = await probarBotones(page);
    await evidencia(page, 'BUG-03', new InventoryPage(page).botones);
    expect(sinRespuesta, 'botones que no respondieron').toEqual([]);
  });

  test('CP-44 | BUG-04 | escribir el apellido no debe cambiar el nombre con problem_user', { tag: '@defecto' }, async ({ page }) => {
    const co = new CheckoutPage(page);
    await irAlCheckout(page);
    await co.llenar('Ana', 'Perez', '110111', true);
    await evidencia(page, 'BUG-04', page.locator('[data-test="firstName"], [data-test="lastName"]'));
    expect(await co.valores()).toEqual({ nombre: 'Ana', apellido: 'Perez', postal: '110111' });
  });

  test('CP-45 | BUG-05 | el detalle corresponde al producto seleccionado con problem_user', { tag: '@defecto' }, async ({ page }) => {
    const inv = new InventoryPage(page);
    const errores: string[] = [];
    for (const p of productos) {
      await inv.item(p.nombre).getByTestId('inventory-item-name').click();
      const mostrado = await page.getByTestId('inventory-item-name').textContent().catch(() => null);
      if (mostrado !== p.nombre) errores.push(`clic en "${p.nombre}" muestra "${mostrado}"`);
      await inv.abrir();
    }
    await inv.item(productos[0].nombre).getByTestId('inventory-item-name').click();
    await evidencia(page, 'BUG-05', page.getByTestId('inventory-item-name'));
    expect(errores, 'productos con detalle equivocado').toEqual([]);
  });

  test('CP-46 | BUG-06 | el enlace About lleva a una pagina valida con problem_user', { tag: '@defecto' }, async ({ page }) => {
    const inv = new InventoryPage(page);
    await inv.abrirMenu();
    const about = page.getByTestId('about-sidebar-link');
    const href = (await about.getAttribute('href')) || '';
    const respuesta = await page.request.get(href);
    await evidencia(page, 'BUG-06', about);
    test.info().annotations.push({ type: 'enlace About', description: `${href} -> HTTP ${respuesta.status()}` });
    expect(respuesta.status(), `estado HTTP de ${href}`).toBeLessThan(400);
  });
});

test.describe('error_user', () => {
  test.beforeEach(async ({ page }) => {
    await new LoginPage(page).loginCompleto(usuarios.error);
  });

  test('CP-47 | BUG-08 | Add to cart y Remove responden en todos los productos con error_user', { tag: '@defecto' }, async ({ page, registro }) => {
    const sinRespuesta = await probarBotones(page);
    await evidencia(page, 'BUG-08', new InventoryPage(page).botones);
    test.info().annotations.push({ type: 'excepciones', description: registro.filter((e) => e.startsWith('[excepcion]')).join(' | ') });
    expect(sinRespuesta, 'botones que no respondieron').toEqual([]);
  });

  test('CP-48 | BUG-09 | el campo Last Name acepta texto con error_user', { tag: '@defecto' }, async ({ page }) => {
    const co = new CheckoutPage(page);
    await irAlCheckout(page);
    await co.llenar('Ana', 'Perez', '110111', true);
    await evidencia(page, 'BUG-09', co.apellido);
    expect((await co.valores()).apellido).toBe('Perez');
  });

  test('CP-49 | BUG-10 | Finish completa la compra con error_user', { tag: '@defecto' }, async ({ page }) => {
    const co = new CheckoutPage(page);
    await irAlCheckout(page);
    await co.llenar('Ana', 'Perez', '110111', true);
    await co.continuar.click();
    await expect(page).toHaveURL(/checkout-step-two\.html$/);
    await co.finalizar.click();
    await evidencia(page, 'BUG-10', co.finalizar);
    await expect(page).toHaveURL(/checkout-complete\.html$/);
    await expect(co.confirmacion).toHaveText('Thank you for your order!');
  });
});

test('CP-50 | BUG-11 | el login de performance_glitch_user tarda menos de 2000 ms', { tag: ['@defecto', '@rendimiento'] }, async ({ page }) => {
  test.setTimeout(120_000);
  const login = new LoginPage(page);
  const inv = new InventoryPage(page);
  const tiempos: Record<string, number[]> = { standard_user: [], performance_glitch_user: [] };
  // 5 repeticiones por usuario: desde el clic en Login hasta que se ve el catalogo
  for (const usuario of Object.keys(tiempos)) {
    for (let i = 0; i < 5; i++) {
      await page.context().clearCookies();
      await login.abrir();
      await login.usuario.fill(usuario);
      await login.password.fill(usuarios.password);
      const inicio = Date.now();
      await login.boton.click();
      await expect(inv.items.first()).toBeVisible({ timeout: 30_000 });
      tiempos[usuario].push(Date.now() - inicio);
    }
  }
  const promedio = (a: number[]) => Math.round(a.reduce((s, x) => s + x, 0) / a.length);
  const resumen = { tiempos, promedio_standard: promedio(tiempos.standard_user), promedio_performance: promedio(tiempos.performance_glitch_user) };
  await test.info().attach('tiempos-login.json', { body: JSON.stringify(resumen, null, 2), contentType: 'application/json' });
  await evidencia(page, 'BUG-11');
  // Umbral de 2000 ms: limite usual para que una accion se perciba como fluida (ver plan de pruebas)
  expect(resumen.promedio_standard).toBeLessThan(2000);
  expect(resumen.promedio_performance, `tiempos: ${tiempos.performance_glitch_user.join(', ')} ms`).toBeLessThan(2000);
});

test('CP-51 | BUG-13 | los elementos de visual_user estan alineados igual que en standard_user', { tag: '@defecto' }, async ({ page }) => {
  const login = new LoginPage(page);
  const inv = new InventoryPage(page);
  // Toma posiciones de referencia con standard_user
  const medir = async () => ({
    carrito: await inv.carrito.boundingBox(),
    alineacionNombres: await inv.nombres.evaluateAll((els) => els.map((e) => getComputedStyle(e).textAlign)),
    botonesX: await inv.botones.evaluateAll((els) => els.map((e) => Math.round(e.getBoundingClientRect().right))),
  });
  await login.loginCompleto(usuarios.standard);
  const base = await medir();
  await page.context().clearCookies();
  await login.loginCompleto(usuarios.visual);
  const visual = await medir();
  const diferencias: string[] = [];
  if (Math.abs(base.carrito!.x - visual.carrito!.x) > 5 || Math.abs(base.carrito!.y - visual.carrito!.y) > 5)
    diferencias.push(`icono del carrito en (${Math.round(visual.carrito!.x)}, ${Math.round(visual.carrito!.y)}) y no en (${base.carrito!.x}, ${base.carrito!.y})`);
  visual.alineacionNombres.forEach((a, i) => { if (a !== base.alineacionNombres[i]) diferencias.push(`nombre ${i + 1} alineado "${a}"`); });
  visual.botonesX.forEach((x, i) => { if (Math.abs(x - base.botonesX[i]) > 5) diferencias.push(`boton ${i + 1} desplazado ${x - base.botonesX[i]} px`); });
  await evidencia(page, 'BUG-13', page.locator('.shopping_cart_link, .align_right, .btn_inventory_misaligned'));
  expect(diferencias, 'diferencias visuales frente a standard_user').toEqual([]);
});

test('CP-53 | BUG-18 | las paginas internas responden HTTP 200 al abrirlas directamente', { tag: '@defecto' }, async ({ page }) => {
  await new LoginPage(page).loginCompleto(usuarios.standard);
  const estados: string[] = [];
  for (const ruta of ['/inventory.html', '/cart.html', '/checkout-step-one.html']) {
    const r = await page.goto(ruta);
    estados.push(`${ruta} -> ${r?.status()}`);
  }
  test.info().annotations.push({ type: 'estados HTTP', description: estados.join(' | ') });
  await evidencia(page, 'BUG-18');
  expect(estados).toEqual(['/inventory.html -> 200', '/cart.html -> 200', '/checkout-step-one.html -> 200']);
});
