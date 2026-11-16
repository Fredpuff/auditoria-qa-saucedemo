# Genera todos los documentos de docs/ a partir de los resultados reales.
# Orden: graficos -> Excel -> Word (01, 03, 04, 05, 06) -> PowerPoint
# Requisitos previos: 3 ejecuciones (resultados-ejecucion-1..3.json), tiempos-login.json, coverage/codigo y capturas.
import runpy, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for s in ["graficos.py", "gen_xlsx.py", "gen_01_plan.py", "gen_03_defectos.py", "gen_04_automatizacion.py",
          "gen_05_cobertura.py", "gen_06_informe.py", "gen_07_pptx.py"]:
    print("==", s)
    runpy.run_path(s, run_name="__main__")
