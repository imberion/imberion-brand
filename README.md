# Imberion Brand Kit

Hojas de estilo, texturas, logos, iconos y snippets HTML del sistema visual de Imberion. Este repo es la fuente pública del kit: lo que se necesita para construir un entregable HTML (propuesta, deck, dashboard, one-pager) con la identidad de Imberion.

Material propietario de Imberion. Público para servirse vía CDN y para colaboradores de la firma. No es open source.

## Qué hay aquí

- `css/` Hojas de estilo canónicas (base, componentes, charts, deck, texturas).
- `assets/textures/` Texturas editoriales de fondo en PNG. `assets/textures/lite/` son las versiones JPEG comprimidas (~900px) para embeber en decks autocontenidos.
- `logos_svg/` Logos en SVG (con y sin tagline, navy y blanco) y favicons.
- `iconos/` 18 iconos editoriales de línea propia (trazo 1.25px, navy). Ver `iconos/_referencia.html`.
- `snippets_html/` Bloques HTML reutilizables. El principal es `plantilla_deck.html`, el chasis estándar de decks (16:9, autocontenido, CSS y logos embebidos).

## Cómo se usa: cargar el CSS vía CDN

Los archivos se sirven por jsDelivr directo desde este repo. En el `<head>` del HTML, cargar las fuentes y luego los CSS canónicos en este orden:

```html
<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap" rel="stylesheet"/>

<!-- Imberion CSS canónicos -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rogarridoe/imberion-brand@main/css/imberion_base.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rogarridoe/imberion-brand@main/css/imberion_componentes.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rogarridoe/imberion-brand@main/css/imberion_charts.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rogarridoe/imberion-brand@main/css/imberion_textures.css"/>
```

Para un deck (modo presentación a pantalla completa) agregar al final:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rogarridoe/imberion-brand@main/css/imberion_deck.css"/>
```

Las texturas se resuelven solas: `imberion_textures.css` las referencia con rutas relativas y la CDN las sirve desde `assets/textures/` sin configuración extra.

### Fijar una versión

`@main` sirve siempre lo último de la rama. Para un entregable que se quiere reproducible (que no cambie si el kit se actualiza), fijar a un tag o commit en vez de `@main`:

```
https://cdn.jsdelivr.net/gh/rogarridoe/imberion-brand@v1.0.0/css/imberion_base.css
```

## Uso local (sin CDN)

Clonar el repo y apuntar los `<link>` a la copia local con rutas relativas:

```bash
git clone https://github.com/rogarridoe/imberion-brand.git
```

```html
<link rel="stylesheet" href="ruta/a/imberion-brand/css/imberion_base.css"/>
```

## Logos e iconos

- Logos: SVG inline para que se embeban en el HTML, no por `<img>`. Para fondos oscuros, usar la variante blanca o aplicar `filter: invert(1)` sobre la navy.
- Iconos: embeber el SVG inline. No importar librerías externas (Lucide, Heroicons, Feather): el set propio sostiene la identidad de línea.

## Reglas de marca

El detalle de cuándo y cómo usar cada pieza (densidad, jerarquía, paleta de charts, reglas de textura, exportación a PDF) vive en la documentación de marca de Imberion. Este repo entrega los assets; el criterio de uso se coordina con el equipo.
