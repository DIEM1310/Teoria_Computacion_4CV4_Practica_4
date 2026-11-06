"""Validadores de la Práctica 4 (Ejercicio 4): expresiones regulares para datos de uso común,
escritas en la notación del curso y convertidas a autómata con el teorema de Kleene
(expresiones.desde_expresion, quitar_lambda, a_afd y minimizar, estas tres de la Práctica 3).

Cada validador se compara con re.fullmatch sobre la misma expresión, traducida automáticamente a
la sintaxis de `re` con expresiones.a_python: así la expresión del curso y la de Python nunca
pueden quedar desincronizadas, porque las dos salen del mismo árbol.

No depende de Flet.
"""

import random
import re
from dataclasses import dataclass

import expresiones as X
from automata import Automata

DIGITO = "0123456789"
MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"


def _clase(caracteres):
    """Unión de un símbolo por cada carácter: una clase como abreviatura (D = 0+1+...+9)."""
    return X.union(*[X.simbolo(c) for c in caracteres])


D = _clase(DIGITO)
DNZ = _clase(DIGITO[1:])
L = _clase(MINUSCULAS)
LD = X.union(L, D)


@dataclass(frozen=True)
class Validador:
    """Un validador: su expresión (ya como árbol), el alfabeto sobre el que está definida, el
    texto abreviado para mostrarlo en la notación del curso y la justificación por escrito de qué
    casos quedan fuera (Ejercicio 4)."""
    clave: str
    titulo: str
    alfabeto: tuple
    notacion_abreviada: str
    leyenda: str
    expresion: "X.ER"
    justificacion: str

    @property
    def notacion_completa(self):
        """La expresión tal cual, sin abreviaturas (puede ser larga)."""
        return str(self.expresion)

    @property
    def python_re(self):
        """La misma expresión en la sintaxis del módulo re, para pytest y para mostrarla."""
        return X.a_python(self.expresion)


# ---------------------------------------------------------------------------
# Fecha en distintos formatos: DD/MM/AAAA y AAAA-MM-DD
# ---------------------------------------------------------------------------

_MES = X.union(X.concat(X.simbolo("0"), DNZ), X.concat(X.simbolo("1"), _clase("012")))
_DIA = X.union(X.concat(X.simbolo("0"), DNZ), X.concat(_clase("12"), D), X.concat(X.simbolo("3"), _clase("01")))
_ANIO = X.concat(D, D, D, D)
_FECHA_ER = X.union(
    X.concat(_DIA, X.simbolo("/"), _MES, X.simbolo("/"), _ANIO),
    X.concat(_ANIO, X.simbolo("-"), _MES, X.simbolo("-"), _DIA),
)

FECHA = Validador(
    clave="fecha",
    titulo="Fecha (DD/MM/AAAA o AAAA-MM-DD)",
    alfabeto=tuple(DIGITO + "/-"),
    notacion_abreviada="Dia/Mes/Anio + Anio-Mes-Dia",
    leyenda=("D = 0+1+...+9 (un dígito). Dnz = 1+2+...+9 (sin el 0). "
             "Mes = (0 Dnz) + (1 (0+1+2))  — 01 a 12. "
             "Dia = (0 Dnz) + ((1+2) D) + (3 (0+1))  — 01 a 31. "
             "Anio = D D D D  — cuatro dígitos, sin validar el valor."),
    expresion=_FECHA_ER,
    justificacion=(
        "No comprueba que el mes tenga esa cantidad de días (acepta 31/02/2027 y 30/02/2024, que no "
        "existen) ni los años bisiestos para el 29 de febrero, ni limita el año a un rango razonable "
        "(acepta 00/01/0000). Quedan fuera los demás separadores (punto, espacio), el mes en letras "
        "(5 de enero de 2027) y el año con dos dígitos. Validar los días de cada mes por separado sí "
        "es regular, pero exige un caso por mes (doce ramas más); se dejó fuera para que la expresión "
        "quedara legible."
    ),
)


# ---------------------------------------------------------------------------
# Teléfono en formato nacional (10 dígitos, seguidos o separados con guion)
# ---------------------------------------------------------------------------
# El analizador de la notación del curso quita los espacios antes de leer la expresión
# (son solo separadores visuales, como en "a + b"), así que el espacio no puede ser un
# símbolo del alfabeto; se usa el guion como separador en su lugar.

_TELEFONO_ER = X.union(
    X.concat(*(D for _ in range(10))),
    X.concat(D, D, X.simbolo("-"), D, D, D, D, X.simbolo("-"), D, D, D, D),
)

TELEFONO = Validador(
    clave="telefono",
    titulo="Teléfono nacional (10 dígitos, seguidos o con guiones 2-4-4)",
    alfabeto=tuple(DIGITO + "-"),
    notacion_abreviada="D¹⁰ + (D D guion D⁴ guion D⁴)",
    leyenda="D = 0+1+...+9. Dⁿ abrevia D concatenado n veces (el curso no tiene notación de repetición).",
    expresion=_TELEFONO_ER,
    justificacion=(
        "No comprueba que el código de dos dígitos sea una clave lada real ni rechaza los números que "
        "empiezan en 00. No admite espacios (55 1234 5678) ni paréntesis ni el prefijo +52; el espacio "
        "se descartó porque el analizador de la notación del curso lo quita antes de leer la expresión "
        "(no puede ser un símbolo), y los demás se dejaron fuera para que el alfabeto se mantuviera "
        "pequeño ({0..9, guion})."
    ),
)


# ---------------------------------------------------------------------------
# Contraseña (criterio propio): 8 caracteres, empieza en letra y termina en dígito
# ---------------------------------------------------------------------------

_CONTRASENA_ER = X.concat(L, LD, LD, LD, LD, LD, LD, D)

CONTRASENA = Validador(
    clave="contrasena",
    titulo="Contraseña (8 caracteres, empieza en letra y termina en dígito)",
    alfabeto=tuple(MINUSCULAS + DIGITO),
    notacion_abreviada="L (L+D)⁶ D",
    leyenda="L = a+b+...+z (minúsculas). D = 0+1+...+9. Longitud exactamente 8.",
    expresion=_CONTRASENA_ER,
    justificacion=(
        "Es un criterio propio, no un estándar: longitud fija de 8 (no un rango), solo minúsculas y "
        "dígitos (sin mayúsculas ni símbolos como # o _), y exige que el primer carácter sea una "
        "letra y el último un dígito, pero no exige más de un dígito ni prohíbe que los seis "
        "caracteres intermedios sean todos dígitos. Se simplificó así para que el alfabeto (36 "
        "símbolos) y la expresión quedaran manejables; una política con mayúsculas, símbolos y "
        "longitud variable también es regular, pero el autómata resultante sería mucho más grande."
    ),
)


VALIDADORES = (FECHA, TELEFONO, CONTRASENA)
POR_CLAVE = {v.clave: v for v in VALIDADORES}


# ---------------------------------------------------------------------------
# Autómata de cada validador (Ejercicio 2 aplicado al Ejercicio 4)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EtapasValidador:
    """Las piezas del Ejercicio 2 aplicadas a un validador, para mostrar cuántos estados tiene el
    AFD antes y después de minimizar."""
    afn_lambda: Automata
    pasos_construccion: tuple
    afn: Automata
    afd: Automata
    minimo: Automata


def construir_automata(v):
    """Autómata del validador `v`, por las cuatro etapas del Ejercicio 2: Thompson (Parte I del
    teorema de Kleene) y, de la Práctica 3, quitar λ, subconjuntos y minimización."""
    afn_lambda, pasos = X.desde_expresion(v.expresion, v.alfabeto)
    afn = afn_lambda.quitar_lambda()
    afd = afn.a_afd(completo=True).afd
    minimo = afd.minimizar()
    return EtapasValidador(afn_lambda, pasos, afn, afd, minimo)


# ---------------------------------------------------------------------------
# Generación de cadenas de prueba (congruencia con re.fullmatch)
# ---------------------------------------------------------------------------

def _generar(e, azar, repeticiones_maximas=3):
    """Una cadena al azar del lenguaje de `e`: en cada unión se elige una parte al azar, en cada
    estrella se repite entre 0 y `repeticiones_maximas` veces (también al azar) y en cada
    concatenación se generan todas las partes y se concatenan."""
    if e.tipo == "vacio":
        return None
    if e.tipo == "lambda":
        return ""
    if e.tipo == "simbolo":
        return e.valor
    if e.tipo == "union":
        orden = list(e.valor)
        azar.shuffle(orden)
        for parte in orden:
            palabra = _generar(parte, azar, repeticiones_maximas)
            if palabra is not None:
                return palabra
        return None
    if e.tipo == "concat":
        partes = []
        for p in e.valor:
            palabra = _generar(p, azar, repeticiones_maximas)
            if palabra is None:
                return None
            partes.append(palabra)
        return "".join(partes)
    n = azar.randint(0, repeticiones_maximas)                   # e.tipo == "estrella"
    partes = []
    for _ in range(n):
        palabra = _generar(e.valor, azar, repeticiones_maximas)
        if palabra is None:
            return ""
        partes.append(palabra)
    return "".join(partes)


def _corromper(palabra, alfabeto, azar):
    """Cambia, quita, inserta o repite un carácter al azar, o trunca la cadena; produce, casi
    siempre, una cadena que ya no pertenece al lenguaje."""
    letras = list(palabra)
    acciones = ["insertar"] + (["quitar", "cambiar", "truncar", "repetir"] if letras else [])
    accion = azar.choice(acciones)
    if accion == "quitar":
        del letras[azar.randrange(len(letras))]
    elif accion == "insertar":
        letras.insert(azar.randint(0, len(letras)), azar.choice(alfabeto))
    elif accion == "cambiar":
        i = azar.randrange(len(letras))
        otros = [s for s in alfabeto if s != letras[i]] or list(alfabeto)
        letras[i] = azar.choice(otros)
    elif accion == "truncar":
        letras = letras[:azar.randint(0, len(letras) - 1)]
    elif accion == "repetir":
        i = azar.randrange(len(letras))
        letras.insert(i, letras[i])
    return "".join(letras)


def generar_casos(v, cantidad=600, semilla="practica4"):
    """Al menos `cantidad` cadenas distintas para la prueba de congruencia del Ejercicio 4: la
    mitad recorriendo el árbol de la expresión al azar (_generar) y la otra mitad corrompiendo una
    de esas cadenas válidas (_corromper) o tomando una cadena por completo al azar sobre el
    alfabeto, de longitud entre 0 y 16. Siempre las mismas cadenas para la misma semilla."""
    azar = random.Random(f"{semilla}|{v.clave}")
    palabras = set()
    intentos = 0
    while len(palabras) < max(1, cantidad // 2) and intentos < cantidad * 30:
        intentos += 1
        palabra = _generar(v.expresion, azar)
        if palabra is not None:
            palabras.add(palabra)
    validas = list(palabras)
    intentos = 0
    while len(palabras) < cantidad and intentos < cantidad * 30:
        intentos += 1
        if validas and azar.random() < 0.6:
            candidata = _corromper(azar.choice(validas), v.alfabeto, azar)
        else:
            n = azar.randint(0, 16)
            candidata = "".join(azar.choice(v.alfabeto) for _ in range(n))
        palabras.add(candidata)
    return sorted(palabras, key=lambda w: (len(w), w))


def coincide_con_re(v, palabra):
    """True si `palabra` pertenece al lenguaje de `v` según re.fullmatch sobre la traducción."""
    return re.fullmatch(v.python_re, palabra) is not None
