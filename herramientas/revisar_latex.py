"""Revisión estática de entrega_lista3/main.tex, para cuando no hay LaTeX a la mano.

No sustituye a compilar, pero detecta lo que más suele romper una compilación: llaves y entornos sin cerrar,
filas de tablas con un número de columnas distinto al de su encabezado, caracteres especiales sin escapar,
`$` impares y figuras que no existen.

Uso: python herramientas/revisar_latex.py [ruta/a/main.tex]
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONOCIDOS = {
    # núcleo y paquetes cargados
    "documentclass", "usepackage", "begin", "end", "section", "subsection", "subsubsection", "tableofcontents", "clearpage", "appendix",
    "textbf", "emph", "texttt", "textcolor", "caption", "captionof", "label", "ref", "item", "centering", "small", "large", "Large",
    "bfseries", "vspace", "includegraphics", "linewidth", "textwidth", "figauto", "newcommand", "renewcommand", "setlength", "setlist",
    "captionsetup", "pagestyle", "fancyhf", "lhead", "chead", "rhead", "cfoot", "thepage", "fancypagestyle", "headrulewidth", "decimalpoint",
    "toprule", "midrule", "bottomrule", "endhead", "hfill", "ifdim", "else", "fi", "dimexpr", "parindent", "parskip", "hline",
    "textordfeminine", "textordmasculine", "ldots", "textbackslash", "noindent",
    # matemáticas
    "lambda", "emptyset", "Sigma", "delta", "hat", "xrightarrow", "to", "rightarrow", "cup", "cap", "bigcup", "in", "notin", "mathtt", "mathrm",
    "varepsilon", "omega", "leq", "geq", "neq", "mathbb", "big", "Big", "text", "cdot", "star", "times", "subseteq", "leftrightarrow",
    "equiv", "neg", "forall", "exists", "bigl", "bigr",
    # acentos y símbolos de texto
    "ref", "hyperref", "tabular", "longtable",
}
ESPECIALES_ACENTOS = {"'", '"', "~", "^", "`", ",", ";", "!", ":", " ", "{", "}", "&", "%", "$", "#", "_", "\\", "[", "]", "(", ")", "/", "-", "."}


def sin_comentarios(texto):
    return re.sub(r"(?<!\\)%.*$", "", texto, flags=re.M)


def revisar(ruta):
    errores, avisos = [], []
    crudo = ruta.read_text(encoding="utf-8")
    texto = sin_comentarios(crudo)

    # llaves
    profundidad, linea = 0, 1
    for i, c in enumerate(texto):
        if c == "\n":
            linea += 1
        elif c == "\\" and i + 1 < len(texto) and texto[i + 1] in "{}\\":
            continue
        elif c in "{}" and i > 0 and texto[i - 1] == "\\" and (i < 2 or texto[i - 2] != "\\"):
            continue
        elif c == "{":
            profundidad += 1
        elif c == "}":
            profundidad -= 1
            if profundidad < 0:
                errores.append(f"línea {linea}: llave de cierre de más")
                profundidad = 0
    if profundidad:
        errores.append(f"{profundidad} llave(s) sin cerrar al final")

    # entornos
    pila = []
    for m in re.finditer(r"\\(begin|end)\{([A-Za-z*]+)\}", texto):
        linea = texto.count("\n", 0, m.start()) + 1
        if m.group(1) == "begin":
            pila.append((m.group(2), linea))
        elif not pila or pila[-1][0] != m.group(2):
            errores.append(f"línea {linea}: \\end{{{m.group(2)}}} no corresponde a {pila[-1] if pila else 'ningún begin'}")
        else:
            pila.pop()
    errores += [f"línea {l}: \\begin{{{n}}} sin cerrar" for n, l in pila]

    # dólares y caracteres especiales fuera de las fórmulas
    sin_escapes = re.sub(r"\\\$", "", texto)
    if sin_escapes.count("$") % 2:
        errores.append("número impar de $ (una fórmula quedó abierta)")
    partes = re.split(r"(?<!\\)\$", texto)
    fuera = "".join(partes[0::2])
    cuerpo = fuera[fuera.index(r"\begin{document}"):] if r"\begin{document}" in fuera else fuera
    for patron, nombre in ((r"(?<!\\)_", "_"), (r"(?<!\\)\^", "^"), (r"(?<!\\)#", "#")):
        for m in re.finditer(patron, cuerpo):
            contexto = cuerpo[max(0, m.start() - 25):m.end() + 25].replace("\n", " ")
            errores.append(f"«{nombre}» sin escapar fuera de una fórmula: …{contexto}…")
            break

    # tablas: columnas por fila
    for m in re.finditer(r"\\begin\{(tabular|longtable)\}\{", texto):
        i = m.end()
        nivel, j = 1, i
        while nivel and j < len(texto):
            nivel += (texto[j] == "{") - (texto[j] == "}")
            j += 1
        spec = texto[i:j - 1]
        columnas = 0
        k = 0
        while k < len(spec):
            c = spec[k]
            if c in "lcr":
                columnas += 1
            elif c in "p":
                columnas += 1
                k = spec.index("}", k)
            elif c == "@":
                k = spec.index("}", k)
            k += 1
        fin = texto.index(r"\end{" + m.group(1) + "}", j)
        cuerpo_tabla = texto[j:fin]
        for fila in re.split(r"\\\\", cuerpo_tabla):
            limpia = re.sub(r"\\(toprule|midrule|bottomrule|endhead)", "", fila).strip()
            if not limpia:
                continue
            sin_mates = "".join(re.split(r"(?<!\\)\$", limpia)[0::2])
            cuenta = len(re.findall(r"(?<!\\)&", sin_mates))
            if cuenta != columnas - 1:
                linea = texto.count("\n", 0, fin) + 1
                errores.append(f"tabla cerca de la línea {linea}: la fila «{limpia[:60]}…» tiene {cuenta + 1} columnas y la tabla {columnas}")
                break

    # figuras
    carpeta = ruta.parent
    for m in re.finditer(r"\\(?:figauto|includegraphics(?:\[[^\]]*\])?)\{([^}]+)\}", texto):
        nombre = m.group(1)
        if nombre.isdigit() or nombre.startswith('#'):
            continue
        if not any((carpeta / (nombre + ext)).exists() for ext in ("", ".pdf", ".png", ".jpg", ".jpeg")):
            errores.append(f"falta la imagen {nombre}")

    # comandos desconocidos
    usados = set(re.findall(r"\\([A-Za-z]+)", texto))
    definidos = set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", texto))
    desconocidos = sorted(usados - CONOCIDOS - definidos)
    if desconocidos:
        avisos.append("comandos que revisar a mano: " + ", ".join(desconocidos))
    return errores, avisos, texto


def main():
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "entrega_lista3" / "main.tex"
    errores, avisos, texto = revisar(ruta)
    print(f"{ruta.name}: {len(texto.splitlines())} líneas, {len(re.findall(r'figauto|includegraphics', texto))} figuras, "
          f"{len(re.findall(r'begin.(?:tabular|longtable)', texto))} tablas")
    for a in avisos:
        print("AVISO:", a)
    for e in errores[:40]:
        print("ERROR:", e)
    print("sin errores" if not errores else f"{len(errores)} error(es)")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
