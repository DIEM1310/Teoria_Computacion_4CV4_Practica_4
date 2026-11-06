"""Constructores de autómatas para los patrones que aparecen en las listas de ejercicios.

No depende de Flet. Sirven para generar los autómatas de automatas/ de forma
reproducible y para tener, en las pruebas, un segundo camino independiente hacia el
mismo lenguaje (por ejemplo, el AFND de "contiene" frente al AFD obtenido por KMP).
"""

from collections import deque
from itertools import product

from automata import Automata


# ---------------------------------------------------------------------------
# Nombres de estados
# ---------------------------------------------------------------------------

def renombrar_secuencial(a, prefijo="q"):
    """Copia del autómata con los estados llamados q0, q1, ... en el orden en que los
    descubre un recorrido a lo ancho desde el inicial (los inaccesibles van al final)."""
    orden, vistos = [], set()
    cola = deque([a.inicial])
    vistos.add(a.inicial)
    while cola:
        q = cola.popleft()
        orden.append(q)
        for lee in [""] + a.alfabeto:
            for r in a.destinos(q, lee):
                if r not in vistos:
                    vistos.add(r)
                    cola.append(r)
    orden += [q for q in a.estados if q not in vistos]
    nombre = {q: f"{prefijo}{i}" for i, q in enumerate(orden)}
    return Automata(a.alfabeto, [nombre[q] for q in orden], nombre[a.inicial],
                    [nombre[q] for q in orden if a.es_aceptacion(q)],
                    [(nombre[d], lee, nombre[h]) for d, lee, h in a.transiciones()], a.nombre)


def minimo(a):
    """AFD mínimo con los estados llamados q0, q1, ... Si es un AFND, se convierte antes
    (el AFD resultante es completo)."""
    if not a.es_determinista():
        a = a.a_afd(completo=True).afd
    return renombrar_secuencial(a.minimizar())


def desde_funcion(alfabeto, inicial, delta, es_final, nombre=""):
    """AFD que se obtiene explorando, desde `inicial`, la función `delta(estado, símbolo)`.

    Los estados pueden ser cualquier valor hashable (tuplas, por ejemplo); se nombran q0,
    q1, ... en el orden en que se descubren. Solo se crean los estados alcanzables.
    """
    ids, orden, trans = {inicial: 0}, [inicial], []
    cola = deque([inicial])
    while cola:
        e = cola.popleft()
        for s in alfabeto:
            d = delta(e, s)
            if d not in ids:
                ids[d] = len(orden)
                orden.append(d)
                cola.append(d)
            trans.append((f"q{ids[e]}", s, f"q{ids[d]}"))
    return Automata(alfabeto, [f"q{i}" for i in range(len(orden))], "q0",
                    [f"q{i}" for i, e in enumerate(orden) if es_final(e)], trans, nombre)


# ---------------------------------------------------------------------------
# AFND de patrones (la construcción natural: se adivina dónde empieza el patrón)
# ---------------------------------------------------------------------------

def termina_en(patron, alfabeto):
    """AFND de len(patron)+1 estados: cadenas que terminan con el patrón."""
    a = Automata(alfabeto, [f"q{i}" for i in range(len(patron) + 1)], "q0", [f"q{len(patron)}"])
    for s in alfabeto:
        a.agregar_transicion("q0", s, "q0")
    for i, s in enumerate(patron):
        a.agregar_transicion(f"q{i}", s, f"q{i + 1}")
    return a


def contiene(patron, alfabeto):
    """AFND de len(patron)+1 estados: cadenas que contienen el patrón."""
    a = termina_en(patron, alfabeto)
    for s in alfabeto:
        a.agregar_transicion(f"q{len(patron)}", s, f"q{len(patron)}")
    return a


def empieza_con(patron, alfabeto):
    """AFD parcial de len(patron)+1 estados: cadenas que empiezan con el patrón."""
    a = Automata(alfabeto, [f"q{i}" for i in range(len(patron) + 1)], "q0", [f"q{len(patron)}"])
    for i, s in enumerate(patron):
        a.agregar_transicion(f"q{i}", s, f"q{i + 1}")
    for s in alfabeto:
        a.agregar_transicion(f"q{len(patron)}", s, f"q{len(patron)}")
    return a


def union(*automatas):
    """AFND cuyo lenguaje es la unión de los lenguajes (los estados iniciales se funden)."""
    alfabeto = list(dict.fromkeys(s for a in automatas for s in a.alfabeto))
    u = Automata(alfabeto, ["s"], "s")
    for i, a in enumerate(automatas):
        def nuevo(q, i=i, a=a):
            return "s" if q == a.inicial else f"{i}.{q}"
        for q in a.estados:
            if nuevo(q) not in u.estados:
                u.agregar_estado(nuevo(q))
            if a.es_aceptacion(q):
                u.marcar_aceptacion(nuevo(q))
        for d, lee, h in a.transiciones():
            u.agregar_transicion(nuevo(d), lee, nuevo(h))
    return u


def secuencia(primero, segundo, alfabeto):
    """AFND de Σ* p Σ* q Σ*: aparece p y, después, sin traslape, q."""
    a = Automata(alfabeto, ["s"], "s")
    for s in alfabeto:
        a.agregar_transicion("s", s, "s")
    anterior = "s"
    for etiqueta, patron in (("p", primero), ("q", segundo)):
        for i, simbolo in enumerate(patron):
            actual = f"{etiqueta}{i + 1}"
            a.agregar_estado(actual)
            a.agregar_transicion(anterior, simbolo, actual)
            anterior = actual
        for s in alfabeto:
            a.agregar_transicion(anterior, s, anterior)
    a.marcar_aceptacion(anterior)
    return a


# ---------------------------------------------------------------------------
# AFD por KMP y contadores (la construcción natural de un AFD)
# ---------------------------------------------------------------------------

def avance_kmp(patron):
    """Función (j, símbolo) -> j' donde j es la longitud del prefijo más largo del patrón
    que es sufijo de lo leído (como máximo len(patron)). Es la tabla del algoritmo KMP."""
    def siguiente(j, simbolo):
        leido = patron[:j] + simbolo
        for k in range(min(len(leido), len(patron)), -1, -1):
            if leido.endswith(patron[:k]):
                return k
    return siguiente


def afd_contiene_todos(patrones, alfabeto, nombre=""):
    """AFD de las cadenas que contienen cada uno de los patrones (con traslape permitido).

    Es el producto de un buscador de patrón por cada patrón; un buscador que ya encontró
    su patrón se queda ahí. El resultado se reduce a su AFD mínimo.
    """
    pasos = [avance_kmp(p) for p in patrones]

    def delta(estado, s):
        return tuple(j if j == len(p) else paso(j, s) for j, p, paso in zip(estado, patrones, pasos))

    afd = desde_funcion(alfabeto, (0,) * len(patrones), delta,
                        lambda e: all(j == len(p) for j, p in zip(e, patrones)), nombre)
    return minimo(afd)


def afd_termina_en(patron, alfabeto, nombre=""):
    """AFD mínimo de las cadenas que terminan con el patrón."""
    paso = avance_kmp(patron)
    afd = desde_funcion(alfabeto, 0, paso, lambda j: j == len(patron), nombre)
    return minimo(afd)


def afd_contar_apariciones(patron, alfabeto, cantidad, nombre=""):
    """AFD mínimo de las cadenas con exactamente `cantidad` apariciones del patrón (se
    cuentan también las que se traslapan). Con más apariciones se cae en un estado trampa."""
    paso = avance_kmp(patron)

    def delta(estado, s):
        j, c = estado
        if c > cantidad:
            return estado
        j = paso(j, s)
        return (j, c + (j == len(patron)))

    afd = desde_funcion(alfabeto, (0, 0), delta, lambda e: e[1] == cantidad, nombre)
    return minimo(afd)


def cadenas_hasta(alfabeto, longitud_maxima):
    """Todas las cadenas sobre el alfabeto hasta la longitud dada (para verificar)."""
    for n in range(longitud_maxima + 1):
        for t in product(alfabeto, repeat=n):
            yield "".join(t)
