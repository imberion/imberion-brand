# Snippets HTML

Bloques HTML reutilizables para construir presentaciones y propuestas. Cada snippet es un archivo `.html` autocontenido, listo para copiarse y rellenar variables.

## Plantilla estándar de deck

`plantilla_deck.html` es el **estándar de todas las presentaciones de Imberion**. Deck de slides **16:9 (formato PowerPoint, 338.67mm × 190.5mm, `@page 13.333in 7.5in`)**, NO A4. Autocontenido (CSS y logos embebidos como base64, cero rutas externas) para que abra standalone en cualquier máquina y exporte a PDF limpio. `fitSlideToViewport` escala a 1280×720.

> **Regla de formato:** los decks de Imberion son 16:9, no A4. A4 (vertical/horizontal) es solo para documentos tipo memo o reportes de lectura, no para presentar.

Cómo usarla: copiar el archivo, reescribir solo el contenido de las slides, ajustar el `<title>`, el total del contador de navegación (`/NN`) y los `page-num` de los footers al número real de slides.

Características:
- Modo presentación (una slide a pantalla, fit-to-viewport) y modo impresión (todas apiladas), toggle con botón o Esc, flechas para navegar. JS embebido.
- Portada y cierre con `class="slide cover"` (fondo navy, logo blanco real embebido, no `filter: invert`).
- **Texturas embebidas**: grano sutil en hojas papel (`.slide::before`) y dust navy en cover/closing (`.slide.cover::before`). Además, bloque `#imb-textures` con seis clases variables (`.slide.tex-paper`, `.tex-signal`, `.tex-focus`, `.tex-haze`, `.tex-leftmist`, `.tex-rightmist`), embebidas como lite JPEG: se agrega una por slide para variar la textura. Regla en `marca/reglas_presentaciones_html.md`.
- Catálogo de componentes documentado en el comentario al inicio del `<body>`: gantt, actions-grid, risk-table, dr-grid + status-pill, data-table, week-block/activity-list, checklist-grid, caveat-box, status-badge.

El origen fue el status semanal de Temisa (`reporte_semanal_status` skill). Para regenerarla o ajustar texturas, ver el builder usado en su momento (downscale con `sips`, embebido base64).

## Snippets de slide disponibles

Tipos de slide extraídos del deck SteerCo Hito 1 de Temisa (2026-06-01). Cada uno trae su `<style>` con las clases que necesita y un `<div class="slide">` con placeholders; asumen las variables `:root` y la base de `plantilla_deck.html`. Copiar el style al `<head>` del deck y el HTML al body.

- `slide_resumen_hub.html` Resumen ejecutivo tipo hub: N temas en columnas, cada bullet con su so-what y liga `goTo(IDX)` a su back slide; los "no existe" cuelgan al pie.
- `slide_analisis_panel.html` Action-title (so-what) + chart a la izquierda + panel derecho de 2-3 takeaways + línea "So what". Hover opcional chart↔takeaway vía `data-hl`.
- `slide_analisis_barra.html` Variante para charts a ancho completo (bridge, dispersión, small multiples): chart arriba, barra inferior de takeaways + "So what". Hereda las clases base de `slide_analisis_panel`.
- `slide_matriz_proyectos.html` Matriz impacto × complejidad (cuadrante SVG con burbujas por alcance) + lista lateral de iniciativas.

## Mockups y motion

- `mockup_mapa_pdv.svg` Dashboard de mapa de puntos de venta: mapa de México (paths reales de estados) con dots de cobertura / white space / competidor (hex hardcodeado, agnóstico). Se embebe en un contenedor con header, leyenda y KPIs. Usado en el deck Market Signal slide 3.
- `anim_noise_to_signal.html` Animación de marca: partículas que parten como ruido y convergen a la señal interior de la "O" del logo (path real del favicon), contenida en un canvas, en loop. Reutilizable como loader, acento de hero o detalle. Parámetros (tamaño, partículas, velocidad) en el script.

## Snippets a crear

- `slide_portada.html`
- `slide_seccion.html`
- `slide_tabla_pricing.html`
- `slide_timeline.html`
- `slide_card_hito.html`
- `slide_quote.html`
- `slide_cierre.html`

Cada uno con las clases CSS necesarias para que herede de `imberion_base.css` y `imberion_componentes.css`.

## Aprendizajes de diseño (deck SteerCo Hito 1, 2026-05-30)

- **Números: serif si van dentro de un enunciado, sans si van sueltos.**
  - **Dentro de una frase o título** (action-titles, `.okr-t`, `.sh-t`, cualquier texto corrido): el número se queda en Cormorant, heredando la fuente del texto. NO envolverlo en sans: un dígito sans en medio de Cormorant "salta" y se ve peor que el problema que resuelve. Ej.: "Madurez baja (1.55 / 4)", "Cerrar el Hito 1".
  - **Sueltos** (scores grandes de un journey/stepper, KPIs aislados, numeración de agenda `.ag-n`, ejes de charts, page-nums): van en sans (DM Sans), donde el "1" de Cormorant se confundiría con "I". Para un número suelto dentro de un SVG/elemento serif, fijar `font-family: var(--font-sans)` en ese elemento puntual.
  - Garamond no tiene variante sans; por eso la regla es contextual, no "todo a sans".
- **Formato 16:9, no A4.** Ver arriba. El chasis ya viene en 16:9; no revertir a A4.
- **Usar el skill `frontend-design` (en `~/.claude/skills/frontend-design`) siempre que se cree o retoque un deck.** Da el criterio de jerarquía, espaciado y tipografía.
- **Tamaño de título consistente entre slides:** las slides analíticas usan `h1.slide-title.action` (25px); las de sección usan `.slide-title` (32px). Un título-frase largo en 32px se ve desproporcionado junto a slides `.action`; usar `.action` cuando el título es una oración, no una etiqueta corta.
- **Renumeración al insertar slides:** además del `<title>`, el `/NN` del contador y los `page-num`, hay que corregir los `goTo(IDX)` (agenda, hub, botones "volver") y los comentarios de sección. El contador de nav es dinámico; los `page-num` NO.
- **Patrón journey / stepper** (usado en "A dónde te llevamos"): SVG con nodos equiespaciados a todo el ancho, línea conectora (sólida = hecho/comprometido, punteada = horizonte), score grande por nodo en sans, etiquetas apiladas con aire. Candidato a snippet `slide_trayectoria.html`.
- **Gantt:** reusar verbatim el del status semanal (`reporte_semanal_status`) cuando el plan no cambió; mover solo el marcador de semana en curso. El status revisado es la fuente de verdad de fechas.
