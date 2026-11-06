"""Piezas comunes para generar el documento de LaTeX: escape de texto, tablas, figuras (SVG del simulador a PDF), pruebas."""

import hashlib
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import construcciones as C                          # noqa: E402
import controlador as K                             # noqa: E402
import dibujo as D                                  # noqa: E402
import ejercicios as E                              # noqa: E402
import expresiones as X                             # noqa: E402
import formatos as F                                # noqa: E402
from automata import formatear_conjunto             # noqa: E402

SALIDA = RAIZ / "entrega_lista3"
IMG = SALIDA / "img"
CAPTURAS = RAIZ / "herramientas" / "capturas"
ALUMNO = {"nombre": "Diego Polo Santoscoy", "boleta": "2025630828", "grupo": "4CV4", "profesor": "Gabriel Hurtado Avilés"}


# ---------------------------------------------------------------------------
# Texto a LaTeX
# ---------------------------------------------------------------------------

_MAPA = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
         "^": r"\^{}", "~": r"\~{}", "λ": r"$\lambda$", "∅": r"$\emptyset$", "Σ": r"$\Sigma$", "δ": r"$\delta$",
         "∈": r"$\in$", "∉": r"$\notin$", "∪": r"$\cup$", "→": r"$\to$", "–": "--", "—": "---", "ω": r"$\omega$",
         "·": r"$\cdot$", "≤": r"$\leq$", "≥": r"$\geq$", "≠": r"$\neq$", "ⁿ": r"$^{n}$", "²": r"$^{2}$", "⁺": r"$^{+}$",
         "′": "'", "×": r"$\times$", "…": r"\ldots{}", "★": r"$\star$", "ε": r"$\varepsilon$", "⊆": r"$\subseteq$",
         "↔": r"$\leftrightarrow$", "≡": r"$\equiv$", "∩": r"$\cap$", "¬": r"$\neg$", "∀": r"$\forall$", "∃": r"$\exists$"}


def tx(texto):
    """Texto normal con los caracteres especiales de LaTeX escapados y los símbolos matemáticos convertidos."""
    texto = str(texto).replace("δ̂", "\u0001")
    return "".join(_MAPA.get(c, c) for c in texto).replace("\u0001", r"$\hat{\delta}$")


def er_tex(texto):
    """Expresión regular (notación del curso) en modo matemático."""
    t = "".join(str(texto).split())
    t = t.replace("λ", r"\lambda ").replace("∅", r"\emptyset ").replace("*", "^{*}")
    return f"${t}$"


def mono(w):
    """Cadena de entrada: en tipo máquina, y λ si es la vacía."""
    return r"$\lambda$" if w == "" else r"\texttt{" + tx(w) + "}"


def conj(a, estados):
    estados = a._ordenar(estados)
    return r"$\emptyset$" if not estados else r"$\{$" + ", ".join(tx(q) for q in estados) + r"$\}$"


def traza_tex(a, recorrido):
    partes = [conj(a, recorrido.pasos[0].conjunto)]
    for p in recorrido.pasos[1:]:
        partes.append(r"$\xrightarrow{\texttt{" + tx(p.simbolo) + "}}$ " + conj(a, p.conjunto))
    return " ".join(partes)


def etiqueta_estado(a, q):
    marca = (r"$\rightarrow$" if q == a.inicial else "") + ("$*$" if a.es_aceptacion(q) else "")
    return (marca + " " if marca else "") + tx(q)


def celda(a, destinos):
    if not destinos:
        return r"$\emptyset$"
    if a.tipo == "AFD":
        return tx(destinos[0])
    return r"$\{$" + ", ".join(tx(q) for q in destinos) + r"$\}$"


def tabla_tex(a, pie=True):
    """Tabla de transiciones como tabular (longtable si es larga)."""
    columnas, filas = a.tabla()
    cabeza = " & ".join([r"\textbf{Estado}"] + [r"\textbf{" + (r"$\lambda$" if c == "" else r"\texttt{" + tx(c) + "}") + "}" for c in columnas])
    cuerpo = [" & ".join([etiqueta_estado(a, q)] + [celda(a, f[c]) for c in columnas]) + r" \\" for q, f in filas]
    formato = "l|" + "c" * len(columnas)
    if len(filas) > 22:
        lineas = [r"\begin{center}\small", r"\begin{longtable}{" + formato + "}", r"\toprule", cabeza + r" \\", r"\midrule", r"\endhead"]
        lineas += cuerpo + [r"\bottomrule", r"\end{longtable}", r"\end{center}"]
    else:
        lineas = [r"\begin{center}\small", r"\begin{tabular}{" + formato + "}", r"\toprule", cabeza + r" \\", r"\midrule"]
        lineas += cuerpo + [r"\bottomrule", r"\end{tabular}", r"\end{center}"]
    return "\n".join(lineas)


def tabla_simple(encabezados, filas, formato=None, chica=True):
    formato = formato or "l" * len(encabezados)
    entorno = "longtable" if len(filas) > 22 else "tabular"
    lineas = [r"\begin{center}" + (r"\small" if chica else ""), r"\begin{" + entorno + "}{" + formato + "}", r"\toprule",
              " & ".join(r"\textbf{" + e + "}" for e in encabezados) + r" \\", r"\midrule"]
    if entorno == "longtable":
        lineas.append(r"\endhead")
    lineas += [" & ".join(f) + r" \\" for f in filas] + [r"\bottomrule", r"\end{" + entorno + "}", r"\end{center}"]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Figuras (SVG del simulador → PDF recortado)
# ---------------------------------------------------------------------------

class Figuras:
    def __init__(self):
        try:
            import pymupdf
        except ImportError:
            sys.exit("Falta PyMuPDF: ejecuta  pip install pymupdf")
        self.pymupdf = pymupdf
        self.hechas = {}
        IMG.mkdir(parents=True, exist_ok=True)

    def pdf(self, a, activos=(), resaltadas=()):
        """Escribe el diagrama como PDF vectorial recortado; devuelve (nombre sin extensión, ancho, alto) en puntos."""
        svg = D.svg_automata(a, activos, resaltadas, titulo="")
        clave = hashlib.sha1(svg.encode("utf-8")).hexdigest()[:10]
        if clave in self.hechas:
            return self.hechas[clave]
        pm = self.pymupdf
        pdf = pm.open("pdf", pm.open(stream=svg.encode("utf-8"), filetype="svg").convert_to_pdf())
        pagina = pdf[0]
        caja = pm.Rect()
        for d in pagina.get_drawings():
            r = d["rect"]
            if r.width >= pagina.rect.width * 0.95 and r.height >= pagina.rect.height * 0.95:
                continue                                          # el fondo blanco
            caja |= r
        for bloque in pagina.get_text("blocks"):
            caja |= pm.Rect(bloque[:4])
        caja = pm.Rect(caja.x0 - 6, caja.y0 - 6, caja.x1 + 6, caja.y1 + 6) & pagina.rect
        pagina.set_cropbox(caja)
        nombre = f"d{clave}"
        pdf.save(IMG / f"{nombre}.pdf", garbage=3, deflate=True)
        self.hechas[clave] = (nombre, round(caja.width, 1), round(caja.height, 1))
        return self.hechas[clave]


FIG = None


def figura(a, titulo, activos=(), resaltadas=(), etiqueta=None):
    nombre, w, h = FIG.pdf(a, activos, resaltadas)
    return (r"\begin{figure}[H]\centering" + "\n" + r"\figauto{img/" + nombre + "}{" + str(w) + "}\n" +
            r"\caption{" + titulo + "}" + (r"\label{" + etiqueta + "}" if etiqueta else "") + "\n" + r"\end{figure}")


def figuras_en_pares(a, corridas):
    """Una figura por corrida (estado final de la simulación); de dos en dos si caben."""
    piezas = []
    for w, r in corridas:
        paso = r.pasos[-1]
        veredicto = "acepta" if r.aceptada else "rechaza"
        if paso.conjunto:
            nombre, ancho, alto = FIG.pdf(a, paso.conjunto, paso.tomadas)
            pie = f"Ejecución con {mono(w)}: {veredicto}; estados activos al terminar: {conj(a, paso.conjunto)}."
        else:                       # el autómata se bloqueó: se muestra el último paso con estados activos
            k = max(i for i, p in enumerate(r.pasos) if p.conjunto)
            nombre, ancho, alto = FIG.pdf(a, r.pasos[k].conjunto, r.pasos[k].tomadas)
            pie = (f"Ejecución con {mono(w)}: {veredicto}. Se muestra el paso {k}, el último con estados activos "
                   f"({conj(a, r.pasos[k].conjunto)}); al leer {mono(r.pasos[k + 1].simbolo)} ninguna transición sigue y el autómata se bloquea.")
        piezas.append((nombre, ancho, pie))
    if len(piezas) == 2 and all(p[1] <= 232 for p in piezas):
        columnas = [r"\begin{minipage}[t]{.49\textwidth}\centering" + "\n" + r"\figauto{img/" + n + "}{" + str(w) + "}\n"
                    + r"\captionof{figure}{" + c + "}\n" + r"\end{minipage}" for n, w, c in piezas]
        return "\\begin{center}\n" + "\n\\hfill\n".join(columnas) + "\n\\end{center}"
    return "\n".join(r"\begin{figure}[H]\centering" + "\n" + r"\figauto{img/" + n + "}{" + str(w) + "}\n" + r"\caption{" + c + "}\n"
                     r"\end{figure}" for n, w, c in piezas)


# ---------------------------------------------------------------------------
# Casos de prueba y ejecuciones
# ---------------------------------------------------------------------------

def elegir_para_figura(a, buenas, malas):
    """Una válida (la más corta de al menos 2 símbolos) y una inválida (de preferencia con la que el autómata se bloquea)."""
    valida = next((w for w in buenas if len(w) >= 2), buenas[0] if buenas else None)
    bloqueadas = [w for w in malas if len(w) >= 2 and not a.simular(w).pasos[-1].conjunto]
    invalida = bloqueadas[0] if bloqueadas else next((w for w in malas if len(w) >= 2), malas[0] if malas else None)
    return [w for w in (valida, invalida) if w is not None]


def pruebas(a, validas=5, invalidas=5, con_figuras=True):
    """Tabla de cadenas válidas e inválidas con su recorrido, y las figuras de una válida y una inválida."""
    buenas, malas = K.casos_de_prueba(a, validas, invalidas)
    no_det = a.tipo != "AFD"
    filas = []
    for tipo, grupo in (("válida", buenas), ("inválida", malas)):
        for w in grupo:
            r = a.simular(w)
            fila = [tipo, mono(w), "acepta" if r.aceptada else "rechaza", traza_tex(a, r)]
            if no_det:
                c = a.caminos(w, limite=500)
                fila.insert(3, f"{len(c.caminos)}{'+' if c.truncado else ''} ({sum(x.aceptado for x in c.caminos)})")
            filas.append(fila)
    if no_det:
        formato = r"@{}l p{1.9cm} l c p{7cm}@{}"
        encabezado = ["Tipo", "Cadena", "Resultado", "Caminos (acept.)", "Recorrido: estados activos"]
    else:
        formato = r"@{}l p{1.9cm} l p{8.2cm}@{}"
        encabezado = ["Tipo", "Cadena", "Resultado", "Recorrido: estados activos"]
    texto = tabla_simple(encabezado, filas, formato)
    if len(buenas) < validas:
        texto += f"\n\\noindent\\emph{{El lenguaje solo tiene {len(buenas)} cadena(s) válida(s); no se pueden dar {validas}.}}\n"
    corridas = [(w, a.simular(w)) for w in elegir_para_figura(a, buenas, malas)] if con_figuras else []
    return texto + ("\n" + figuras_en_pares(a, corridas) if corridas else "")


def con_nombre(e):
    a = e.fabrica()
    a.nombre = e.nombre
    return a


def por_nombre(nombre):
    return con_nombre(E.POR_NOMBRE[nombre])


def datos(a):
    tipo = a.tipo.replace("-lambda", r"-$\lambda$")
    return f"{tipo}, {len(a.estados)} estados, {len(a.transiciones())} transiciones"
