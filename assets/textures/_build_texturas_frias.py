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

# Solo papel lleva fibra, y no es preferencia sino aritmética. Una base necesita
# margen hacia el blanco para que el grano tenga hacia dónde subir: #EDEEEF deja
# 6.7% y alcanza, #F9FAFB deja 1.6% mientras la fibra sola pide ~3.6% en sus
# picos. Con blanco, un tercio de la superficie terminaba aplanada contra el 255
# y la textura dejaba de modular. `paper-cool-light` sigue vivo como tinte liso
# (`.surf-blanco` sin `.atm-*`), que es el rol que de todos modos juega.
BASES = {
    "papel":  "#EDEEEF",   # paper-cool. El aparte, y lámina de argumento a sangre.
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
    # Exponente 1.0 y no 1.4: elevarlo concentra la energía del campo en un pico
    # chico, y como el campo se normaliza por su desviación, ese pico se pasa
    # del margen al blanco y aplana el centro. Lineal reparte mejor y de paso
    # deja más amplitud de nube útil.
    return np.clip(1 - r / 0.75, 0, 1)


def luz_alta(w, h):
    _, y = _malla(w, h)
    return (1 - y) ** 1.6


def diagonal(w, h):
    x, y = _malla(w, h)
    return np.clip(1 - (x * 0.65 + y * 0.35), 0, 1) ** 1.1


# Una sola superficie, y la decisión es de Rodrigo sobre render (2026-08-13).
#
# El set tenía seis atmósferas: un gradiente de luz distinto por lámina, para
# dar ritmo sin romper la coherencia de la fibra. En revisión, el foco radial se
# leyó como "una fotocopia", que es el mismo modo de falla que quedó anotado al
# calibrar: pasado cierto punto el radial se lee como reflector de PowerPoint y
# no como luz sobre papel. La `plana`, con la MISMA fibra, se aceptó.
#
# O sea que lo que aportaba carácter era el grano, y la nube solo aportaba el
# tell. Se quedan las funciones de campo abajo por si algún día se retoma la
# idea con amplitudes menores, pero no se generan.
#
# Consecuencia de diseño, y es la buena: con una sola textura no hay nada que
# rotar. El motor asignaba superficie por rotación automática, que era la brecha
# abierta desde deck-engine#26. Ahora la superficie se pone a propósito por
# slide-type, no se sortea.
ATMOSFERAS = [
    ("plana", plana, "La superficie. Fibra sin evento de luz."),
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

    # Una base clara casi no tiene margen hacia el blanco: #EDEEEF deja 6.7% y
    # #F9FAFB apenas 1.6%, mientras que la fibra sola pide ~3.6% en sus picos.
    # No cabe, y hay que elegir qué se sacrifica.
    #
    # Antes se sesgaba el campo entero hacia lo sustractivo para que el pico
    # cupiera. Eso preservaba los altos pero movía la MEDIA: la superficie salía
    # hasta 34 niveles por debajo de su token, o sea que #F9FAFB renderizaba
    # gris y #EDEEEF renderizaba gris sucio. Era el defecto, no un efecto.
    #
    # Ahora no se desplaza: se recorta contra el blanco. La media queda en el
    # token, que es el color que el ojo lee como el de la hoja, y lo que se
    # pierde son los altos, que se aplanan en blanco puro. Sobre papel eso se
    # lee como papel iluminado. El precio (cuánta superficie se aplana) lo
    # vigila el gate de `deriva`, que es lo que faltaba para cazar esto.
    out = (1.0 + fibra + campo)[:, :, None] * base[None, None, :]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


# Cuánto puede alejarse la media de la superficie del token que dice ser, en
# niveles de 0-255. Dos niveles es imperceptible; veinte es otro color.
DERIVA_MAX = 2.0
# Qué fracción de la superficie puede quedar aplanada contra el blanco. Arriba
# de esto la textura deja de modular y se vuelve un parche liso brillante.
RECORTE_MAX = 6.0


def deriva(img, base_hex):
    """(deriva de la media en niveles, % de superficie aplanada en el blanco).

    El gate que faltaba: una textura tiene que seguir siendo del color que
    declara. Sin esto, un cambio en la composición puede oscurecer la hoja
    entera y pasar todos los demás gates, porque el contraste incluso mejora.
    """
    a = np.asarray(img, dtype=np.float64)
    base = np.array(hex_to_rgb(base_hex), dtype=np.float64)
    aplanado = float((a.max(axis=2) >= 254.5).mean() * 100)
    return float(a.mean() - base.mean()), aplanado


# Desviación del grano neutro, en 0-1. NO es la de la fibra horneada (0.0108):
# `soft-light` sobre una base clara comprime, porque su efecto va con b*(1-b) y
# eso tiende a cero cerca del blanco. Calibrado contra la fórmula para que el
# resultado compuesto sobre #EDEEEF iguale la fibra del set.
GRANO_STD = 0.11


def grano_neutro(w=W, h=H):
    """La fibra sola, centrada en gris medio, para teñirse en runtime.

    Las superficies `papel_*` traen el color horneado, y eso las vuelve opacas:
    puestas como `background-image` tapan el `background-color` de abajo, así que
    el color de la hoja deja de ser elegible. Es la razón por la que un control
    de tono sobre ellas no movía nada: no había nada que mover.

    Este archivo guarda SOLO el grano, sin color. Compuesto con
    `mix-blend-mode: soft-light` sobre cualquier fondo le imprime la fibra sin
    imponerle matiz, y su `opacity` gradúa cuánto se ve. Así el color de la
    superficie sale de la paleta del brand-pack y no del archivo.
    """
    src = Image.open(FIBRA_BASE).convert("RGB").resize((w, h), Image.LANCZOS)
    lum, suave = _bandas(src)
    fibra = lum - suave
    fibra = fibra / max(fibra.std(), 1e-9) * GRANO_STD
    out = 255.0 * (0.5 + fibra)
    g = np.clip(out, 0, 255).astype(np.uint8)
    return Image.fromarray(np.repeat(g[:, :, None], 3, axis=2), "RGB")


def _softlight(base, top):
    return np.where(top <= 0.5,
                    base - (1 - 2 * top) * base * (1 - base),
                    base + (2 * top - 1) * (np.sqrt(base) - base))


def grano_compuesto(img, base_hex):
    """Desviación de alta frecuencia que deja el grano al mezclarse sobre una base.

    Es el gate del grano neutro: el archivo por sí solo no dice nada útil (vive
    en gris medio), y lo que importa es lo que produce ya compuesto. Sin esto,
    recalibrar el grano y aplanar la superficie se ven igual en disco.
    """
    top = np.asarray(img.convert("L"), dtype=np.float64) / 255.0
    b = np.mean(hex_to_rgb(base_hex)) / 255.0
    r = _softlight(np.full_like(top, b), top)
    suave = np.asarray(Image.fromarray((r * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(RADIO_NUBE)), dtype=np.float64) / 255.0
    return float((r - suave).std())


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
            d, aplanado = deriva(img, base_hex)
            estado = "ok"
            if c < AA:
                estado = "FALLA"
                fallas.append(f"{nombre}: contraste {c:.2f}:1")
            if abs(d) > DERIVA_MAX:
                estado = "FALLA"
                fallas.append(f"{nombre}: la media se va {d:+.1f} niveles de {base_hex}")
            if aplanado > RECORTE_MAX:
                estado = "FALLA"
                fallas.append(f"{nombre}: {aplanado:.1f}% de la superficie aplanada en blanco")
            kb = destino.stat().st_size / 1024 if destino.exists() else 0
            lkb = (SALIDA / "lite" / nombre).stat().st_size / 1024 if (SALIDA / "lite" / nombre).exists() else 0
            print(f"  {nombre:22s} fibra {f:4.2f}%  nube {n:4.2f}%  "
                  f"contraste {c:5.2f}:1  deriva {d:+5.1f}  aplanado {aplanado:5.1f}%  "
                  f"{estado:5s}  {kb:4.0f} KB / lite {lkb:3.0f} KB")

    # El grano neutro no lleva color, asi que ni contraste ni deriva aplican:
    # su gate es que conserve la amplitud de fibra del set.
    gn = grano_neutro()
    if not check:
        gn.save(SALIDA / "grano_neutro.jpg", format="JPEG", quality=CALIDAD, subsampling=0)
        gn.resize((LITE_W, LITE_H), Image.LANCZOS).save(
            SALIDA / "lite" / "grano_neutro.jpg", format="JPEG", quality=LITE_Q, subsampling=0)
    compuesto = grano_compuesto(gn, BASES["papel"]) * 100
    objetivo = amplitud(superficie(BASES["papel"], plana))[1]
    print(f"  {'grano_neutro.jpg':22s} compuesto {compuesto:4.2f}%  "
          f"(objetivo {objetivo:4.2f}%, la fibra horneada del set)")
    if abs(compuesto - objetivo) > 0.25:
        fallas.append(
            f"grano_neutro.jpg: compuesto da {compuesto:.2f}% contra {objetivo:.2f}% "
            f"del set; recalibrar GRANO_STD")

    if faltantes:
        print("\nFALTAN ARCHIVOS:\n  " + "\n  ".join(faltantes))
    if fallas:
        print("\nFALLAS:\n  " + "\n  ".join(fallas))
    return 1 if (fallas or faltantes) else 0


if __name__ == "__main__":
    sys.exit(main())
