import { Page, Locator } from '@playwright/test';
import usuarios from '../data/usuarios.json';

// Pagina de inicio de sesion
export class LoginPage {
  readonly usuario: Locator;
  readonly password: Locator;
  readonly boton: Locator;
  readonly error: Locator;

  constructor(private page: Page) {
    this.usuario = page.getByPlaceholder('Username');
    this.password = page.getByPlaceholder('Password');
    this.boton = page.getByTestId('login-button');
    this.error = page.getByTestId('error');
  }

  async abrir() {
    await this.page.goto('/');
  }

  async ingresar(usuario: string, password: string = usuarios.password) {
    if (usuario) await this.usuario.fill(usuario);
    if (password) await this.password.fill(password);
    await this.boton.click();
  }

  // Abre la pagina e inicia sesion esperando el catalogo
  async loginCompleto(usuario: string, password: string = usuarios.password) {
    await this.abrir();
    await this.ingresar(usuario, password);
    await this.page.waitForURL('**/inventory.html');
  }
}
