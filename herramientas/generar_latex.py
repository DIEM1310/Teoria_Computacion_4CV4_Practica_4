"""Genera el proyecto de LaTeX (para Overleaf) con la 3.ª Lista resuelta, con figuras de cada autómata en ejecución.

Uso, desde la raíz del repositorio:

    pip install pymupdf        # solo para convertir los diagramas SVG a PDF; no hace falta para las pruebas
    python herramientas/generar_latex.py

Escribe entrega_lista3/ (main.tex y img/) y entrega_lista3_overleaf.zip. En Overleaf: New Project → Upload Project →
el .zip; el compilador es pdfLaTeX (el predeterminado). Las capturas del simulador que haya en
herramientas/capturas/ se agregan en un anexo.
"""

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import latex_base as B           # noqa: E402
import latex_secciones as S      # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sin-zip", action="store_true", help="no crea entrega_lista3_overleaf.zip")
    args = parser.parse_args()
    if B.SALIDA.exists():
        shutil.rmtree(B.SALIDA)
    B.SALIDA.mkdir(parents=True)
    B.FIG = B.Figuras()
    texto = S.construir()
    (B.SALIDA / "main.tex").write_text(texto, encoding="utf-8", newline="\n")
    figuras = len(list(B.IMG.glob("*.pdf")))
    print(f"entrega_lista3/main.tex: {len(texto.splitlines())} líneas, {figuras} figuras en img/")
    if not args.sin_zip:
        # el nombre del .zip es el del proyecto en Overleaf y, por tanto, el del PDF que se descarga
        ruta = B.RAIZ / f"{B.ALUMNO['nombre'].replace(' ', '_')}_{B.ALUMNO['boleta']}.zip"
        with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
            for archivo in sorted(B.SALIDA.rglob("*")):
                if archivo.is_file():
                    z.write(archivo, archivo.relative_to(B.SALIDA).as_posix())
        print(f"{ruta.name}: {ruta.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
