"""Expresiones regulares y su obtención a partir de un autómata por eliminación de estados.

No depende de Flet. Se usa la notación del curso: `+` es la unión, la yuxtaposición es la concatenación,
`*` es la cerradura de Kleene, `λ` es la cadena vacía y `∅` el lenguaje vacío.
"""

import re
from dataclasses import dataclass
from itertools import count, permutations

import construcciones as C
from automata import Automata
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
# Práctica 4: de expresión regular a AFN-λ (teorema de Kleene, Parte I)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PasoDeConstruccion:
    """Una pieza de la construcción de Thompson: la subexpresión que se acaba de armar, el caso
    de la Parte I del teorema de Kleene que se aplicó y el autómata parcial resultante (con sus
    propios nombres de estado; el autómata final se renombra q0, q1, ... al terminar)."""
    expresion: str
    caso: str
    automata: "Automata"


def _nuevo_estado(generador):
    return f"t{next(generador)}"


def _automata_base(alfabeto, generador):
    """Dos estados nuevos: i inicial, f de aceptación, sin ninguna transición entre ellos."""
    i, f = _nuevo_estado(generador), _nuevo_estado(generador)
    return Automata(alfabeto, [i, f], i, [f])


def _final_unico(pieza):
    """El único estado de aceptación de una pieza de Thompson (por construcción siempre hay uno)."""
    return next(iter(pieza.aceptacion))


def _fundir(piezas, alfabeto, extra_estados=()):
    """Autómata con los estados y las transiciones de cada pieza (ya con nombres propios y sin
    repetidos) más `extra_estados`; todavía sin estado inicial ni de aceptación."""
    a = Automata(alfabeto, list(extra_estados))
    for pieza in piezas:
        for q in pieza.estados:
            a.agregar_estado(q)
    for pieza in piezas:
        for desde, lee, hacia in pieza.transiciones():
            a.agregar_transicion(desde, lee, hacia)
    return a


def _union_automata(piezas, alfabeto, generador):
    """Caso unión (+): un inicio y un final nuevos; el inicio llega por λ al inicio de cada pieza
    y el final de cada pieza llega por λ al final nuevo."""
    i, f = _nuevo_estado(generador), _nuevo_estado(generador)
    a = _fundir(piezas, alfabeto, [i, f])
    a.establecer_inicial(i)
    a.marcar_aceptacion(f)
    for pieza in piezas:
        a.agregar_transicion(i, "", pieza.inicial)
        a.agregar_transicion(_final_unico(pieza), "", f)
    return a


def _concat_automata(piezas, alfabeto):
    """Caso concatenación (yuxtaposición): sin estados nuevos; una λ del final de cada pieza al
    inicio de la siguiente. El inicio es el de la primera pieza; el final, el de la última."""
    a = _fundir(piezas, alfabeto)
    a.establecer_inicial(piezas[0].inicial)
    a.marcar_aceptacion(_final_unico(piezas[-1]))
    for anterior, siguiente in zip(piezas, piezas[1:]):
        a.agregar_transicion(_final_unico(anterior), "", siguiente.inicial)
    return a


def _estrella_automata(pieza, alfabeto, generador):
    """Caso cerradura (*): un inicio y un final nuevos, con cuatro λ: saltarse la pieza (inicio→
    final), entrar a ella (inicio→inicio de la pieza), repetirla (final de la pieza→inicio de la
    pieza) y terminar (final de la pieza→final). No se reutiliza el inicio ni el final de la
    pieza como los del resultado: el ejercicio 274 de la Lista 4 muestra que ahorrarse esos dos
    estados nuevos (haciendo final al inicio de la pieza y agregándole una λ de vuelta desde su
    final) acepta cadenas de más."""
    i, f = _nuevo_estado(generador), _nuevo_estado(generador)
    a = _fundir([pieza], alfabeto, [i, f])
    a.establecer_inicial(i)
    a.marcar_aceptacion(f)
    pf = _final_unico(pieza)
    a.agregar_transicion(i, "", pieza.inicial)
    a.agregar_transicion(i, "", f)
    a.agregar_transicion(pf, "", pieza.inicial)
    a.agregar_transicion(pf, "", f)
    return a


def _construir(e, alfabeto, generador, pasos):
    if e.tipo == "vacio":
        a = _automata_base(alfabeto, generador)
        caso = "Caso básico ∅: dos estados nuevos sin ninguna transición; no se acepta ninguna cadena."
    elif e.tipo == "lambda":
        a = _automata_base(alfabeto, generador)
        a.agregar_transicion(a.inicial, "", _final_unico(a))
        caso = "Caso básico λ: dos estados nuevos unidos por una transición λ."
    elif e.tipo == "simbolo":
        a = _automata_base(alfabeto, generador)
        a.agregar_transicion(a.inicial, e.valor, _final_unico(a))
        caso = f"Caso básico «{e.valor}»: dos estados nuevos unidos por una transición «{e.valor}»."
    elif e.tipo == "union":
        piezas = [_construir(p, alfabeto, generador, pasos) for p in e.valor]
        a = _union_automata(piezas, alfabeto, generador)
        caso = (f"Unión de {len(piezas)} partes (regla de +): un inicio y un final nuevos, con una λ "
                "del inicio a cada pieza y una λ de cada pieza al final.")
    elif e.tipo == "concat":
        piezas = [_construir(p, alfabeto, generador, pasos) for p in e.valor]
        a = _concat_automata(piezas, alfabeto)
        caso = (f"Concatenación de {len(piezas)} partes (yuxtaposición): sin estados nuevos, una λ "
                "del final de cada pieza al inicio de la siguiente.")
    elif e.tipo == "estrella":
        pieza = _construir(e.valor, alfabeto, generador, pasos)
        a = _estrella_automata(pieza, alfabeto, generador)
        caso = ("Cerradura de Kleene (regla de *): un inicio y un final nuevos, con λ para saltarse "
                "la pieza, λ para entrar a ella, λ para repetirla y λ para terminar.")
    else:
        raise ValueError(f"Tipo de expresión desconocido: {e.tipo!r}.")
    a.nombre = a_texto(e)
    pasos.append(PasoDeConstruccion(a_texto(e), caso, a))
    return a


def desde_expresion(e, alfabeto):
    """AFN-λ equivalente a `e` por la Parte I del teorema de Kleene (construcción de Thompson): los
    casos básicos ∅, λ y cada símbolo, y las construcciones de unión, concatenación y cerradura,
    cada una armada sobre los autómatas ya construidos para las subexpresiones.

    `alfabeto` es Σ (una lista, o un texto de un símbolo por carácter) y debe incluir todos los
    símbolos que aparecen en `e`. Devuelve (automata, pasos): el AFN-λ final, con los estados
    renombrados q0, q1, ... en el orden en que los recorre un BFS desde el inicial (construcciones.
    renombrar_secuencial), y la tupla de PasoDeConstruccion en el orden en que se arman las piezas
    (de las subexpresiones a la expresión completa), cada una con su propio autómata parcial, para
    mostrar la construcción paso a paso (ejercicio 272 de la Lista 4).
    """
    alfabeto = list(dict.fromkeys(alfabeto))
    if not alfabeto:
        raise ValueError("El alfabeto Σ no puede estar vacío.")
    faltan = sorted(_simbolos(e) - set(alfabeto))
    if faltan:
        raise ValueError(f"La expresión usa el símbolo «{faltan[0]}», que no está en Σ = {{{', '.join(alfabeto)}}}.")
    generador = count()
    pasos = []
    _construir(e, alfabeto, generador, pasos)
    final = C.renombrar_secuencial(pasos[-1].automata)
    pasos[-1] = PasoDeConstruccion(pasos[-1].expresion, pasos[-1].caso, final)
    return final, tuple(pasos)


# ---------------------------------------------------------------------------
# Eliminación de estados
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PasoDeEliminacion:
    eliminado: str
    aristas: tuple        # (origen, destino, expresión en texto) después de eliminar el estado


def aristas_iniciales(a):
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
    aristas = aristas_iniciales(a)
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


def _parsear_arbol(texto, hacer_union, hacer_concat, hacer_estrella):
    """Analizador recursivo descendente común a parsear() y parsear_sin_simplificar(); solo cambian
    los constructores con los que se arma cada operador (los que simplifican, o los literales). Toda
    expresión mal formada se rechaza con un ErrorDeSintaxis que indica la posición del error."""
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
        return hacer_union(*partes)

    def concatenacion():
        partes = []
        while mirar() not in ("", "+", ")"):
            partes.append(estrella_())
        if not partes:
            raise ErrorDeSintaxis(f"Falta una expresión cerca de la posición {posicion} de {texto!r}.")
        return hacer_concat(*partes)

    def estrella_():
        nonlocal posicion
        e = atomo()
        while mirar() == "*":
            posicion += 1
            e = hacer_estrella(e)
        return e

    def atomo():
        nonlocal posicion
        c = mirar()
        if c == "(":
            posicion += 1
            e = union_()
            if mirar() != ")":
                raise ErrorDeSintaxis(f"Falta cerrar un paréntesis abierto, cerca de la posición {posicion} de {texto!r}.")
            posicion += 1
            return e
        if c == "*":
            raise ErrorDeSintaxis(f"Una estrella sin nada que repetir, en la posición {posicion} de {texto!r}.")
        posicion += 1
        return ER_LAMBDA if c == LAMBDA else ER_VACIO if c == VACIO else simbolo(c)

    e = union_()
    if posicion != len(texto):
        raise ErrorDeSintaxis(f"Sobra «{texto[posicion:]}» en la posición {posicion} de {texto!r}.")
    return e


def parsear(texto):
    """Expresión regular a partir de su texto: `+` unión, yuxtaposición concatenación, `*` estrella, `λ`, `∅` y paréntesis.
    Los espacios se ignoran y cualquier otro carácter es un símbolo. El árbol se simplifica con las mismas
    reglas que union(), concat() y estrella() (aplana, quita ∅ y λ de más, funde estrellas); para el árbol
    literal, tal como se escribió, usa parsear_sin_simplificar (Práctica 4, construcción de Thompson)."""
    return _parsear_arbol(texto, union, concat, estrella)


def _union_cruda(*partes):
    return partes[0] if len(partes) == 1 else ER("union", tuple(partes))


def _concat_cruda(*partes):
    return partes[0] if len(partes) == 1 else ER("concat", tuple(partes))


def _estrella_cruda(e):
    return ER("estrella", e)


def parsear_sin_simplificar(texto):
    """Como parsear(), pero sin aplanar ni simplificar: cada `+`, cada yuxtaposición y cada `*` del
    texto da su propio nodo del árbol, tal como se escribió (incluida una unión con ∅ o con λ, que
    parsear() simplificaría). La usa desde_expresion (Ejercicio 2 de la Práctica 4) para que la
    construcción de Thompson arme una pieza por cada operador que escribió el usuario, también en
    los casos degenerados (ejercicio 272(e) de la Lista 4: `(a+λ)(b+∅)`)."""
    return _parsear_arbol(texto, _union_cruda, _concat_cruda, _estrella_cruda)


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
