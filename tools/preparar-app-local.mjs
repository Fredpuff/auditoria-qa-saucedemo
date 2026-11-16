// Prepara una copia local de SauceDemo (saucelabs/sample-app-web) instrumentada con Istanbul
// para medir la cobertura de codigo que alcanzan las pruebas E2E.
// Uso: node tools/preparar-app-local.mjs   (luego: npm run app:serve)
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const DIR = path.resolve('app-local/sample-app-web');
const REPO = 'https://github.com/saucelabs/sample-app-web.git';
// Commit fijo para que la medicion sea repetible
const COMMIT = 'd5cd655fa8a974f4ddb6fde2868586e0084211d2';
const run = (cmd, cwd = DIR) => { console.log('> ' + cmd); execSync(cmd, { cwd, stdio: 'inherit' }); };

if (!fs.existsSync(DIR)) {
  fs.mkdirSync(path.dirname(DIR), { recursive: true });
  run(`git clone ${REPO} "${DIR}"`, process.cwd());
}
run(`git fetch --depth 1 origin ${COMMIT}`);
run(`git checkout --force ${COMMIT}`);

// El paquete pide Node 24; con Node 18+ compila igual, por eso se desactiva engine-strict.
run('npm ci --ignore-scripts --engine-strict=false --no-audit --no-fund');
run('npm i -D vite-plugin-istanbul@9.0.1 --ignore-scripts --engine-strict=false --no-audit --no-fund');

// El codigo original trae comentarios "istanbul ignore" que sacan funciones del calculo.
// Se eliminan para NO inflar la cobertura: todo el codigo de src cuenta en el denominador.
let quitados = 0;
const recorrer = d => {
  for (const f of fs.readdirSync(d)) {
    const p = path.join(d, f);
    if (fs.statSync(p).isDirectory()) { recorrer(p); continue; }
    if (!/\.(js|jsx)$/.test(f)) continue;
    const txt = fs.readFileSync(p, 'utf8');
    const nuevo = txt.replace(/\/\*\s*istanbul ignore[^*]*\*\//g, () => { quitados++; return ''; });
    if (nuevo !== txt) fs.writeFileSync(p, nuevo);
  }
};
recorrer(path.join(DIR, 'src'));
console.log(`Comentarios "istanbul ignore" eliminados: ${quitados}`);

fs.writeFileSync(path.join(DIR, 'vite.config.coverage.mjs'), `import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import istanbul from "vite-plugin-istanbul";

// Configuracion de build instrumentada (solo para la auditoria)
export default defineConfig({
  plugins: [
    react(),
    istanbul({
      include: "src/*",
      exclude: ["node_modules", "src/**/__tests__/**", "src/storybook/**", "src/**/*.stories.jsx", "src/setupTests.js", "src/jest.setupTextEncoder.js"],
      extension: [".js", ".jsx"],
      requireEnv: false,
      forceBuildInstrument: true,
    }),
  ],
  build: { outDir: "build-coverage", sourcemap: true },
  preview: { port: 3000, strictPort: true },
});
`);
run('npx vite build --config vite.config.coverage.mjs');
console.log('Listo. Ejecute: npm run app:serve  (http://localhost:3000)');
