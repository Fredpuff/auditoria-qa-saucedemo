# Arma ../auditoria-qa-saucedemo.zip sin dependencias ni archivos regenerables.
# Uso (desde la carpeta que contiene el proyecto): python auditoria-qa-saucedemo/tools/empaquetar-zip.py
import collections
import os
import sys
import zipfile

RAIZ = "auditoria-qa-saucedemo"
EXCLUIR = ("node_modules", "app-local", "evidencias/test-results", "coverage/ejecucion-local")
SIN_VIDEOS = "--sin-videos" in sys.argv
DESTINO = "auditoria-qa-saucedemo.zip"


def normal(p):
    return p.replace(os.sep, "/")


def excluido(rel):
    if "__pycache__" in rel.split("/"):
        return True
    if SIN_VIDEOS and rel.startswith("evidencias/videos"):
        return True
    return any(rel == e or rel.startswith(e + "/") for e in EXCLUIR)


tmp = DESTINO + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for d, ds, fs in os.walk(RAIZ):
        rel = normal(os.path.relpath(d, RAIZ))
        rel = "" if rel == "." else rel + "/"
        ds[:] = [x for x in ds if not excluido(rel + x)]
        for f in fs:
            if not excluido(rel + f):
                z.write(os.path.join(d, f), normal(os.path.join(d, f)))
os.replace(tmp, DESTINO)

z = zipfile.ZipFile(DESTINO)
nombres = z.namelist()
print("archivos", len(nombres), "tamano MB", round(os.path.getsize(DESTINO) / 1e6, 1))
peso = collections.Counter()
for i in z.infolist():
    peso["/".join(i.filename.split("/")[1:3])] += i.compress_size
print([(k, round(v / 1e6, 1)) for k, v in peso.most_common(6)])
