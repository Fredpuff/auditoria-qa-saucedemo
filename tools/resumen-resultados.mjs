// Resume evidencias/reportes/resultados.json: estado de cada test y primera linea del error.
import fs from 'fs';
const archivo = process.argv[2] || 'evidencias/reportes/resultados.json';
const r = JSON.parse(fs.readFileSync(archivo, 'utf8'));
const filas = [];
const recorrer = (s, ruta = []) => {
  for (const spec of s.specs || []) for (const t of spec.tests) for (const res of t.results) {
    const err = (res.error?.message || '').replace(/\x1b\[[0-9;]*m/g, '').split('\n').filter(Boolean).slice(0, 2).join(' / ');
    filas.push({ proyecto: t.projectName, titulo: spec.title, estado: res.status, ms: res.duration, err });
  }
  for (const h of s.suites || []) recorrer(h, [...ruta, h.title]);
};
r.suites.forEach((s) => recorrer(s));
const solo = process.argv[3];
for (const f of filas) if (!solo || f.estado !== 'passed') console.log(`${f.proyecto.padEnd(8)} ${f.estado.padEnd(7)} ${String(f.ms).padStart(6)}ms  ${f.titulo}${f.err ? '\n      -> ' + f.err.slice(0, 220) : ''}`);
const s = r.stats;
console.log(`\nTotal: pasaron ${s.expected}, fallaron ${s.unexpected}, inestables ${s.flaky}, omitidos ${s.skipped}, duracion ${(s.duration / 1000).toFixed(1)} s`);
