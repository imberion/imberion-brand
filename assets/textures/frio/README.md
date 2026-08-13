# Texturas frías (set vigente)

Set de superficies del sistema vigente. Generado por `../_build_texturas_frias.py`, no a mano.

## Qué son

Una textura de Imberion son dos capas separables:

- **Fibra**: el papel en el que está impreso el deck. **Constante en las seis.** Es identidad. Si la fibra cambia de lámina a lámina, el deck se lee impreso en seis papeles distintos.
- **Nube**: cómo cae la luz sobre esa hoja. **Variable.** Es ritmo, y es lo que permite variar sin romper coherencia.

Seis archivos: una base (`papel_*` sobre `--paper-cool` `#EDEEEF`) por seis atmósferas.

**Solo hay una base con fibra, y es aritmética.** El grano necesita margen hacia el blanco para tener hacia dónde subir: `#EDEEEF` deja 6.7% y alcanza, mientras que `#F9FAFB` deja 1.6% y la fibra sola pide ~3.6% en sus picos. Con esa base, un tercio de la superficie quedaba aplanada contra el 255 y la textura dejaba de modular. `--paper-cool-light` sigue vivo como **tinte liso** (`.surf-blanco` sin `.atm-*`), que es el rol que de todos modos juega. Si hace falta grano sobre una superficie clara, la respuesta es `.surf-papel`.

El set `blanco_*` existió y se retiró el 2026-08-12, junto con la corrección de la deriva de luminancia descrita abajo.

| Atmósfera | Cuándo |
|---|---|
| `plana` | Default. Sin evento de luz. |
| `brumaizq` | Abre sección. La luz entra por el margen de lectura. |
| `brumader` | Cierra sección. Empuja hacia el remate. |
| `foco` | Statement corto. Concentra en el centro óptico. |
| `luzalta` | Lámina con mucho texto. Aligera la mitad superior. |
| `diagonal` | Divisor o transición. Movimiento sin dibujar nada. |

## Regla de área

Van **solo a sangre**: lámina completa o banda de ancho completo. En un recuadro chico la fibra no alcanza a formar patrón y se lee como suciedad de impresión. Los paneles internos van con tinte liso (`--page-aside`, `--page-group`), sin borde ni sombra.

## Calibración

Los dos números salieron de comparar renders, no de estimar:

- **Fibra 1.2%.** Debajo de ~0.6% la superficie se lee como tinte plano, que es el default de todo deck generado por herramienta (el set cálido anterior medía 0.37%). Arriba de ~2.5% la fibra deja de ser superficie y se vuelve dibujo.
- **Nube 3.5%.** Debajo de ~2.5% dos atmósferas no se distinguen a escala de deck. Arriba de ~4% el radial empieza a leerse como reflector de PowerPoint.

En una base muy clara la nube se sesga hacia lo sustractivo: `#F9FAFB` deja solo 1.6% de margen hasta el blanco, así que una nube simétrica se saturaría y perdería amplitud justo en la zona iluminada. El pico de luz llega como mucho al color del token y el resto cae, que es además lo que hace la luz sobre papel real.

## Gates del build

**Contraste.** Mide el texto de cuerpo (`--fg-muted`, navy-72) contra el **percentil 5 de luminancia** de cada textura y falla si baja de 4.5:1. Se mide contra la zona oscura y no contra el promedio porque el texto no se lee sobre el promedio: se lee sobre el punto donde la nube más baja. Peor caso del set: 6.18:1.

**Deriva de luminancia** (`DERIVA_MAX`, 2 niveles). La media de la textura tiene que quedar en el token que dice ser. Este gate se agregó después de que un sesgo en la composición dejara todas las texturas hasta 34 niveles por debajo de su base: `#F9FAFB` renderizaba gris y `#EDEEEF` renderizaba gris sucio, y **ningún otro gate lo cazó porque oscurecer la superficie mejora el contraste**. Ese es el punto: sin este gate, el defecto se lee como mejora.

**Superficie aplanada** (`RECORTE_MAX`, 6%). Qué fracción queda pegada contra el blanco. Arriba de ese umbral la textura deja de modular y se vuelve un parche liso brillante. Es el gate que demostró que la base `#F9FAFB` no puede llevar fibra.

## Archivos

- Raíz: 1600×900, q82. Para render y pantalla.
- `lite/`: 1000×563, q70 (~41 KB). Para embeber en base64 en HTML autocontenido.
- Fuente de fibra: `../_fibra_base.jpg`. El master a resolución completa vive en Drive, `04_marca/identidad_visual/texturas/`.

## Regenerar

```
python3 00_imberion/marca/assets/textures/_build_texturas_frias.py
python3 00_imberion/marca/assets/textures/_build_texturas_frias.py --check   # gate, no escribe
```

Cambiar amplitud o agregar atmósfera se hace en el script (`FIBRA_PCT`, `NUBE_PCT`, `ATMOSFERAS`), nunca editando los JPEG.
