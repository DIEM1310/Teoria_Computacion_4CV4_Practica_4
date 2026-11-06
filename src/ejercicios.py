"""Los autómatas de la Lista 3 (Tarea 3): los que da el enunciado en tablas y figuras y los AFN que hay que diseñar.

No depende de Flet. Cada autómata es una `Entrega`: carpeta y nombre del archivo en automatas/, cómo
construirlo y, cuando el enunciado define el lenguaje con palabras, un predicado que lo describe de forma
independiente. Con eso se generan los archivos (herramientas/generar_lista3.py) y las pruebas comprueban
que cualquier archivo entregado, también el que se dibuje a mano en JFLAP, reconoce el mismo lenguaje.
"""

import re
from dataclasses import dataclass, field

import construcciones as C
from automata import Automata

S1, S2, S3 = "012", "abc01", "ab"


@dataclass(frozen=True)
class Entrega:
    carpeta: str                 # subcarpeta de automatas/
    nombre: str                  # nombre del archivo, sin extensión
    ejercicio: str               # número o números del ejercicio de la Lista 3
    descripcion: str
    fabrica: object              # función sin argumentos que devuelve el Automata
    pertenece: object = None     # predicado independiente del lenguaje, si el enunciado lo define con palabras
    alfabeto: str = ""           # alfabeto con el que se prueba el predicado


def desde_tabla(alfabeto, filas, inicial=None, finales=(), nombre=""):
    """Autómata a partir de {estado: {símbolo: 'B,C' o ''}}. Los estados salen en el orden de la tabla."""
    estados = list(filas)
    a = Automata(alfabeto, estados, inicial or estados[0], finales, nombre=nombre)
    for q, fila in filas.items():
        for simbolo, destinos in fila.items():
            for destino in [d for d in destinos.replace(" ", "").split(",") if d]:
                a.agregar_transicion(q, simbolo, destino)
    return a


def _tabla(alfabeto, renglones, finales):
    """renglones: {estado: 'B C ...'} con un destino por columna; '-' es ninguno; 'B,C' es un conjunto."""
    filas = {q: {s: ("" if d == "-" else d) for s, d in zip(alfabeto, texto.split())} for q, texto in renglones.items()}
    return desde_tabla(alfabeto, filas, finales=finales)


# ---------------------------------------------------------------------------
# 151 a 157: simplificar AFD
# ---------------------------------------------------------------------------

def t151():
    return _tabla("01", {"A": "C E", "B": "F E", "C": "A G", "D": "C E", "E": "I B", "F": "D H",
                         "G": "F I", "H": "C J", "I": "J E", "J": "I E"}, "CEF")


def t152():
    return _tabla("012", {"A": "C E B", "B": "D E B", "C": "A D F", "D": "F B C", "E": "F B A", "F": "D B C"}, "DEF")


def t153():
    return _tabla("01", {"A": "B C", "B": "D E", "C": "F G", "D": "D E", "E": "F G", "F": "E D", "G": "F G"}, "DFG")


def t154():
    return _tabla("01", {"A": "D K", "B": "H K", "C": "I E", "D": "C G", "E": "K I", "F": "B E", "G": "C I",
                         "H": "C B", "I": "G K", "J": "F B", "K": "C F"}, "EGHJ")


def t155():
    return _tabla("01", {"A": "B C", "B": "D E", "C": "K G", "D": "H E", "E": "F D", "F": "J G", "G": "E G",
                         "H": "B K", "I": "C A", "J": "D G", "K": "F D", "L": "C J"}, "F")


def f156():
    return _tabla("01", {"A": "B C", "B": "C E", "C": "D C", "D": "C E", "E": "B E"}, "E")


def f157():
    return _tabla("01", {"A": "B F", "B": "C E", "C": "D E", "D": "B E", "E": "F D", "F": "F B"}, "F")


# ---------------------------------------------------------------------------
# 158 a 161: figuras de AFN que en realidad son deterministas (parciales)
# ---------------------------------------------------------------------------

def f158():
    return _tabla("01", {"q1": "q2 -", "q2": "- q3", "q3": "- -"}, ["q3"])


def f159():
    return _tabla("01", {"q1": "q2 q1", "q2": "- q3", "q3": "- -"}, ["q3"])


def f160():
    return _tabla("01", {"q1": "q2 -", "q2": "- q3", "q3": "q3 q3"}, ["q3"])


def f161():
    a = _tabla("01", {"q1": "q2 -", "q2": "- q3", "q3": "q1 -"}, ["q1", "q3"])
    return a


# ---------------------------------------------------------------------------
# 162 a 188: AFN de los ejercicios obligatorios de la Lista 2 (solo donde el diagrama es más simple)
# ---------------------------------------------------------------------------

def n099():
    return C.termina_en("001001", S1)


def n102():
    return C.contiene("abbbab", S3)


def n103():
    return C.contiene("aabbba", S3)


def n106():
    return C.contiene("1101001", S1)


def n118():
    """a x a b y a: se adivina dónde empieza `ab`, y dónde empieza la última `a`."""
    return desde_tabla("ab", {"q0": {"a": "q1"}, "q1": {"a": "q1,q2", "b": "q1"}, "q2": {"b": "q3"},
                              "q3": {"a": "q3,q4", "b": "q3"}, "q4": {}}, "q0", ["q4"])


def n120():
    """Primer y último símbolo distintos: se adivina cuál es el último."""
    filas = {"q0": {"0": "p0", "1": "p1", "2": "p2"}, "p0": {"0": "p0", "1": "p0,f", "2": "p0,f"},
             "p1": {"0": "p1,f", "1": "p1", "2": "p1,f"}, "p2": {"0": "p2,f", "1": "p2,f", "2": "p2"}, "f": {}}
    return desde_tabla(S1, filas, "q0", ["f"])


def n123():
    """wxw con |w| = 2: se adivina dónde empieza la segunda w."""
    filas = {"q0": {"a": "A_a", "b": "A_b"}, "F": {}}
    for s in "ab":
        filas[f"A_{s}"] = {t: f"B_{s}{t}" for t in "ab"}
    for s in "ab":
        for t in "ab":
            filas[f"B_{s}{t}"] = {"a": f"B_{s}{t}" + (f",C_{s}{t}" if s == "a" else ""),
                                  "b": f"B_{s}{t}" + (f",C_{s}{t}" if s == "b" else "")}
            filas[f"C_{s}{t}"] = {t: "F"}
    return C.renombrar_secuencial(desde_tabla("ab", filas, "q0", ["F"]))


# ---------------------------------------------------------------------------
# 189 y 190: AFN con dos patrones
# ---------------------------------------------------------------------------

def n189():
    """Contiene 00101 o 00110: los dos patrones comparten el prefijo 001."""
    filas = {"q0": {"0": "q0,q1", "1": "q0"}, "q1": {"0": "q2"}, "q2": {"1": "q3"},
             "q3": {"0": "q4", "1": "q6"}, "q4": {"1": "q5"}, "q5": {"0": "q5", "1": "q5"},
             "q6": {"0": "q7"}, "q7": {"0": "q7", "1": "q7"}}
    return desde_tabla("01", filas, "q0", ["q5", "q7"])


def n190():
    """Contiene 11010 y 10100. Se adivina cuál aparece primero; 10100 puede empezar dentro de 11010
    (comparten `10` o `1010`), y eso se resuelve con dos transiciones hacia la cadena de 10100."""
    filas = {"s": {"0": "s", "1": "s,p1,r1"}}
    # rama 1: 11010 y después 10100 (con los traslapes posibles)
    filas.update({"p1": {"1": "p2"}, "p2": {"0": "p3"}, "p3": {"1": "p4"}, "p4": {"0": "p5"},
                  "p5": {"0": "p5", "1": "p5,u1"},
                  "u1": {"0": "u2"}, "u2": {"1": "u3"}, "u3": {"0": "u4"}, "u4": {"0": "uf"}, "uf": {"0": "uf", "1": "uf"}})
    filas["p1"]["1"] = "p2,u1"          # 10100 empieza en el segundo símbolo de 11010 (traslape de 4)
    filas["p3"]["1"] = "p4,u1"          # 10100 empieza en el cuarto símbolo de 11010 (traslape de 2)
    # rama 2: 10100 y después 11010
    filas.update({"r1": {"0": "r2"}, "r2": {"1": "r3"}, "r3": {"0": "r4"}, "r4": {"0": "r5"},
                  "r5": {"0": "r5", "1": "r5,v1"},
                  "v1": {"1": "v2"}, "v2": {"0": "v3"}, "v3": {"1": "v4"}, "v4": {"0": "vf"}, "vf": {"0": "vf", "1": "vf"}})
    return C.renombrar_secuencial(desde_tabla("01", filas, "s", ["uf", "vf"]))


# ---------------------------------------------------------------------------
# 192 a 195: AFN dados por tabla, con su AFD equivalente
# ---------------------------------------------------------------------------

def t192():
    return _tabla("01", {"A": "B B,C", "B": "A,B -", "C": "A,C -"}, "C")


def t193():
    return _tabla("01", {"A": "- B,C", "B": "A,D B,C,D", "C": "C A,C", "D": "C D"}, "D")


def t194():
    return _tabla("012", {"A": "A,B A,C A", "B": "- - -", "C": "A,B A,B,C,D -", "D": "B A -"}, "CD")


def t195():
    return _tabla("01", {"A": "A,B A", "B": "A C", "C": "A D", "D": "D E", "E": "E C,D"}, "CE")


# ---------------------------------------------------------------------------
# 196 a 200: AFND-λ dados por tabla (columnas λ, 0, 1)
# ---------------------------------------------------------------------------

def _tabla_lambda(alfabeto, renglones, finales):
    """renglones: {estado: 'λ 0 1'} con un conjunto por columna ('-' es ninguno)."""
    columnas = [""] + list(alfabeto)
    filas = {q: {c: ("" if d == "-" else d) for c, d in zip(columnas, texto.split())} for q, texto in renglones.items()}
    return desde_tabla(alfabeto, filas, finales=finales)


def l196():
    return _tabla_lambda("01", {"A": "B A -", "B": "- A,B C", "C": "- - -"}, "C")


def l197():
    return _tabla_lambda("01", {"A": "C B,D -", "B": "D A,C D", "C": "B - A,C", "D": "- - D"}, "D")


def l198():
    return _tabla_lambda("01", {"A": "C B -", "B": "- C -", "C": "B - C,D", "D": "- - B"}, "D")


def l199():
    return _tabla_lambda("01", {"A": "B,C E -", "B": "- E B", "C": "E - A,C", "D": "- - D", "E": "- - D"}, "DE")


def l200():
    return _tabla_lambda("01", {"A": "B F A,C,F", "B": "- C,D B,E", "C": "E - A,C", "D": "E,F A,C B,E",
                                "E": "- - D", "F": "E B,E -"}, "DE")


# ---------------------------------------------------------------------------
# 254 a 258: AFD dados por tabla, para obtener su expresión regular
# ---------------------------------------------------------------------------

def t254():
    return _tabla("01", {"A": "A B", "B": "A B"}, "B")


def t255():
    return _tabla("01", {"A": "B B", "B": "A B"}, "A")


def t256():
    return _tabla("012", {"A": "B A A", "B": "B B A"}, "B")


def t257():
    return _tabla("01", {"A": "B C", "B": "C B", "C": "A A"}, "BC")


def t258():
    return _tabla("01", {"A": "C C", "B": "A C", "C": "B A"}, "C")


# ---------------------------------------------------------------------------
# 260 a 263: AFN a AFD
# ---------------------------------------------------------------------------

def t260():
    return _tabla("01", {"A": "- B,C", "B": "A,B,D C,D", "C": "A,C A,E", "D": "- D,E", "E": "A,E -"}, "D")


def f261():
    """Figura: q0 con bucles 0 y 1; q0 –0→ q1 –0→ q2 (aceptación); q0 –1→ q3 –1→ q4."""
    return desde_tabla("01", {"q0": {"0": "q0,q1", "1": "q0,q3"}, "q1": {"0": "q2"}, "q2": {},
                              "q3": {"1": "q4"}, "q4": {}}, "q0", ["q2"])


def n262():
    """{ab, ba}: dos ramas desde q0 que se juntan en el estado final."""
    return desde_tabla("ab", {"q0": {"a": "q1", "b": "q2"}, "q1": {"b": "q3"}, "q2": {"a": "q3"}, "q3": {}}, "q0", ["q3"])


def f263():
    return desde_tabla("01", {"q0": {"0": "q0,q1", "1": "q0"}, "q1": {"1": "q2"}, "q2": {}}, "q0", ["q2"])


# ---------------------------------------------------------------------------
# Lenguajes definidos con palabras, para probar los diseños de forma independiente
# ---------------------------------------------------------------------------

def _ventana(w, patron):
    return patron in w


PERTENECE = {
    "158": lambda w: w == "01",
    "159": lambda w: re.fullmatch("1*01", w) is not None,
    "160": lambda w: w.startswith("01"),
    "161": lambda w: re.fullmatch("(010)*(01)?", w) is not None,
    "099": lambda w: w.endswith("001001"),
    "102": lambda w: "abbbab" in w,
    "103": lambda w: "aabbba" in w,
    "106": lambda w: "1101001" in w,
    "118": lambda w: re.fullmatch("a[ab]*ab[ab]*a", w) is not None,
    "120": lambda w: len(w) >= 2 and w[0] != w[-1],
    "123": lambda w: len(w) >= 4 and w[:2] == w[-2:],
    "189": lambda w: "00101" in w or "00110" in w,
    "190": lambda w: "11010" in w and "10100" in w,
    "261": lambda w: w.endswith("00"),
    "262": lambda w: w in ("ab", "ba"),
    "263": lambda w: w.endswith("01"),
    "254": lambda w: w.endswith("1"),
}


def _e(carpeta, nombre, ejercicio, descripcion, fabrica, clave=None, alfabeto=""):
    return Entrega(carpeta, nombre, ejercicio, descripcion, fabrica, PERTENECE.get(clave), alfabeto)


ENTREGAS = [
    # --- simplificación (151 a 157) y descripción de AFN deterministas (158 a 161)
    _e("lista3-afd", "Ej_151_original", "151", "Tabla del enunciado (10 estados)", t151),
    _e("lista3-afd", "Ej_152_original", "152", "Tabla del enunciado (6 estados, Σ = {0,1,2})", t152),
    _e("lista3-afd", "Ej_153_original", "153", "Tabla del enunciado (7 estados)", t153),
    _e("lista3-afd", "Ej_154_original", "154", "Tabla del enunciado (11 estados)", t154),
    _e("lista3-afd", "Ej_155_original", "155", "Tabla del enunciado (12 estados)", t155),
    _e("lista3-afd", "Ej_156_original", "156", "Figura del enunciado (5 estados)", f156),
    _e("lista3-afd", "Ej_157_original", "157", "Figura del enunciado (6 estados)", f157),
    _e("lista3-afd", "Ej_158_figura", "158", "Figura: q1 –0→ q2 –1→ q3", f158, "158", "01"),
    _e("lista3-afd", "Ej_159_figura", "159", "Figura: lazo 1 en q1, luego 0 y 1", f159, "159", "01"),
    _e("lista3-afd", "Ej_160_figura", "160", "Figura: 01 y lazo 0,1 en q3", f160, "160", "01"),
    _e("lista3-afd", "Ej_161_figura", "161", "Figura: ciclo 0,1,0 con q1 y q3 de aceptación", f161, "161", "01"),
    # --- AFN de los ejercicios de la Lista 2 (162 a 188), solo donde el diagrama es más simple que el del AFD
    _e("lista3-afnd", "Ej_099_afn_termina_en_001001", "99 (Lista 2)", "AFN: se adivina dónde empieza el sufijo", n099, "099", S1),
    _e("lista3-afnd", "Ej_102_afn_contiene_abbbab", "102 (Lista 2)", "AFN: se adivina dónde empieza el patrón", n102, "102", S3),
    _e("lista3-afnd", "Ej_103_afn_contiene_aabbba", "103 (Lista 2)", "AFN: se adivina dónde empieza el patrón", n103, "103", S3),
    _e("lista3-afnd", "Ej_106_afn_contiene_1101001", "106 (Lista 2)", "AFN: se adivina dónde empieza el patrón", n106, "106", S1),
    _e("lista3-afnd", "Ej_118_afn_forma_axabya", "118 (Lista 2)", "AFN de 5 estados", n118, "118", S3),
    _e("lista3-afnd", "Ej_120_afn_primer_y_ultimo_distintos", "120 (Lista 2)", "AFN: se adivina el último símbolo", n120, "120", S1),
    _e("lista3-afnd", "Ej_123_afn_forma_wxw", "123 (Lista 2)", "AFN: se adivina dónde empieza la segunda w", n123, "123", S3),
    # --- 189 y 190
    _e("lista3-afnd", "Ej_189_afn_00101_o_00110", "189", "Contiene 00101 o 00110", n189, "189", "01"),
    _e("lista3-afnd", "Ej_190_afn_11010_y_10100", "190", "Contiene 11010 y 10100", n190, "190", "01"),
    # --- 192 a 195, 260 a 263: AFN dados
    _e("lista3-afnd", "Ej_192_tabla", "192", "Tabla del enunciado (3 estados)", t192),
    _e("lista3-afnd", "Ej_193_tabla", "193", "Tabla del enunciado (4 estados)", t193),
    _e("lista3-afnd", "Ej_194_tabla", "194", "Tabla del enunciado (4 estados, Σ = {0,1,2})", t194),
    _e("lista3-afnd", "Ej_195_tabla", "195", "Tabla del enunciado (5 estados)", t195),
    _e("lista3-afnd", "Ej_260_tabla", "260", "Tabla del enunciado (5 estados)", t260),
    _e("lista3-afnd", "Ej_261_figura", "261", "Figura del enunciado: acepta lo que termina en 00", f261, "261", "01"),
    _e("lista3-afd", "Ej_262_ab_ba", "262", "AFN que acepta {ab, ba}; resulta determinista (AFD parcial)", n262, "262", "ab"),
    _e("lista3-afnd", "Ej_263_figura", "263", "Figura del enunciado: acepta lo que termina en 01", f263, "263", "01"),
    # --- AFND-λ (196 a 200, opcionales pero necesarios para el apartado 2.3 de la práctica)
    _e("lista3-afnd-lambda", "Ej_196_tabla", "196", "Tabla del enunciado (3 estados)", l196),
    _e("lista3-afnd-lambda", "Ej_197_tabla", "197", "Tabla del enunciado (4 estados)", l197),
    _e("lista3-afnd-lambda", "Ej_198_tabla", "198", "Tabla del enunciado (4 estados)", l198),
    _e("lista3-afnd-lambda", "Ej_199_tabla", "199", "Tabla del enunciado (5 estados)", l199),
    _e("lista3-afnd-lambda", "Ej_200_tabla", "200", "Tabla del enunciado (6 estados)", l200),
    # --- autómatas de los que se pide la expresión regular
    _e("lista3-afd", "Ej_254_tabla", "254", "Tabla del enunciado", t254, "254", "01"),
    _e("lista3-afd", "Ej_255_tabla", "255", "Tabla del enunciado", t255),
    _e("lista3-afd", "Ej_256_tabla", "256", "Tabla del enunciado (Σ = {0,1,2})", t256),
    _e("lista3-afd", "Ej_257_tabla", "257", "Tabla del enunciado", t257),
    _e("lista3-afd", "Ej_258_tabla", "258", "Tabla del enunciado", t258),
]

POR_NOMBRE = {e.nombre: e for e in ENTREGAS}


def _derivar(origen, carpeta, nombre, descripcion, transformar):
    """Entrega que se obtiene aplicando una operación a otra (simplificar o convertir)."""
    def fabrica(origen=origen, transformar=transformar):
        return transformar(POR_NOMBRE[origen].fabrica())
    return Entrega(carpeta, nombre, POR_NOMBRE[origen].ejercicio, descripcion, fabrica, None, "")


# Simplificación de 151 a 157: sin estados inaccesibles (solo si los hay) y AFD mínimo.
for _n in range(151, 158):
    _origen = f"Ej_{_n}_original"
    if POR_NOMBRE[_origen].fabrica().accesibles() != tuple(POR_NOMBRE[_origen].fabrica().estados):
        ENTREGAS.append(_derivar(_origen, "lista3-afd", f"Ej_{_n}_sin_inaccesibles",
                                 "Sin los estados inaccesibles", lambda a: a.quitar_inaccesibles()))
    ENTREGAS.append(_derivar(_origen, "lista3-afd", f"Ej_{_n}_minimo", "AFD mínimo (partición)", lambda a: a.minimizar()))
    POR_NOMBRE = {e.nombre: e for e in ENTREGAS}

# Conversiones: AFN a AFD por subconjuntos; AFND-λ a AFND (sin λ) y de ahí a AFD.
CONVERSIONES_AFN = ["Ej_099_afn_termina_en_001001", "Ej_102_afn_contiene_abbbab", "Ej_103_afn_contiene_aabbba",
                    "Ej_106_afn_contiene_1101001", "Ej_118_afn_forma_axabya", "Ej_120_afn_primer_y_ultimo_distintos",
                    "Ej_123_afn_forma_wxw", "Ej_189_afn_00101_o_00110", "Ej_190_afn_11010_y_10100", "Ej_192_tabla",
                    "Ej_193_tabla", "Ej_194_tabla", "Ej_195_tabla", "Ej_260_tabla", "Ej_261_figura", "Ej_262_ab_ba",
                    "Ej_263_figura"]
CONVERSIONES_LAMBDA = ["Ej_196_tabla", "Ej_197_tabla", "Ej_198_tabla", "Ej_199_tabla", "Ej_200_tabla"]
for _origen in CONVERSIONES_AFN:
    _num = _origen.split("_")[1]
    ENTREGAS.append(_derivar(_origen, "conversiones", f"Ej_{_num}_afd", "AFD equivalente (subconjuntos)",
                             (lambda a: a.a_afd(completo=True).afd) if _num == "262" else (lambda a: a.a_afd().afd)))
for _origen in CONVERSIONES_LAMBDA:
    _num = _origen.split("_")[1]
    ENTREGAS.append(_derivar(_origen, "conversiones", f"Ej_{_num}_afnd", "AFND equivalente, sin transiciones λ",
                             lambda a: a.quitar_lambda()))
    ENTREGAS.append(_derivar(_origen, "conversiones", f"Ej_{_num}_afd", "AFD equivalente (de AFND-λ a AFND y a AFD)",
                             lambda a: a.quitar_lambda().a_afd().afd))
POR_NOMBRE = {e.nombre: e for e in ENTREGAS}
assert len(POR_NOMBRE) == len(ENTREGAS), "nombres de archivo repetidos"


# ---------------------------------------------------------------------------
# Preguntas de los ejercicios 192 a 200
# ---------------------------------------------------------------------------

# ("delta_hat", Z, w) · ("clausura", conjunto) · ("delta", estado, símbolo)
CONSULTAS = {
    "192": [("a", ("delta_hat", "A", "0111")), ("b", ("delta_hat", "BC", "010111"))],
    "193": [("a", ("delta_hat", "A", "01101")), ("b", ("delta_hat", "AB", "1101")), ("c", ("delta_hat", "C", "1101"))],
    "194": [("a", ("delta_hat", "AC", "0121")), ("b", ("delta_hat", "B", "20111")),
            ("c", ("delta_hat", "C", "02112")), ("d", ("delta_hat", "AB", "0121"))],
    "195": [("a", ("delta_hat", "A", "10010")), ("b", ("delta_hat", "AD", "0110")),
            ("c", ("delta_hat", "BE", "0100")), ("d", ("delta_hat", "BCD", "10100"))],
    "196": [("a", ("delta_hat", "A", "110")), ("b", ("clausura", "A")), ("c", ("clausura", "B")),
            ("d", ("clausura", "AB")), ("e", ("delta", "A", "0"))],
    "197": [("a", ("clausura", "A")), ("b", ("clausura", "BD")), ("c", ("clausura", "ABC")),
            ("d", ("delta", "A", "0")), ("e", ("delta_hat", "A", "010"))],
    "198": [("a", ("clausura", "A")), ("b", ("clausura", "CD")), ("c", ("clausura", "ACD")),
            ("e", ("delta_hat", "B", "0111"))],
    "199": [("a", ("clausura", "A")), ("b", ("clausura", "C")), ("c", ("delta_hat", "A", "011"))],
    "200": [("a", ("clausura", "A")), ("b", ("clausura", "CD")), ("c", ("delta_hat", "C", "1011"))],
}


def responder(a, consulta):
    """Resultado de una consulta sobre el autómata, como conjunto de estados."""
    tipo = consulta[0]
    if tipo == "delta_hat":
        return a.delta_hat(set(consulta[1]), consulta[2])
    if tipo == "clausura":
        return a.clausura(set(consulta[1]))
    return a.delta(consulta[1], consulta[2])


# Ejercicios de la Lista 2 cuyo AFN no es más simple que el AFD: se reutiliza el AFD como AFN
# (todo AFD es un AFN). Número del ejercicio -> motivo.
AFD_COMO_AFN = {
    "97": "el AFD ya es un ciclo de 3 estados: no hay nada que adivinar",
    "107": "el AFN (unión de los dos órdenes) tiene 15 estados y el AFD 13",
    "109": "el AFN, que además necesita las cadenas fundidas, tiene 40 estados y el AFD 22",
    "111": "«exactamente tres» obliga a comprobar que no hay una cuarta aparición: es un contador",
    "112": "«exactamente dos» obliga a comprobar que no hay una tercera aparición: es un contador",
    "113": "«exactamente dos» obliga a comprobar que no hay una tercera aparición: es un contador",
    "121": "es una posición módulo 3 con una bandera: no hay elección que adivinar",
    "122": "es una ventana de memoria acotada: no hay elección que adivinar",
}
