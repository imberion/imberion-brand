# Iconografia Imberion

Set editorial de linea propia. **33 glifos** en dos familias (23 base + 10 de industria), trazo 1.25px, lienzo 24px, esquinas redondeadas (round caps/joins). Sin rellenos salvo el `signal` de marca y los puntos de glifo (`decision`, `alert`, `help`).

El color se hereda: los SVG pintan con `currentColor`, asi que sobre papel toman navy, sobre navy toman blanco y en acento toman petroleo, con solo setear `color` en el contenedor. No hay archivo por variante ni `filter: invert`.

Origen: `imberion-website/Imberion/assets/icons.html`. Esta es la copia canonica en el brain para usar en presentaciones y entregables.

## Regla

Extender el set **dibujando dentro de este vocabulario**, nunca importando Lucide / Heroicons / Feather u otros. Los glifos referencian palancas comerciales (pricing, portfolio, promo, trade), mecanica de decision (loop, framework, segment) y contextos de industria.

## Glifos

`signal` (marca), `decision`, `pricing`, `portfolio`, `promotion`, `trade`, `margin`, `growth`, `loop`, `framework`, `segment`, `benchmark`, `governance`, `data`, `execution`, `industrial`, `consumer`, `services`.

Sub-familia utilitaria (estado / anotacion): `alert` (triangulo, oportunidad o atencion), `help` (interrogacion en circulo), `cross` (equis en circulo, no o rechazado), `check` (palomita en circulo, si o validado). Se usan para resaltar oportunidades, dudas y estatus en mapas de proceso y entregables.

Industrias (`industrias/`): `retail`, `cpg`, `telco`, `farma`, `automotriz`, `logistics`, `building_materials`, `b2b_industrial`, `servicios_b2b`, `servicios_b2c`. Ademas del set base hay `hanger` (retail de moda).

## Hoja de contacto

`_referencia.html` es la hoja visual del set completo y **se genera**, no se edita:

```bash
python3 00_imberion/marca/iconos/_build_referencia.py          # regenera
python3 00_imberion/marca/iconos/_build_referencia.py --check  # exit 1 si hay drift
```

El builder tambien valida la disciplina de linea: si un glifo nuevo no trae `viewBox="0 0 24 24"` y `stroke-width="1.25"`, aborta y lo nombra. La version escrita a mano se habia desfasado: declaraba 23 glifos y no tenia ninguno de industrias.

## Uso

Cada icono es un `.svg` standalone con el trazo ya seteado. Para un deck/HTML autocontenido, embeber el SVG inline (el `_build.py` de Market Signal los lee y los inyecta). Para recolorear, setear `color` en el contenedor: el glifo lo hereda.

Por debajo de 20px el trazo de 1.25 empieza a cerrar los contraformas de los glifos densos (`data`, `industrial`); ahi conviene usar los glifos simples.
