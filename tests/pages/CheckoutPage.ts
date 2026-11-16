import { Page, Locator } from '@playwright/test';

// Checkout: paso 1 (informacion), paso 2 (resumen) y pagina de compra completada
export class CheckoutPage {
  readonly nombre: Locator;
  readonly apellido: Locator;
  readonly postal: Locator;
  readonly continuar: Locator;
  readonly cancelar: Locator;
  readonly error: Locator;
  readonly subtotal: Locator;
  readonly impuesto: Locator;
  readonly total: Locator;
  readonly finalizar: Locator;
  readonly confirmacion: Locator;
  readonly volverInicio: Locator;

  constructor(private page: Page) {
    this.nombre = page.getByPlaceholder('First Name');
    this.apellido = page.getByPlaceholder('Last Name');
    this.postal = page.getByPlaceholder('Zip/Postal Code');
    this.continuar = page.getByTestId('continue');
    this.cancelar = page.getByTestId('cancel');
    this.error = page.getByTestId('error');
    this.subtotal = page.getByTestId('subtotal-label');
    this.impuesto = page.getByTestId('tax-label');
    this.total = page.getByTestId('total-label');
    this.finalizar = page.getByTestId('finish');
    this.confirmacion = page.getByTestId('complete-header');
    this.volverInicio = page.getByTestId('back-to-products');
  }

  // escribir=true simula a un usuario tecleando letra por letra
  async llenar(nombre: string, apellido: string, postal: string, escribir = false) {
    for (const [campo, valor] of [[this.nombre, nombre], [this.apellido, apellido], [this.postal, postal]] as const) {
      if (!valor) continue;
      if (escribir) await campo.pressSequentially(valor);
      else await campo.fill(valor);
    }
  }

  async valores() {
    return {
      nombre: await this.nombre.inputValue(),
      apellido: await this.apellido.inputValue(),
      postal: await this.postal.inputValue(),
    };
  }

  // Convierte "Item total: $29.99" en 29.99
  async montos() {
    const num = async (l: Locator) => Number(((await l.textContent()) || '').replace(/[^0-9.]/g, ''));
    return { subtotal: await num(this.subtotal), impuesto: await num(this.impuesto), total: await num(this.total) };
  }
}
