// Mide la cobertura de codigo de SauceDemo que alcanzan las pruebas E2E.
// 1) corre la suite en Chromium contra la copia local instrumentada (http://localhost:3000)
// 2) cada test deja window.__coverage__ en .nyc_output
// 3) los archivos de src que el navegador nunca cargo se agregan con 0 % (equivalente a nyc --all)
// 4) nyc genera el reporte HTML y el resumen en coverage/codigo
// Requisito previo: npm run app:prepare
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const APP = path.resolve('app-local/sample-app-web');
const SRC = path.join(APP, 'src');
const TMP = path.resolve('.nyc_output');
const SALIDA = path.resolve('coverage/codigo');

if (!fs.existsSync(path.join(APP, 'build-coverage'))) {
  console.error('Falta la app local instrumentada. Ejecute primero: npm run app:prepare');
  process.exit(1);
}
fs.rmSync(path.join(TMP, 'zz-no-cargados.json'), { force: true });
fs.rmSync(SALIDA, { recursive: true, force: true });

if (!process.argv.includes('--solo-reporte')) {
  fs.rmSync(TMP, { recursive: true, force: true });
  try {
    execSync('npx playwright test', { stdio: 'inherit', env: { ...process.env, COVERAGE: '1' } });
  } catch {
    // Los tests que reproducen defectos fallan a proposito; igual se genera el reporte
    console.log('\nHay pruebas fallidas (esperado por los defectos). Se genera el reporte de cobertura igualmente.');
  }
}

// Archivos que se miden: todo src menos pruebas unitarias, Storybook y configuracion de Jest
const excluir = (p) => /__tests__|__mocks__|storybook|\.stories\.|setupTests|jest\.setupTextEncoder/.test(p);
const fuentes = [];
const recorrer = (d) => {
  for (const f of fs.readdirSync(d)) {
    const p = path.join(d, f);
    if (fs.statSync(p).isDirectory()) recorrer(p);
    else if (/\.(js|jsx)$/.test(f) && !excluir(p)) fuentes.push(p);
  }
};
recorrer(SRC);

const archivos = fs.existsSync(TMP) ? fs.readdirSync(TMP) : [];
console.log(`\nArchivos de cobertura recogidos de los tests: ${archivos.length}`);
const medidos = new Set();
for (const a of archivos) {
  for (const k of Object.keys(JSON.parse(fs.readFileSync(path.join(TMP, a), 'utf8')))) medidos.add(path.resolve(k));
}

// Agrega con 0 % los archivos que ningun test cargo, para no inflar el porcentaje
const { createInstrumenter } = require('istanbul-lib-instrument');
const inst = createInstrumenter({ esModules: true, parserPlugins: ['jsx'] });
const vacios = {};
for (const f of fuentes) {
  if (medidos.has(path.resolve(f))) continue;
  inst.instrumentSync(fs.readFileSync(f, 'utf8'), f);
  vacios[f] = inst.lastFileCoverage();
}
console.log(`Archivos de src no cargados por ningun test (se cuentan con 0 %): ${Object.keys(vacios).map((f) => path.relative(APP, f)).join(', ') || 'ninguno'}`);
fs.mkdirSync(TMP, { recursive: true });
fs.writeFileSync(path.join(TMP, 'zz-no-cargados.json'), JSON.stringify(vacios));

execSync(
  `npx nyc report --temp-dir "${TMP}" --report-dir "${SALIDA}" --cwd "${APP}" --exclude-after-remap=false ` +
    '--reporter=html --reporter=text --reporter=text-summary --reporter=json-summary',
  { stdio: 'inherit' },
);
console.log('\nReporte HTML: coverage/codigo/index.html');
