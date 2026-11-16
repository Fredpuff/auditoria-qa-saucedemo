// Extrae los tiempos de login medidos por CP-50 (Chromium) del resultado JSON y los guarda aparte.
// Uso: node tools/extraer-tiempos.mjs [evidencias/reportes/resultados-ejecucion-3.json]
import fs from 'fs';
const archivo = process.argv[2] || 'evidencias/reportes/resultados-ejecucion-3.json';
const r = JSON.parse(fs.readFileSync(archivo, 'utf8'));
let salida = null;
const rec = (s) => {
  for (const sp of s.specs || []) {
    if (!sp.title.startsWith('CP-50')) continue;
    for (const t of sp.tests) {
      if (t.projectName !== 'chromium') continue;
      const a = t.results[0].attachments.find((x) => x.name === 'tiempos-login.json');
      if (a?.body) salida = Buffer.from(a.body, 'base64').toString('utf8');
      else if (a?.path) salida = fs.readFileSync(a.path, 'utf8');
    }
  }
  (s.suites || []).forEach(rec);
};
r.suites.forEach(rec);
if (!salida) throw new Error('No se encontro el adjunto tiempos-login.json');
fs.writeFileSync('evidencias/reportes/tiempos-login.json', salida);
console.log(salida);
