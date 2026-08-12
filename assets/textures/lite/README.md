# Texturas lite (set cálido, EN RETIRO)

> **Este set salió del chasis.** Su base coincide en matiz (48°) y luminosidad con el oat
> que usan las herramientas generativas, y su amplitud de fibra medía 0.37%, o sea que se
> leían como tinte plano. El set vigente es `../frio/` (ver su README).
>
> Se conservan porque seis `_build.py` de cliente las referencian. No usar en material nuevo.
> Las dos navy (`01_hero_dust_navy`, `11_cta_dust_navy`) **no** son legacy: siguen siendo
> portada y cierre.

Versiones optimizadas (JPEG ~900px, q66) del set de texturas editoriales. Espejo lite de los PNG master de la carpeta padre.

## Para qué

Para **materiales autocontenidos que se comparten** (decks, one-pagers HTML/PDF que se mandan por fuera): los PNG master pesan 1-4 MB cada uno, inviable embeberlos en base64. Estas lite pesan 18-85 KB, embebibles sin inflar el archivo.

- **PNG master** (carpeta padre): para web con assets servidos aparte, o reedición.
- **Lite JPEG** (aquí): para embeber en base64 en HTML standalone.

El chasis `snippets_html/plantilla_deck.html` embebe 6 de estas lite como clases de textura (`.slide.tex-paper`, `.tex-signal`, `.tex-focus`, `.tex-haze`, `.tex-rightmist`, `.tex-leftmist`). Ver la regla de texturas en `marca/reglas_presentaciones_html.md`.

## Regenerar

```
sips -s format jpeg -s formatOptions 66 -Z 900 <master.png> --out lite/<nombre>.jpg
```

El JPEG no conserva alpha; las texturas son fondos full-bleed sin transparencia, así que no aplica.
