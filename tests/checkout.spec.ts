import { test, expect, evidencia } from './fixtures';
import { LoginPage } from './pages/LoginPage';
import { InventoryPage } from './pages/InventoryPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import usuarios from './data/usuarios.json';
import productos from './data/productos.json';
import reglas from './data/checkout-decision.json';

const redondear = (n: number) => Math.round(n * 100) / 100;

test.describe('Checkout', () => {
  test.beforeEach(async ({ page }) => {
    await new LoginPage(page).loginCompleto(usuarios.standard);
  });

  // Agrega productos y llega al paso 1 del checkout
  async function hastaPasoUno(page: any, nombres: string[]) {
    const inv = new InventoryPage(page);
    for (const n of nombres) await inv.agregar(n);
    await inv.irAlCarrito();
    await new CartPage(page).irAlCheckout();
    await expect(page).toHaveURL(/checkout-step-one\.html$/);
  }

  test('CP-05 | compra completa con standard_user (smoke)', { tag: ['@smoke', '@positiva'] }, async ({ page }) => {
    const co = new CheckoutPage(page);
    await hastaPasoUno(page, ['Sauce Labs Backpack']);
    await co.llenar('Ana', 'Perez', '110111');
    await co.continuar.click();
    await expect(page).toHaveURL(/checkout-step-two\.html$/);
    await co.finalizar.click();
    await expect(page).toHaveURL(/checkout-complete\.html$/);
    await expect(co.confirmacion).toHaveText('Thank you for your order!');
    await evidencia(page, 'CP-05');
  });

  test('CP-09 | continuar el checkout sin datos muestra error', { tag: '@negativa' }, async ({ page }) => {
    const co = new CheckoutPage(page);
    await hastaPasoUno(page, ['Sauce Labs Backpack']);
    await co.continuar.click();
    await expect(co.error).toHaveText('Error: First Name is required');
    await expect(page).toHaveURL(/checkout-step-one\.html$/);
    await evidencia(page, 'CP-09');
  });

  test('CP-10 | BUG-14 | no se debe poder iniciar el checkout con el carrito vacio', { tag: ['@negativa', '@defecto'] }, async ({ page }) => {
    const inv = new InventoryPage(page);
    const cart = new CartPage(page);
    await inv.irAlCarrito();
    await expect(cart.items).toHaveCount(0);
    await cart.irAlCheckout();
    await evidencia(page, 'BUG-14');
    // Esperado: la aplicacion bloquea el checkout (permanece en el carrito o muestra un aviso)
    await expect(page).not.toHaveURL(/checkout-step-one\.html$/);
  });

  test('CP-11 | BUG-17 | el codigo postal no debe aceptar letras ni simbolos', { tag: ['@negativa', '@defecto'] }, async ({ page }) => {
    const co = new CheckoutPage(page);
    await hastaPasoUno(page, ['Sauce Labs Backpack']);
    await co.llenar('Ana', 'Perez', 'ABC!@#');
    await co.continuar.click();
    await evidencia(page, 'BUG-17', co.postal);
    // Esperado: mensaje de validacion y no avanza al resumen
    await expect(page).toHaveURL(/checkout-step-one\.html$/);
    await expect(co.error).toBeVisible();
  });

  test('CP-18 | valor limite: calculo de impuesto y total con 1 producto', { tag: '@valor-limite' }, async ({ page }) => {
    const co = new CheckoutPage(page);
    const p = productos[0];
    await hastaPasoUno(page, [p.nombre]);
    await co.llenar('Ana', 'Perez', '110111');
    await co.continuar.click();
    const m = await co.montos();
    const impuesto = redondear(p.precio * 0.08);
    expect(m.subtotal).toBe(p.precio);
    expect(m.impuesto).toBe(impuesto);
    expect(m.total).toBe(redondear(p.precio + impuesto));
    await evidencia(page, 'CP-18');
  });

  test('CP-19 | valor limite: calculo de impuesto y total con los 6 productos', { tag: '@valor-limite' }, async ({ page }) => {
    const co = new CheckoutPage(page);
    await hastaPasoUno(page, productos.map((p) => p.nombre));
    await co.llenar('Ana', 'Perez', '110111');
    await co.continuar.click();
    // Suma hecha a mano: 29.99 + 9.99 + 15.99 + 49.99 + 7.99 + 15.99 = 129.94
    const subtotal = redondear(productos.reduce((s, p) => s + p.precio, 0));
    const impuesto = redondear(subtotal * 0.08);
    const m = await co.montos();
    expect(subtotal).toBe(129.94);
    expect(m.subtotal).toBe(subtotal);
    expect(m.impuesto).toBe(impuesto);
    expect(m.total).toBe(redondear(subtotal + impuesto));
    await evidencia(page, 'CP-19');
  });

  // Longitud del nombre: 1 y 50 caracteres (rango normal) y 255 caracteres (extremo superior).
  // El valor 0 (vacio) se cubre en CP-09 y CP-28.
  for (const [id, largos] of [['CP-20', [1, 50]], ['CP-21', [255]]] as const) {
    test(`${id} | valor limite: First Name con ${largos.join(' y ')} caracteres`, { tag: '@valor-limite' }, async ({ page }) => {
      const co = new CheckoutPage(page);
      await hastaPasoUno(page, ['Sauce Labs Onesie']);
      for (const largo of largos) {
        await co.nombre.fill('');
        await co.llenar('A'.repeat(largo), 'Perez', '110111');
        expect((await co.valores()).nombre.length).toBe(largo);
      }
      await co.continuar.click();
      await expect(page).toHaveURL(/checkout-step-two\.html$/);
      await evidencia(page, id);
    });
  }

  // Tabla de decision del formulario de checkout
  for (const r of reglas) {
    test(`${r.id} | tabla de decision checkout ${r.regla}: ${r.condicion}`, { tag: '@tabla-decision' }, async ({ page }) => {
      const co = new CheckoutPage(page);
      await hastaPasoUno(page, ['Sauce Labs Backpack']);
      await co.llenar(r.first, r.last, r.postal);
      await co.continuar.click();
      if (r.esperado === 'continua') await expect(page).toHaveURL(/checkout-step-two\.html$/);
      else {
        await expect(co.error).toHaveText(r.mensaje);
        await expect(page).toHaveURL(/checkout-step-one\.html$/);
      }
      await evidencia(page, r.id);
    });
  }

  test('CP-32 | transicion valida Inventario > Carrito > Informacion > Resumen > Completado > Inventario', { tag: '@transicion' }, async ({ page }) => {
    const co = new CheckoutPage(page);
    const inv = new InventoryPage(page);
    await hastaPasoUno(page, ['Sauce Labs Bolt T-Shirt']);
    await co.llenar('Ana', 'Perez', '110111');
    await co.continuar.click();
    await expect(page).toHaveURL(/checkout-step-two\.html$/);
    await co.finalizar.click();
    await expect(page).toHaveURL(/checkout-complete\.html$/);
    await co.volverInicio.click();
    await expect(page).toHaveURL(/inventory\.html$/);
    await expect(inv.badge).toHaveCount(0);
    await evidencia(page, 'CP-32');
  });

  test('CP-33 | transicion Cancel en Informacion vuelve al carrito y en Resumen al inventario', { tag: '@transicion' }, async ({ page }) => {
    const co = new CheckoutPage(page);
    const inv = new InventoryPage(page);
    await hastaPasoUno(page, ['Sauce Labs Bolt T-Shirt']);
    await co.cancelar.click();
    await expect(page).toHaveURL(/cart\.html$/);
    // Continue Shopping desde el carrito vuelve al inventario
    await new CartPage(page).seguirComprando.click();
    await expect(page).toHaveURL(/inventory\.html$/);
    await inv.irAlCarrito();
    await new CartPage(page).irAlCheckout();
    await co.llenar('Ana', 'Perez', '110111');
    await co.continuar.click();
    await co.cancelar.click();
    await expect(page).toHaveURL(/inventory\.html$/);
    // El carrito se conserva al cancelar
    await expect(inv.badge).toHaveText('1');
    await evidencia(page, 'CP-33');
  });

  test('CP-35 | BUG-19 | no se debe mostrar la confirmacion de compra entrando directo a /checkout-complete.html', { tag: ['@transicion', '@defecto'] }, async ({ page }) => {
    const co = new CheckoutPage(page);
    // Con sesion iniciada y sin haber hecho ninguna compra
    await page.goto('/checkout-complete.html');
    await evidencia(page, 'BUG-19', co.confirmacion);
    // Esperado: transicion invalida, la app redirige y no confirma una orden inexistente
    await expect(co.confirmacion).toHaveCount(0);
  });
});

test('CP-34 | transicion invalida: /checkout-step-two.html sin sesion redirige al login', { tag: ['@transicion', '@negativa'] }, async ({ page }) => {
  const login = new LoginPage(page);
  await page.goto('/checkout-step-two.html');
  await expect(login.boton).toBeVisible();
  await expect(login.error).toHaveText("Epic sadface: You can only access '/checkout-step-two.html' when you are logged in.");
  await evidencia(page, 'CP-34');
});
