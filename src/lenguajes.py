"""Operaciones básicas sobre cadenas y lenguajes (núcleo de la práctica).

Son funciones puras: no dependen de Flet y no leen ni escriben archivos, por eso
se pueden probar de forma automática con pytest.

Convención: la cadena vacía es "" en Python y se escribe λ en pantalla y en los
archivos, como en el curso.
"""

from itertools import product

LAMBDA = "λ"               # así se escribe la cadena vacía
LIMITE_CADENAS = 200_000   # máximo de cadenas que se aceptan generar (Σ* o Σ⁺)
LONGITUD_MAXIMA = 1_000    # máximo de longitud, para cadenas y para Σ* / Σ⁺


class LimiteExcedido(ValueError):
    """La petición pide más de lo que el programa acepta calcular."""


def formatear_cadena(cadena):
    """Devuelve λ para la cadena vacía y la propia cadena en los demás casos."""
    return cadena if cadena else LAMBDA


# ---------------------------------------------------------------------------
# Operación 1: prefijos, sufijos y subcadenas
# ---------------------------------------------------------------------------

def _validar_cadena(w):
    if not isinstance(w, str):
        raise ValueError("La cadena debe ser texto.")
    if LAMBDA in w:
        raise ValueError(f"La cadena no puede contener «{LAMBDA}»: se reserva para la cadena vacía.")
    if len(w) > LONGITUD_MAXIMA:
        raise LimiteExcedido(
            f"La cadena tiene {len(w):,} símbolos y el máximo permitido es {LONGITUD_MAXIMA:,}.")


def prefijos(w):
    """Prefijos de w, de menor a mayor longitud. Incluye λ y a la propia w."""
    _validar_cadena(w)
    return [w[:i] for i in range(len(w) + 1)]


def sufijos(w):
    """Sufijos de w, de menor a mayor longitud. Incluye λ y a la propia w."""
    _validar_cadena(w)
    n = len(w)
    return [w[n - i:] for i in range(n + 1)]


def subcadenas(w):
    """Subcadenas distintas de w (incluye λ), por longitud y luego en orden alfabético."""
    _validar_cadena(w)
    n = len(w)
    distintas = {w[i:j] for i in range(n + 1) for j in range(i, n + 1)}
    return sorted(distintas, key=lambda s: (len(s), s))


def cantidad_prefijos(n):
    """Prefijos (y también sufijos) de una cadena de longitud n: n + 1."""
    return n + 1


def cantidad_maxima_subcadenas(n):
    """Máximo de subcadenas distintas de una cadena de longitud n, contando λ."""
    return n * (n + 1) // 2 + 1


# ---------------------------------------------------------------------------
# Operación 2: cerradura de Kleene (Σ*) y cerradura positiva (Σ⁺)
# ---------------------------------------------------------------------------

def parsear_alfabeto(texto):
    """Convierte el texto escrito por el usuario en una lista de símbolos.

    Se ignoran comas y espacios, y cada carácter restante es un símbolo:
    "a, b", "a b" y "ab" dan ["a", "b"]. Se descartan los repetidos.
    """
    simbolos = []
    for caracter in texto:
        if caracter == "," or caracter.isspace() or caracter in simbolos:
            continue
        simbolos.append(caracter)
    return _validar_alfabeto(simbolos)


def _validar_alfabeto(alfabeto):
    simbolos = list(dict.fromkeys(alfabeto))   # sin repetidos y en el mismo orden
    if not simbolos:
        raise ValueError("El alfabeto debe tener al menos un símbolo.")
    for simbolo in simbolos:
        if not isinstance(simbolo, str) or len(simbolo) != 1:
            raise ValueError(f"Cada símbolo debe ser un solo carácter: {simbolo!r}.")
        if simbolo == LAMBDA:
            raise ValueError(f"«{LAMBDA}» no puede ser símbolo: se reserva para la cadena vacía.")
    return simbolos


def _validar_longitud(n):
    if isinstance(n, bool) or not isinstance(n, int):
        raise ValueError("La longitud máxima debe ser un número entero.")
    if n < 0:
        raise ValueError("La longitud máxima no puede ser negativa.")
    if n > LONGITUD_MAXIMA:
        raise LimiteExcedido(f"La longitud máxima permitida es {LONGITUD_MAXIMA:,}.")


def cantidad_cadenas(tam_alfabeto, n, incluir_vacia=True):
    """Cadenas de Σ* (o de Σ⁺ si incluir_vacia es False) de longitud hasta n.

    Hay |Σ|^k cadenas de longitud k, así que el total es |Σ|⁰ + |Σ|¹ + ... + |Σ|ⁿ.
    """
    if tam_alfabeto == 1:
        total = n + 1
    else:
        total = (tam_alfabeto ** (n + 1) - 1) // (tam_alfabeto - 1)
    return total if incluir_vacia else total - 1


def _describir(cantidad):
    return f"{cantidad:,}" if cantidad < 10 ** 12 else "más de un billón de"


def _cerradura(alfabeto, n, incluir_vacia):
    simbolos = _validar_alfabeto(alfabeto)
    _validar_longitud(n)
    total = cantidad_cadenas(len(simbolos), n, incluir_vacia)
    if total > LIMITE_CADENAS:       # se rechaza ANTES de generar nada
        nombre = "Σ*" if incluir_vacia else "Σ⁺"
        raise LimiteExcedido(
            f"{nombre} con |Σ| = {len(simbolos)} y longitud máxima {n} tendría "
            f"{_describir(total)} cadenas, y el máximo permitido es {LIMITE_CADENAS:,}. "
            "Reduce la longitud máxima o el alfabeto.")
    desde = 0 if incluir_vacia else 1
    return ["".join(c) for k in range(desde, n + 1) for c in product(simbolos, repeat=k)]


def cerradura_kleene(alfabeto, n):
    """Σ* restringida a las cadenas de longitud hasta n. Incluye λ."""
    return _cerradura(alfabeto, n, incluir_vacia=True)


def cerradura_positiva(alfabeto, n):
    """Σ⁺ restringida a las cadenas de longitud hasta n. No incluye λ."""
    return _cerradura(alfabeto, n, incluir_vacia=False)


# ---------------------------------------------------------------------------
# Texto para guardar en un archivo
# ---------------------------------------------------------------------------

def texto_operacion1(w):
    """Texto con los prefijos, sufijos y subcadenas de w, listo para guardarlo."""
    lineas = [
        "Operación 1: prefijos, sufijos y subcadenas",
        f"Cadena: {formatear_cadena(w)}",
        f"Longitud: {len(w)}",
    ]
    for titulo, lista in (("Prefijos", prefijos(w)), ("Sufijos", sufijos(w)),
                          ("Subcadenas distintas", subcadenas(w))):
        lineas += ["", f"{titulo} ({len(lista)}):"]
        lineas += [f"  {formatear_cadena(x)}" for x in lista]
    return "\n".join(lineas) + "\n"


def texto_cerradura(alfabeto, n, cadenas, positiva):
    """Texto con las cadenas de Σ* o Σ⁺ ya calculadas, listo para guardarlo."""
    simbolos = _validar_alfabeto(alfabeto)
    nombre = "Σ⁺ (cerradura positiva)" if positiva else "Σ* (cerradura de Kleene)"
    lineas = [
        f"Operación 2: {nombre}",
        f"Alfabeto: {{{', '.join(simbolos)}}}",
        f"Longitud máxima: {n}",
        f"Cantidad de cadenas: {len(cadenas)}",
        "",
    ]
    lineas += [formatear_cadena(c) for c in cadenas]
    return "\n".join(lineas) + "\n"
