// Copia los videos de los tests fallidos (Chromium) a evidencias/videos con el nombre del bug.
// Uso: npm run evidencias   (despues de npm test)
import fs from 'fs';
import path from 'path';

const r = JSON.parse(fs.readFileSync('evidencias/reportes/resultados.json', 'utf8'));
fs.mkdirSync('evidencias/videos', { recursive: true });
let copiados = 0;
const recorrer = (s) => {
  for (const spec of s.specs || []) {
    const bug = spec.title.match(/BUG-\d+/)?.[0];
    for (const t of spec.tests) {
      if (t.projectName !== 'chromium') continue;
      for (const res of t.results) {
        const video = res.attachments.find((a) => a.name === 'video' && a.path);
        if (bug && video && fs.existsSync(video.path)) {
          fs.copyFileSync(video.path, path.join('evidencias/videos', `${bug}.webm`));
          copiados++;
        }
      }
    }
  }
  (s.suites || []).forEach(recorrer);
};
r.suites.forEach(recorrer);
console.log(`Videos copiados: ${copiados}`);
