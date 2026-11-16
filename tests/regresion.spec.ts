import { test, expect, evidencia } from './fixtures';
import { LoginPage } from './pages/LoginPage';
import { InventoryPage } from './pages/InventoryPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import usuarios from './data/usuarios.json';
import productos from './data/productos.json';

// Regresion: el MISMO flujo de compra parametrizado por usuario.
// standard_user debe pasar; los demas fallan en el primer paso afectado por su defecto.
const casos = [
  { id: 'CP-38', bug: '', usuario: usuarios.standard },
  { id: 'CP-39', bug: 'BUG-01', usuario: usuarios.problem },
  { id: 'CP-40', bug: 'BUG-07', usuario: usuarios.error },
  { id: 'CP-41', bug: 'BUG-12', usuario: usuarios.visual },
];
const porNombre = [...productos].sort((a, b) => a.nombre.localeCompare(b.nombre));

for (const c of casos) {
  const titulo = [c.id, c.bug, `regresion del flujo de compra con ${c.usuario}`].filter(Boolean).join(' | ');
  test(titulo, { tag: ['@regresion', c.bug ? '@defecto' : '@smoke'] }, async ({ page }) => {
    const inv = new InventoryPage(page);
    const co = new CheckoutPage(page);
    const captura = c.bug || c.id;
    await new LoginPage(page).loginCompleto(c.usuario);

    await test.step('1. los precios del catalogo son los oficiales', async () => {
      const precios = await inv.listaPrecios();
      if (c.bug === 'BUG-12') await evidencia(page, captura, inv.precios);
      expect(precios).toEqual(porNombre.map((p) => p.precio));
    });

    await test.step('2. cada producto muestra su propia imagen', async () => {
      const imgs = await inv.imagenes();
      if (c.bug === 'BUG-01') await evidencia(page, captura, inv.items.locator('img'));
      imgs.forEach((src, i) => expect(src, porNombre[i].nombre).toContain(porNombre[i].imagen));
    });

    await test.step('3. el ordenamiento Z-A funciona', async () => {
      await inv.ordenar('za');
      const nombres = await inv.listaNombres();
      if (c.bug === 'BUG-07') await evidencia(page, captura, inv.orden);
      expect(nombres).toEqual(porNombre.map((p) => p.nombre).reverse());
      await inv.ordenar('az');
    });

    await test.step('4. agregar 2 productos al carrito', async () => {
      await inv.agregar('Sauce Labs Backpack');
      await inv.agregar('Sauce Labs Onesie');
      await expect(inv.badge).toHaveText('2');
    });

    await test.step('5. llenar los datos del comprador', async () => {
      await inv.irAlCarrito();
      await new CartPage(page).irAlCheckout();
      await co.llenar('Ana', 'Perez', '110111', true);
      expect(await co.valores()).toEqual({ nombre: 'Ana', apellido: 'Perez', postal: '110111' });
      await co.continuar.click();
    });

    await test.step('6. el resumen calcula bien subtotal, impuesto y total', async () => {
      // 29.99 + 7.99 = 37.98; impuesto 8 % = 3.04; total = 41.02
      expect(await co.montos()).toEqual({ subtotal: 37.98, impuesto: 3.04, total: 41.02 });
    });

    await test.step('7. Finish confirma la compra', async () => {
      await co.finalizar.click();
      await expect(co.confirmacion).toHaveText('Thank you for your order!');
      if (!c.bug) await evidencia(page, captura);
    });
  });
}
