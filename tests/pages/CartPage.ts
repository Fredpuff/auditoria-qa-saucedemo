import { Page, Locator } from '@playwright/test';

// Pagina del carrito
export class CartPage {
  readonly items: Locator;
  readonly checkout: Locator;
  readonly seguirComprando: Locator;

  constructor(private page: Page) {
    this.items = page.getByTestId('inventory-item');
    this.checkout = page.getByTestId('checkout');
    this.seguirComprando = page.getByTestId('continue-shopping');
  }

  async abrir() {
    await this.page.goto('/cart.html');
  }

  async nombres() {
    return this.page.getByTestId('inventory-item-name').allTextContents();
  }

  async irAlCheckout() {
    await this.checkout.click();
  }
}
