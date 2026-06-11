# Iconografia Imberion

Set editorial de linea propia. **22 glifos**, trazo 1.25px, lienzo 24px, esquinas redondeadas (round caps/joins), navy `#0A1828` sobre claro (blanco sobre oscuro). Sin rellenos salvo el `signal` de marca y los puntos de glifo (`decision`, `alert`, `help`).

Origen: `imberion-website/Imberion/assets/icons.html`. Esta es la copia canonica en el brain para usar en presentaciones y entregables.

## Regla

Extender el set **dibujando dentro de este vocabulario**, nunca importando Lucide / Heroicons / Feather u otros. Los glifos referencian palancas comerciales (pricing, portfolio, promo, trade), mecanica de decision (loop, framework, segment) y contextos de industria.

## Glifos

`signal` (marca), `decision`, `pricing`, `portfolio`, `promotion`, `trade`, `margin`, `growth`, `loop`, `framework`, `segment`, `benchmark`, `governance`, `data`, `execution`, `industrial`, `consumer`, `services`.

Sub-familia utilitaria (estado / anotacion): `alert` (triangulo, oportunidad o atencion), `help` (interrogacion en circulo), `cross` (equis en circulo, no o rechazado), `check` (palomita en circulo, si o validado). Se usan para resaltar oportunidades, dudas y estatus en mapas de proceso y entregables.

Ver `_referencia.html` para la hoja visual.

## Uso

Cada icono es un `.svg` standalone con el trazo y color ya seteados. Para un deck/HTML autocontenido, embeber el SVG inline (el `_build.py` de Market Signal los lee y los inyecta). Para recolorear en fondo oscuro, override `stroke:#fff` en CSS.
