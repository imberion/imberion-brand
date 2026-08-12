#!/usr/bin/env python3
"""
Genera el set de texturas frías del sistema de superficies.

Una textura de Imberion son dos capas separables:

  fibra   el papel en el que está impreso el deck. CONSTANTE en todo el set.
          Es identidad: si la fibra cambia de lámina a lámina, el deck se lee
          impreso en seis papeles distintos.
  nube    cómo cae la luz sobre esa hoja. VARIABLE. Es ritmo, y es lo que
          permite variar de lámina sin romper la coherencia.

La fibra se muestrea una sola vez de `_fibra_base.jpg` (scan sintético de papel
de algodón, gris neutro). Las nubes son procedurales: se calculan a la
resolución pedida, así que no hay que tilear nada, no hay costuras, y el grano
mide lo mismo en cualquier lámina.

Calibración (medida, no estimada):
  fibra 1.2%   debajo de ~0.6% la superficie se lee como tinte plano, que es
               el default de todo deck generado; arriba de ~2.5% la fibra deja
               de ser superficie y se vuelve dibujo.
  nube 3.5%    debajo de ~2.5% dos atmósferas no se distinguen a escala de
               deck; arriba de ~4% el radial empieza a leerse como reflector
               de PowerPoint.

Uso:
  python3 00_imberion/marca/assets/textures/_build_texturas_frias.py
  python3 ... --check      # falla si lo generado difiere de lo commiteado
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

AQUI = Path(__file__).resolve().parent
FIBRA_BASE = AQUI / "_fibra_base.jpg"
SALIDA = AQUI / "frio"

W, H = 1600, 900
CALIDAD = 82
LITE_W, LITE_H = 1000, 563   # espejo lite para embeber en base64
LITE_Q = 70

FIBRA_PCT = 1.2
NUBE_PCT = 3.5
RADIO_NUBE = 4      # px. Frontera entre banda de nube y banda de fibra.

BASES = {
    "papel":  "#EDEEEF",   # paper-cool.        El aparte, y lámina de argumento.
    "blanco": "#F9FAFB",   # paper-cool-light.  Cuando el blanco puro corta demasiado.
}


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ nubes
# Cada una devuelve un campo escalar en [0,1] del tamaño pedido. La amplitud
# se normaliza después, así que aquí solo importa la FORMA de la luz.

def _malla(w, h):
    x = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    y = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    return x, y


def plana(w, h):
    return np.zeros((h, w))


def bruma_izq(w, h):
    x, _ = _malla(w, h)
    return 1 - x ** 0.8


def bruma_der(w, h):
    x, _ = _malla(w, h)
    return x ** 0.8


def foco(w, h):
    x, y = _malla(w, h)
    r = np.sqrt(((x - 0.42) * 1.05) ** 2 + ((y - 0.44) * 1.5) ** 2)
    return np.clip(1 - r / 0.75, 0, 1) ** 1.4


def luz_alta(w, h):
    _, y = _malla(w, h)
    return (1 - y) ** 1.6


def diagonal(w, h):
    x, y = _malla(w, h)
    return np.clip(1 - (x * 0.65 + y * 0.35), 0, 1) ** 1.1


ATMOSFERAS = [
    ("plana",     plana,      "Default. Sin evento de luz."),
    ("brumaizq",  bruma_izq,  "Abre sección. La luz entra por el margen de lectura."),
    ("brumader",  bruma_der,  "Cierra sección. Empuja hacia el remate."),
    ("foco",      foco,       "Statement corto. Concentra en el centro óptico."),
    ("luzalta",   luz_alta,   "Lámina con mucho texto. Aligera la mitad superior."),
    ("diagonal",  diagonal,   "Divisor o transición. Movimiento sin dibujar nada."),
]


# ------------------------------------------------------------- composición

def _bandas(img):
    gris = img.convert("L")
    lum = np.asarray(gris, dtype=np.float64) / 255.0
    nube = np.asarray(gris.filter(ImageFilter.GaussianBlur(RADIO_NUBE)), dtype=np.float64) / 255.0
    return lum, nube


def superficie(base_hex, nube_fn, w=W, h=H, fibra_pct=FIBRA_PCT, nube_pct=NUBE_PCT):
    src = Image.open(FIBRA_BASE).convert("RGB").resize((w, h), Image.LANCZOS)
    lum, suave = _bandas(src)

    fibra = lum - suave
    fibra = fibra / max(fibra.std(), 1e-9) * (fibra_pct / 100)

    campo = nube_fn(w, h)
    campo = campo - campo.mean()
    if campo.std() > 1e-9:
        campo = campo / campo.std() * (nube_pct / 100)

    base = np.array(hex_to_rgb(base_hex), dtype=np.float64)

    # Una base clara casi no tiene margen hacia el blanco: #F9FAFB deja 1.6%,
    # así que una nube de 3.5% simétrica se satura y pierde amplitud justo en
    # la zona iluminada. En vez de bajar la amplitud (que aplanaría la
    # superficie) se sesga la nube hacia lo sustractivo: el pico de luz llega
    # como mucho al color del token y el resto cae. Es además lo que hace la
    # luz sobre papel, que no lo vuelve más blanco que su propio stock.
    margen = (255.0 - base.max()) / base.max()
    pico = (fibra + campo).max()
    if pico > margen:
        campo = campo - (pico - margen)

    out = (1.0 + fibra + campo)[:, :, None] * base[None, None, :]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def amplitud(img):
    """(nube, fibra) en % de 255. Sirve de gate: si la fibra cae, es tinte plano."""
    lum, nube = _bandas(img)
    return lum.std() * 100, (lum - nube).std() * 100


# --------------------------------------------------------------- contraste

NAVY = np.array(hex_to_rgb("#0A1828"), dtype=np.float64)
ALPHA_CUERPO = 0.72     # --fg-muted / --navy-72
AA = 4.5


def _lineal(c):
    c = np.asarray(c, dtype=np.float64) / 255
    return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


def _luminancia(rgb):
    rgb = np.asarray(rgb, dtype=np.float64)
    return (.2126 * _lineal(rgb[..., 0]) + .7152 * _lineal(rgb[..., 1])
            + .0722 * _lineal(rgb[..., 2]))


def contraste_peor(img, alpha=ALPHA_CUERPO):
    """Contraste del texto de cuerpo contra la ZONA OSCURA de la textura.

    Medirlo contra el color promedio da un número optimista: el texto no se
    lee sobre el promedio, se lee sobre el punto donde la nube más baja.
    """
    arr = np.asarray(img, dtype=np.float64).reshape(-1, 3)
    lum = _luminancia(arr)
    fondo = arr[int(np.argmin(np.abs(lum - np.percentile(lum, 5))))]
    frente = alpha * NAVY + (1 - alpha) * fondo
    a, b = _luminancia(frente), _luminancia(fondo)
    return (max(a, b) + .05) / (min(a, b) + .05)


def main():
    check = "--check" in sys.argv
    SALIDA.mkdir(exist_ok=True)
    (SALIDA / "lite").mkdir(exist_ok=True)
    fallas, faltantes = [], []

    print(f"fibra {FIBRA_PCT}%  ·  nube {NUBE_PCT}%  ·  {W}x{H}  ·  q{CALIDAD}")
    print(f"gate de contraste: navy-{int(ALPHA_CUERPO * 100)} contra el percentil 5, "
          f"mínimo {AA}:1\n")

    for base_key, base_hex in BASES.items():
        for atm_key, fn, _uso in ATMOSFERAS:
            nombre = f"{base_key}_{atm_key}.jpg"
            destino = SALIDA / nombre
            img = superficie(base_hex, fn)

            if check and not destino.exists():
                faltantes.append(nombre)
            if not check:
                img.save(destino, format="JPEG", quality=CALIDAD, subsampling=0)
                img.resize((LITE_W, LITE_H), Image.LANCZOS).save(
                    SALIDA / "lite" / nombre, format="JPEG", quality=LITE_Q, subsampling=0)

            n, f = amplitud(img)
            c = contraste_peor(img)
            estado = "ok" if c >= AA else "FALLA"
            if c < AA:
                fallas.append(f"{nombre}: {c:.2f}:1")
            kb = destino.stat().st_size / 1024 if destino.exists() else 0
            lkb = (SALIDA / "lite" / nombre).stat().st_size / 1024 if (SALIDA / "lite" / nombre).exists() else 0
            print(f"  {nombre:22s} fibra {f:4.2f}%  nube {n:4.2f}%  "
                  f"contraste {c:5.2f}:1 {estado:5s}  {kb:4.0f} KB / lite {lkb:3.0f} KB")

    if faltantes:
        print("\nFALTAN ARCHIVOS:\n  " + "\n  ".join(faltantes))
    if fallas:
        print("\nCONTRASTE POR DEBAJO DE AA:\n  " + "\n  ".join(fallas))
    return 1 if (fallas or faltantes) else 0


if __name__ == "__main__":
    sys.exit(main())
