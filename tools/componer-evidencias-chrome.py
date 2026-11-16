# Arma las capturas compuestas de la verificacion en Brave (BUG-11, 12, 13, 16, 18).
# Las imagenes de origen son capturas reales tomadas con la extension Claude in Chrome;
# los textos son los valores medidos en la misma sesion (ver evidencias/capturas/manual/registro.txt).
import sys
from PIL import Image, ImageDraw, ImageFont

ORIGEN = sys.argv[1]  # carpeta con las capturas jpg de la sesion
OUT = "evidencias/capturas/manual/"


def fuente(t):
    for f in ["arial.ttf", "C:/Windows/Fonts/arial.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(f, t)
        except OSError:
            pass
    return ImageFont.load_default()


def cargar(n):
    return Image.open(f"{ORIGEN}/{n}.jpg").convert("RGB")


def lado_a_lado(izq, der, t_izq, t_der, titulo, nombre):
    alto = max(izq.height, der.height)
    w = izq.width + der.width + 30
    lienzo = Image.new("RGB", (w, alto + 110), "white")
    d = ImageDraw.Draw(lienzo)
    d.text((10, 10), titulo, fill="black", font=fuente(26))
    d.text((10, 55), t_izq, fill="#1E2761", font=fuente(22))
    d.text((izq.width + 40, 55), t_der, fill="#B00020", font=fuente(22))
    lienzo.paste(izq, (0, 100))
    lienzo.paste(der, (izq.width + 30, 100))
    lienzo.save(OUT + nombre)
    print("ok", nombre)


def texto(lineas, titulo, nombre, ancho=1500):
    f = fuente(22)
    lienzo = Image.new("RGB", (ancho, 90 + 34 * len(lineas)), "white")
    d = ImageDraw.Draw(lienzo)
    d.text((20, 20), titulo, fill="black", font=fuente(26))
    for i, l in enumerate(lineas):
        color = "#B00020" if "404" in l or "ms" in l and "performance" in l else "black"
        d.text((20, 75 + 34 * i), l, fill=color, font=f)
    lienzo.save(OUT + nombre)
    print("ok", nombre)


reg = {k: v for k, v in (a.split("=") for a in sys.argv[2:])}

lado_a_lado(cargar(reg["c12a"]), cargar(reg["c12b"]),
            "Catalogo (visual_user): Backpack $48.05", "Resumen de compra: Backpack $29.99",
            "BUG-12 - Brave 157 - el precio mostrado no es el cobrado", "BUG-12_chrome.png")
lado_a_lado(cargar(reg["c13a"]).resize((761, 340)), cargar(reg["c13b"]).resize((761, 340)),
            "standard_user: carrito (1447,10), nombres a la izquierda", "visual_user: carrito (1261,39), nombres 3 y 4 a la derecha",
            "BUG-13 - Brave 157 - comparacion standard_user vs visual_user", "BUG-13_chrome.png")
Image.open(f"{ORIGEN}/{reg['c16']}.jpg").save(OUT + "BUG-16_chrome.png")
print("ok BUG-16_chrome.png")
texto(["Inicio de sesion medido desde el clic en Login hasta el primer producto (MutationObserver):",
       "performance_glitch_user  repeticion 1: 5022 ms",
       "performance_glitch_user  repeticion 2: 10039 ms",
       "standard_user            referencia:      18 ms",
       "Umbral esperado: menos de 2000 ms"],
      "BUG-11 - Brave 157 (Chromium 157) - 16/11/2026", "BUG-11_chrome.png")
texto(["Pestana Red (read_network_requests de la extension):",
       "GET https://www.saucedemo.com/inventory.html           -> 404",
       "GET https://www.saucedemo.com/?/inventory.html         -> 200 (redireccion)",
       "GET https://www.saucedemo.com/cart.html                -> 404",
       "GET https://www.saucedemo.com/?/cart.html              -> 200 (redireccion)",
       "GET https://www.saucedemo.com/checkout-step-one.html   -> 404",
       "GET https://www.saucedemo.com/?/checkout-step-one.html -> 200 (redireccion)"],
      "BUG-18 - Brave 157 - recarga y URL directa de paginas internas", "BUG-18_chrome.png")

if "c14a" in reg:
    lado_a_lado(cargar(reg["c14a"]).resize((761, 340)), cargar(reg["c14b"]).resize((761, 340)),
                "Resumen con el carrito vacio: Total $0.00", "Finish: Thank you for your order!",
                "BUG-14 - Brave 157 - compra sin productos", "BUG-14_chrome.png")
if "c17a" in reg:
    lado_a_lado(cargar(reg["c17a"]).resize((761, 340)), cargar(reg["c17b"]).resize((761, 340)),
                "Codigo postal ABC!@# aceptado", "Pasa al resumen sin mensaje de error",
                "BUG-17 - Brave 157 - codigo postal invalido", "BUG-17_chrome.png")
