"""Expresiones regulares y su obtención a partir de un autómata por eliminación de estados.

No depende de Flet. Se usa la notación del curso: `+` es la unión, la yuxtaposición es la concatenación,
`*` es la cerradura de Kleene, `λ` es la cadena vacía y `∅` el lenguaje vacío.
"""

import re
from dataclasses import dataclass
from itertools import permutations

from lenguajes import LAMBDA

VACIO = "∅"


# ---------------------------------------------------------------------------
# Árbol de la expresión, con constructores que simplifican
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ER:
    tipo: str            # "vacio", "lambda", "simbolo", "union", "concat", "estrella"
    valor: object = None  # el símbolo, o la tupla de partes, o la expresión

    def __str__(self):
        return a_texto(self)

    def __repr__(self):
        return f"ER({a_texto(self)!r})"


ER_VACIO = ER("vacio")
ER_LAMBDA = ER("lambda")


def simbolo(c):
    return ER("simbolo", c)


def union(*partes):
    """Unión: aplana, quita repeticiones y ∅; con una sola parte devuelve esa parte."""
    plano = []
    for p in partes:
        for q in (p.valor if p.tipo == "union" else (p,)):
            if q.tipo != "vacio" and q not in plano:
                plano.append(q)
    if not plano:
        return ER_VACIO
    return plano[0] if len(plano) == 1 else ER("union", tuple(plano))


def concat(*partes):
    """Concatenación: aplana, quita λ y devuelve ∅ si alguna parte es ∅."""
    plano = []
    for p in partes:
        if p.tipo == "vacio":
            return ER_VACIO
        for q in (p.valor if p.tipo == "concat" else (p,)):
            if q.tipo != "lambda":
                plano.append(q)
    if not plano:
        return ER_LAMBDA
    return plano[0] if len(plano) == 1 else ER("concat", tuple(plano))


def estrella(e):
    if e.tipo in ("vacio", "lambda"):
        return ER_LAMBDA
    if e.tipo == "estrella":
        return e
    if e.tipo == "union":                       # (λ + a)* = a*
        sin_lambda = [p for p in e.valor if p.tipo != "lambda"]
        if len(sin_lambda) != len(e.valor):
            return estrella(union(*sin_lambda))
    return ER("estrella", e)


# ---------------------------------------------------------------------------
# Texto y expresión de Python (para comprobar)
# ---------------------------------------------------------------------------

def a_texto(e, contexto=0):
    """contexto: 0 = raíz, 1 = dentro de una unión, 2 = dentro de una concatenación, 3 = dentro de una estrella."""
    if e.tipo == "vacio":
        return VACIO
    if e.tipo == "lambda":
        return LAMBDA
    if e.tipo == "simbolo":
        return e.valor
    if e.tipo == "estrella":
        return a_texto(e.valor, 3) + "*"
    if e.tipo == "concat":
        texto = "".join(a_texto(p, 2) for p in e.valor)
        return f"({texto})" if contexto == 3 else texto
    texto = "+".join(a_texto(p, 1) for p in e.valor)
    return f"({texto})" if contexto >= 2 else texto


def a_python(e):
    """La misma expresión en la sintaxis de `re`, para comparar con el autómata."""
    if e.tipo == "vacio":
        return "(?!)"
    if e.tipo == "lambda":
        return ""
    if e.tipo == "simbolo":
        return re.escape(e.valor)
    if e.tipo == "estrella":
        return f"(?:{a_python(e.valor)})*"
    if e.tipo == "concat":
        return "".join(f"(?:{a_python(p)})" for p in e.valor)
    return "(?:" + "|".join(a_python(p) for p in e.valor) + ")"


def acepta(e, w):
    """True si la cadena pertenece al lenguaje de la expresión."""
    return re.fullmatch(a_python(e), w) is not None


# ---------------------------------------------------------------------------
# Eliminación de estados
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PasoDeEliminacion:
    eliminado: str
    aristas: tuple        # (origen, destino, expresión en texto) después de eliminar el estado


def _aristas_iniciales(a):
    """Autómata generalizado: estados nuevos «inicio» y «fin», y una expresión en cada arista."""
    aristas = {}

    def sumar(p, q, e):
        aristas[(p, q)] = union(aristas.get((p, q), ER_VACIO), e)

    sumar("inicio", a.inicial, ER_LAMBDA)
    for q in a.aceptacion:
        sumar(q, "fin", ER_LAMBDA)
    for desde, lee, hacia in a.transiciones():
        sumar(desde, hacia, simbolo(lee) if lee else ER_LAMBDA)
    return aristas


def eliminar_en_orden(a, orden):
    """Expresión del autómata eliminando los estados en el orden dado, y los pasos intermedios."""
    aristas = _aristas_iniciales(a)
    vivos = list(a.estados)
    pasos = []
    for k in orden:
        lazo = estrella(aristas.get((k, k), ER_VACIO))
        entradas = [(p, e) for (p, q), e in aristas.items() if q == k and p != k]
        salidas = [(q, e) for (p, q), e in aristas.items() if p == k and q != k]
        for clave in [c for c in aristas if k in c]:
            del aristas[clave]
        for p, e_in in entradas:
            for q, e_out in salidas:
                aristas[(p, q)] = union(aristas.get((p, q), ER_VACIO), concat(e_in, lazo, e_out))
        vivos.remove(k)
        pasos.append(PasoDeEliminacion(k, tuple((p, q, a_texto(e)) for (p, q), e in sorted(aristas.items()))))
    return aristas.get(("inicio", "fin"), ER_VACIO), pasos


def desde_automata(a, orden=None):
    """Expresión regular del autómata. Si no se da el orden de eliminación, se prueban todos (hasta 6
    estados) y se queda la más corta. Devuelve (expresión, orden usado, pasos)."""
    ordenes = [list(orden)] if orden else (list(permutations(a.estados)) if len(a.estados) <= 6 else [list(a.estados)])
    mejor = None
    for o in ordenes:
        e, pasos = eliminar_en_orden(a, o)
        if mejor is None or len(a_texto(e)) < len(a_texto(mejor[0])):
            mejor = (e, list(o), pasos)
    return mejor


# ---------------------------------------------------------------------------
# Análisis de la notación del curso
# ---------------------------------------------------------------------------

class ErrorDeSintaxis(ValueError):
    """El texto no es una expresión regular bien escrita."""


def parsear(texto):
    """Expresión regular a partir de su texto: `+` unión, yuxtaposición concatenación, `*` estrella, `λ`, `∅` y paréntesis.
    Los espacios se ignoran y cualquier otro carácter es un símbolo."""
    texto = "".join(texto.split())
    posicion = 0

    def mirar():
        return texto[posicion] if posicion < len(texto) else ""

    def union_():
        nonlocal posicion
        partes = [concatenacion()]
        while mirar() == "+":
            posicion += 1
            partes.append(concatenacion())
        return union(*partes)

    def concatenacion():
        partes = []
        while mirar() not in ("", "+", ")"):
            partes.append(estrella_())
        if not partes:
            raise ErrorDeSintaxis(f"Falta una expresión cerca de la posición {posicion} de {texto!r}.")
        return concat(*partes)

    def estrella_():
        nonlocal posicion
        e = atomo()
        while mirar() == "*":
            posicion += 1
            e = estrella(e)
        return e

    def atomo():
        nonlocal posicion
        c = mirar()
        if c == "(":
            posicion += 1
            e = union_()
            if mirar() != ")":
                raise ErrorDeSintaxis(f"Falta cerrar un paréntesis en {texto!r}.")
            posicion += 1
            return e
        if c in ("*",):
            raise ErrorDeSintaxis(f"Una estrella sin nada que repetir en {texto!r}.")
        posicion += 1
        return ER_LAMBDA if c == LAMBDA else ER_VACIO if c == VACIO else simbolo(c)

    e = union_()
    if posicion != len(texto):
        raise ErrorDeSintaxis(f"Sobra «{texto[posicion:]}» en {texto!r}.")
    return e


def palabras(e, longitud_maxima, alfabeto=None):
    """Las cadenas del lenguaje de longitud hasta `longitud_maxima`, ordenadas por longitud y luego alfabéticamente."""
    from itertools import product
    if alfabeto is None:
        alfabeto = sorted(_simbolos(e))
    return [w for n in range(longitud_maxima + 1) for t in product(alfabeto, repeat=n) for w in ["".join(t)] if acepta(e, w)]


def _simbolos(e):
    if e.tipo == "simbolo":
        return {e.valor}
    if e.tipo in ("union", "concat"):
        return set().union(*(_simbolos(p) for p in e.valor))
    if e.tipo == "estrella":
        return _simbolos(e.valor)
    return set()
