import { Page, Locator } from '@playwright/test';

// Catalogo de productos, encabezado y menu lateral
export class InventoryPage {
  readonly items: Locator;
  readonly nombres: Locator;
  readonly precios: Locator;
  readonly orden: Locator;
  readonly badge: Locator;
  readonly carrito: Locator;
  readonly titulo: Locator;
  readonly botones: Locator;

  constructor(private page: Page) {
    this.items = page.getByTestId('inventory-item');
    this.nombres = page.getByTestId('inventory-item-name');
    this.precios = page.getByTestId('inventory-item-price');
    this.orden = page.getByTestId('product-sort-container');
    this.badge = page.getByTestId('shopping-cart-badge');
    this.carrito = page.getByTestId('shopping-cart-link');
    this.titulo = page.getByTestId('title');
    // Botones Add to cart / Remove de cada tarjeta (los enlaces de imagen y titulo tambien tienen rol button)
    this.botones = this.items.getByRole('button', { name: /^(Add to cart|Remove)$/ });
  }

  async abrir() {
    await this.page.goto('/inventory.html');
  }

  item(nombre: string) {
    return this.items.filter({ hasText: nombre });
  }

  boton(nombre: string) {
    return this.item(nombre).getByRole('button', { name: /^(Add to cart|Remove)$/ });
  }

  async agregar(nombre: string) {
    await this.page.getByTestId(`add-to-cart-${slug(nombre)}`).click();
  }

  async quitar(nombre: string) {
    await this.page.getByTestId(`remove-${slug(nombre)}`).click();
  }

  async ordenar(opcion: 'az' | 'za' | 'lohi' | 'hilo') {
    await this.orden.selectOption(opcion);
  }

  async listaNombres() {
    return this.nombres.allTextContents();
  }

  async listaPrecios() {
    return (await this.precios.allTextContents()).map((p) => Number(p.replace('$', '')));
  }

  async imagenes() {
    return this.items.locator('img').evaluateAll((imgs) => imgs.map((i) => i.getAttribute('src') || ''));
  }

  async cantidadBadge() {
    if ((await this.badge.count()) === 0) return 0;
    return Number(await this.badge.textContent());
  }

  async abrirMenu() {
    await this.page.getByRole('button', { name: 'Open Menu' }).click();
  }

  async opcionMenu(testId: 'inventory-sidebar-link' | 'about-sidebar-link' | 'logout-sidebar-link' | 'reset-sidebar-link') {
    await this.abrirMenu();
    await this.page.getByTestId(testId).click();
  }

  async irAlCarrito() {
    await this.carrito.click();
  }
}

// Convierte el nombre del producto al formato de los atributos data-test
export function slug(nombre: string) {
  return nombre.toLowerCase().replace(/\s+/g, '-');
}
