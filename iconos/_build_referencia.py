#!/usr/bin/env python3
"""
Genera iconos/_referencia.html a partir de los SVG que hay en la carpeta.

La pagina anterior estaba escrita a mano y se desfaso: declaraba 23 glifos,
tenia los 23 del set base incrustados y cero de los 10 de industrias. Se
genera para que la hoja de contacto no pueda volver a mentir sobre el set.

Ademas valida la disciplina de linea: todo icono tiene que ser viewBox
"0 0 24 24" y stroke-width 1.25. Si alguno se sale, aborta y lo dice.

Uso:
  python3 00_imberion/marca/iconos/_build_referencia.py
  python3 00_imberion/marca/iconos/_build_referencia.py --check   # exit 1 si hay drift
"""
import html
import re
import sys
from pathlib import Path

ICONOS = Path(__file__).resolve().parent
SALIDA = ICONOS / "_referencia.html"

VIEWBOX = "0 0 24 24"
STROKE = "1.25"


def leer_svgs(directorio):
    """(nombre, marcado_inline) de cada SVG, ordenado alfabeticamente."""
    fuera = []
    for ruta in sorted(directorio.glob("*.svg")):
        marcado = ruta.read_text().strip()
        marcado = re.sub(r"<\?xml[^>]*\?>\s*", "", marcado)
        marcado = re.sub(r"<!--.*?-->", "", marcado, flags=re.S).strip()
        fuera.append((ruta.stem, marcado))
    return fuera


def validar(nombre, marcado, problemas):
    if f'viewBox="{VIEWBOX}"' not in marcado:
        problemas.append(f"{nombre}: viewBox distinto de \"{VIEWBOX}\"")
    anchos = set(re.findall(r'stroke-width="([^"]+)"', marcado))
    if anchos and anchos != {STROKE}:
        problemas.append(f"{nombre}: stroke-width {sorted(anchos)} en vez de {STROKE}")


def celdas(items):
    fuera = []
    for nombre, marcado in items:
        etiqueta = html.escape(nombre.replace("_", " "))
        fuera.append(
            f'    <figure class="ic">{marcado}'
            f'<figcaption>{etiqueta}</figcaption></figure>'
        )
    return "\n".join(fuera)


PAGINA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Iconografía · Imberion</title>
<!-- GENERADO por iconos/_build_referencia.py. No editar a mano: se regenera. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/imberion_base.css">
<style>
  body {{ padding: var(--space-9) var(--space-6); background: var(--cream); }}
  .hoja {{ max-width: var(--max); margin: 0 auto; }}
  .hoja > header {{ margin-bottom: var(--space-8); }}
  .hoja h1 {{ margin-bottom: var(--space-4); }}
  .hoja .lead + .lead {{ margin-top: var(--space-4); }}

  .set {{ margin-top: var(--space-8); }}
  .set > h2 {{ font-size: var(--display-5); margin-bottom: var(--space-2); }}
  .set > .nota {{
    font-size: var(--text-sm); color: var(--navy-60);
    margin-bottom: var(--space-5); max-width: var(--measure);
  }}

  /* Las hairlines viven en la celda y no como fondo del contenedor: con gap
     sobre fondo, la ultima fila incompleta deja bloques grises colgando. */
  .rejilla {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(132px, 1fr));
    border-top: 1px solid var(--navy-12);
    border-left: 1px solid var(--navy-12);
  }}
  .ic {{
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: var(--space-3);
    aspect-ratio: 1;
    background: var(--white);
    border-right: 1px solid var(--navy-12);
    border-bottom: 1px solid var(--navy-12);
    margin: 0;
  }}
  .ic svg {{ width: 28px; height: 28px; color: var(--navy); }}
  .ic figcaption {{
    font-size: var(--text-2xs); letter-spacing: .14em; text-transform: uppercase;
    color: var(--navy-60); font-weight: 500; text-align: center; padding: 0 var(--space-2);
  }}

  /* Prueba sobre navy: el set tiene que sostenerse invertido, que es como
     aparece en portadas y secciones oscuras. */
  .rejilla--oscura {{ border-top-color: var(--white-16); border-left-color: var(--white-16); }}
  .rejilla--oscura .ic {{
    background: var(--navy);
    border-right-color: var(--white-16);
    border-bottom-color: var(--white-16);
  }}
  .rejilla--oscura .ic svg {{ color: var(--fg-on-dark); }}
  .rejilla--oscura .ic figcaption {{ color: var(--fg-on-dark-subtle); }}

  /* Escalas reales de uso, para ver donde el trazo de 1.25 se rompe. */
  .escalas {{ display: flex; align-items: flex-end; gap: var(--space-7); flex-wrap: wrap; }}
  .escala {{ display: flex; flex-direction: column; align-items: center; gap: var(--space-2); }}
  .escala svg {{ color: var(--navy); }}
  .escala span {{ font-size: var(--text-2xs); color: var(--navy-60); letter-spacing: .1em; }}
</style>
</head>
<body>
<main class="hoja">
  <header>
    <h1>Iconografía Imberion</h1>
    <p class="lead">Set editorial de línea propia: {total} glifos en dos familias, trazo 1.25&nbsp;px sobre lienzo de 24&nbsp;px, esquinas redondeadas, sin rellenos salvo el punto de glifo y la señal de marca.</p>
    <p class="lead">Se extiende dibujando dentro de este vocabulario. No se importa Lucide, Heroicons ni Feather: el grosor de línea propio es lo que hace que un documento se lea como de Imberion y no como una plantilla.</p>
  </header>

  <section class="set">
    <h2>Escalas de uso</h2>
    <p class="nota">A 16&nbsp;px el trazo de 1.25 empieza a cerrar los contraformas de los glifos densos (data, industrial). Por debajo de 20&nbsp;px, preferir los glifos simples.</p>
    <div class="escalas">{escalas}</div>
  </section>

  <section class="set">
    <h2>Set base</h2>
    <p class="nota">{n_base} glifos de concepto comercial y analítico. Los cuatro de cierre (alert, help, cross, check) son la sub-familia utilitaria de estado y anotación.</p>
    <div class="rejilla">
{base}
    </div>
  </section>

  <section class="set">
    <h2>Industrias</h2>
    <p class="nota">{n_ind} glifos de sector, para portadas y páginas de industria. Mismo trazo y mismo lienzo que el set base.</p>
    <div class="rejilla">
{industrias}
    </div>
  </section>

  <section class="set">
    <h2>Sobre navy</h2>
    <p class="nota">El mismo set en contexto oscuro. Se pinta con <code>color</code> heredado (los SVG usan <code>currentColor</code>), no con <code>filter: invert</code>.</p>
    <div class="rejilla rejilla--oscura">
{oscuro}
    </div>
  </section>
</main>
</body>
</html>
"""


def main():
    check = "--check" in sys.argv
    base = leer_svgs(ICONOS)
    industrias = leer_svgs(ICONOS / "industrias")

    problemas = []
    for nombre, marcado in base + industrias:
        validar(nombre, marcado, problemas)
    if problemas:
        print("Iconos fuera de la disciplina de linea:")
        for p in problemas:
            print(f"  - {p}")
        sys.exit(1)

    muestra = dict(base)["signal"]
    filas = []
    for px in (16, 20, 24, 32, 48):
        svg = muestra.replace("<svg ", f'<svg width="{px}" height="{px}" ', 1)
        filas.append(f'      <div class="escala">{svg}<span>{px} px</span></div>')
    escalas = "\n".join(filas)

    pagina = PAGINA.format(
        total=len(base) + len(industrias),
        n_base=len(base),
        n_ind=len(industrias),
        base=celdas(base),
        industrias=celdas(industrias),
        oscuro=celdas(base),
        escalas=escalas,
    )

    if check:
        actual = SALIDA.read_text() if SALIDA.exists() else ""
        if actual != pagina:
            print("DRIFT: _referencia.html no coincide con los SVG de la carpeta.")
            print("Corre: python3 00_imberion/marca/iconos/_build_referencia.py")
            sys.exit(1)
        print(f"OK: _referencia.html al dia ({len(base)} base + {len(industrias)} industrias).")
        return

    SALIDA.write_text(pagina)
    print(f"Generado: _referencia.html ({len(base)} base + {len(industrias)} industrias)")


if __name__ == "__main__":
    main()
