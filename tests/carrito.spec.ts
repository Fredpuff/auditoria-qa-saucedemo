import { test, expect, evidencia } from './fixtures';
import { LoginPage } from './pages/LoginPage';
import { InventoryPage } from './pages/InventoryPage';
import { CartPage } from './pages/CartPage';
import usuarios from './data/usuarios.json';
import productos from './data/productos.json';

test.describe('Carrito', () => {
  test.beforeEach(async ({ page }) => {
    await new LoginPage(page).loginCompleto(usuarios.standard);
  });

  test('CP-02 | agregar un producto al carrito', { tag: ['@positiva', '@smoke'] }, async ({ page }) => {
    const inv = new InventoryPage(page);
    await inv.agregar('Sauce Labs Backpack');
    await expect(inv.badge).toHaveText('1');
    await expect(inv.boton('Sauce Labs Backpack')).toHaveText('Remove');
    await evidencia(page, 'CP-02');
  });

  // Valores limite del carrito: 0, 1, 5 y 6 (todos los productos)
  for (const cantidad of [0, 1, 5, 6]) {
    const id = { 0: 'CP-14', 1: 'CP-15', 5: 'CP-16', 6: 'CP-17' }[cantidad];
    test(`${id} | valor limite: carrito con ${cantidad} productos y contador del badge`, { tag: '@valor-limite' }, async ({ page }) => {
      const inv = new InventoryPage(page);
      const cart = new CartPage(page);
      for (const p of productos.slice(0, cantidad)) await inv.agregar(p.nombre);
      if (cantidad === 0) await expect(inv.badge).toHaveCount(0);
      else await expect(inv.badge).toHaveText(String(cantidad));
      if (cantidad === 6) await expect(page.getByRole('button', { name: 'Add to cart' })).toHaveCount(0);
      await inv.irAlCarrito();
      await expect(cart.items).toHaveCount(cantidad);
      await evidencia(page, id!);
    });
  }

  test('CP-37 | BUG-15 | Reset App State debe vaciar el carrito y restaurar los botones', { tag: ['@transicion', '@defecto'] }, async ({ page }) => {
    const inv = new InventoryPage(page);
    await inv.agregar('Sauce Labs Backpack');
    await expect(inv.badge).toHaveText('1');
    await inv.opcionMenu('reset-sidebar-link');
    await expect(inv.badge).toHaveCount(0);
    await evidencia(page, 'BUG-15', inv.boton('Sauce Labs Backpack'));
    // Esperado: con el carrito vacio el boton vuelve a "Add to cart"
    await expect(inv.boton('Sauce Labs Backpack')).toHaveText('Add to cart');
  });

  test('CP-52 | BUG-16 | el carrito de un usuario no debe aparecer al iniciar sesion con otro', { tag: '@defecto' }, async ({ page }) => {
    const login = new LoginPage(page);
    const inv = new InventoryPage(page);
    await inv.agregar('Sauce Labs Bike Light');
    await expect(inv.badge).toHaveText('1');
    await inv.opcionMenu('logout-sidebar-link');
    await login.ingresar(usuarios.visual);
    await page.waitForURL('**/inventory.html');
    await evidencia(page, 'BUG-16', inv.badge);
    // Esperado: visual_user empieza con el carrito vacio
    await expect(inv.badge).toHaveCount(0);
  });
});
