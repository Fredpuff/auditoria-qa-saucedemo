import { defineConfig, devices } from '@playwright/test';

// URL de la aplicacion: sitio publico por defecto, o la copia local instrumentada para cobertura
const COBERTURA = !!process.env.COVERAGE;
const BASE_URL = process.env.BASE_URL || (COBERTURA ? 'http://localhost:3000' : 'https://www.saucedemo.com');
// La corrida de cobertura guarda sus reportes aparte para no mezclarlos con la evidencia del sitio publico
const REPORTES = COBERTURA ? 'coverage/ejecucion-local' : 'evidencias/reportes';

export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0, // sin reintentos: un fallo real debe verse en rojo
  workers: process.env.CI ? 2 : 4,
  outputDir: COBERTURA ? 'coverage/ejecucion-local/test-results' : 'evidencias/test-results',
  reporter: [
    ['list'],
    ['html', { outputFolder: `${REPORTES}/html`, open: 'never' }],
    ['json', { outputFile: `${REPORTES}/resultados.json` }],
    ['junit', { outputFile: `${REPORTES}/junit.xml` }],
  ],
  use: {
    baseURL: BASE_URL,
    testIdAttribute: 'data-test',
    screenshot: 'on',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
    launchOptions: { slowMo: Number(process.env.SLOWMO || 0) },
  },
  projects: COBERTURA
    ? [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }]
    : [
        { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
        { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
      ],
  // Para la cobertura se levanta la copia local instrumentada de SauceDemo
  webServer: COBERTURA
    ? { command: 'npm run app:serve', url: 'http://localhost:3000', reuseExistingServer: true, timeout: 120_000 }
    : undefined,
});
