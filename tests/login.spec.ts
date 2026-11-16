import { test, expect, evidencia } from './fixtures';
import { LoginPage } from './pages/LoginPage';
import { InventoryPage } from './pages/InventoryPage';
import usuarios from './data/usuarios.json';
import reglas from './data/login-decision.json';

test.describe('Login y sesion', () => {
  test('CP-01 | login valido con standard_user (smoke)', { tag: ['@smoke', '@positiva'] }, async ({ page }) => {
    const login = new LoginPage(page);
    const inv = new InventoryPage(page);
    await login.abrir();
    await login.ingresar(usuarios.standard);
    await expect(page).toHaveURL(/\/inventory\.html$/);
    await expect(inv.titulo).toHaveText('Products');
    await expect(inv.items).toHaveCount(6);
    await evidencia(page, 'CP-01');
  });

  test('CP-06 | logout desde el menu cierra la sesion', { tag: '@positiva' }, async ({ page, context }) => {
    const login = new LoginPage(page);
    const inv = new InventoryPage(page);
    await login.loginCompleto(usuarios.standard);
    await inv.opcionMenu('logout-sidebar-link');
    await expect(page).toHaveURL(/saucedemo\.com\/$|localhost:3000\/$/);
    await expect(login.boton).toBeVisible();
    const cookies = await context.cookies();
    expect(cookies.find((c) => c.name === 'session-username')).toBeUndefined();
    await evidencia(page, 'CP-06');
  });

  test('CP-08 | acceso a /inventory.html sin sesion redirige al login', { tag: '@negativa' }, async ({ page }) => {
    const login = new LoginPage(page);
    await page.goto('/inventory.html');
    await expect(login.boton).toBeVisible();
    await expect(login.error).toHaveText("Epic sadface: You can only access '/inventory.html' when you are logged in.");
    await evidencia(page, 'CP-08');
  });

  test('CP-12 | usuario con mayusculas no es aceptado', { tag: '@negativa' }, async ({ page }) => {
    const login = new LoginPage(page);
    await login.abrir();
    await login.ingresar('Standard_User');
    await expect(login.error).toHaveText('Epic sadface: Username and password do not match any user in this service');
    await evidencia(page, 'CP-12');
  });

  test('CP-13 | contrasena en mayusculas no es aceptada', { tag: '@negativa' }, async ({ page }) => {
    const login = new LoginPage(page);
    await login.abrir();
    await login.ingresar(usuarios.standard, 'SECRET_SAUCE');
    await expect(login.error).toHaveText('Epic sadface: Username and password do not match any user in this service');
    await evidencia(page, 'CP-13');
  });

  // Tabla de decision del login: un test por regla, datos tomados del JSON
  for (const r of reglas) {
    test(`${r.id} | tabla de decision login ${r.regla}: ${r.condicion}`, { tag: '@tabla-decision' }, async ({ page }) => {
      const login = new LoginPage(page);
      await login.abrir();
      await login.ingresar(r.usuario, r.password);
      if (r.esperado === 'acceso') {
        await expect(page).toHaveURL(/\/inventory\.html$/);
      } else {
        await expect(login.error).toHaveText(r.mensaje);
        await expect(page).not.toHaveURL(/inventory/);
      }
      await evidencia(page, r.id);
    });
  }

  test('CP-36 | Back despues de logout no debe mostrar el catalogo', { tag: '@transicion' }, async ({ page }) => {
    const login = new LoginPage(page);
    const inv = new InventoryPage(page);
    await login.loginCompleto(usuarios.standard);
    // El usuario recarga la pagina durante la sesion (F5) y luego cierra sesion
    await page.reload();
    await inv.opcionMenu('logout-sidebar-link');
    await expect(login.boton).toBeVisible();
    await page.goBack();
    // Esperado: sin sesion no se muestra ningun producto, se ve el formulario de login
    await expect(page).not.toHaveURL(/inventory/);
    await evidencia(page, 'CP-36');
    await expect(inv.items).toHaveCount(0);
    await expect(login.boton).toBeVisible();
  });
});
