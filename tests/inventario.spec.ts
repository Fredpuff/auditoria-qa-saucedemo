import { test, expect, evidencia } from './fixtures';
import { LoginPage } from './pages/LoginPage';
import { InventoryPage } from './pages/InventoryPage';
import usuarios from './data/usuarios.json';
import productos from './data/productos.json';

const porNombre = [...productos].map((p) => p.nombre).sort((a, b) => a.localeCompare(b));
const precios = productos.map((p) => p.precio);

test.describe('Catalogo, ordenamiento y detalle', () => {
  test.beforeEach(async ({ page }) => {
    await new LoginPage(page).loginCompleto(usuarios.standard);
  });

  test('CP-03 | ordenar por nombre A-Z y Z-A', { tag: '@positiva' }, async ({ page }) => {
    const inv = new InventoryPage(page);
    await inv.ordenar('za');
    expect(await inv.listaNombres()).toEqual([...porNombre].reverse());
    await inv.ordenar('az');
    expect(await inv.listaNombres()).toEqual(porNombre);
    await evidencia(page, 'CP-03');
  });

  test('CP-04 | ordenar por precio menor a mayor y mayor a menor', { tag: '@positiva' }, async ({ page }) => {
    const inv = new InventoryPage(page);
    await inv.ordenar('lohi');
    expect(await inv.listaPrecios()).toEqual([...precios].sort((a, b) => a - b));
    await inv.ordenar('hilo');
    expect(await inv.listaPrecios()).toEqual([...precios].sort((a, b) => b - a));
    await evidencia(page, 'CP-04');
  });

  test('CP-07 | el detalle muestra el producto seleccionado', { tag: '@positiva' }, async ({ page }) => {
    const inv = new InventoryPage(page);
    for (const p of productos) {
      await inv.item(p.nombre).getByTestId('inventory-item-name').click();
      await expect(page).toHaveURL(new RegExp(`inventory-item\\.html\\?id=${p.id}$`));
      await expect(page.getByTestId('inventory-item-name')).toHaveText(p.nombre);
      await expect(page.getByTestId('inventory-item-price')).toHaveText(`$${p.precio}`);
      await page.getByTestId('back-to-products').click();
    }
    await inv.item(productos[0].nombre).getByTestId('inventory-item-name').click();
    await evidencia(page, 'CP-07');
  });

  test('CP-56 | la opcion All Items del menu vuelve al catalogo', { tag: '@positiva' }, async ({ page }) => {
    const inv = new InventoryPage(page);
    await inv.irAlCarrito();
    await expect(page).toHaveURL(/cart\.html$/);
    await inv.opcionMenu('inventory-sidebar-link');
    await expect(page).toHaveURL(/inventory\.html$/);
    await expect(inv.items).toHaveCount(6);
    // El menu se cierra solo al escoger la opcion
    await expect(page.getByTestId('close-menu')).toBeHidden();
    await evidencia(page, 'CP-56');
  });

  test('CP-57 | Dynamic Catalog muestra productos en Lazy Load, Spinner y Slider', { tag: '@positiva' }, async ({ page }) => {
    const inv = new InventoryPage(page);
    const nombres = productos.map((p) => p.nombre);
    // Lazy Load
    await inv.abrirMenu();
    await page.getByTestId('dynamic-catalog-sidebar-link').click();
    await page.getByTestId('dynamic-catalog-lazy-load-link').click();
    await expect(page).toHaveURL(/dynamic-catalog-lazy-load\.html$/);
    await expect(page.getByTestId('lazy-load-item-0-name')).toBeVisible({ timeout: 15_000 });
    expect(nombres).toContain(await page.getByTestId('lazy-load-item-0-name').textContent());
    // Spinner: primero carga y luego muestra los productos
    await page.goto('/dynamic-catalog-spinner.html');
    await expect(page.getByTestId('spinner-item-0-name')).toBeVisible({ timeout: 15_000 });
    expect(nombres).toContain(await page.getByTestId('spinner-item-0-name').textContent());
    // Slider: al pulsar otro punto cambia el producto mostrado
    await page.goto('/dynamic-catalog-slider.html');
    const nombre = page.getByTestId('dynamic-catalog-slider-item-name');
    await expect(nombre).toBeVisible({ timeout: 15_000 });
    const primero = await nombre.textContent();
    await page.getByTestId('dynamic-catalog-slider-dot-1').click();
    await expect(nombre).not.toHaveText(primero || '');
    expect(nombres).toContain(await nombre.textContent());
    await evidencia(page, 'CP-57');
  });
});
