"""Genera los autómatas de la Lista 2 que no vienen de la Práctica 1 (o que había que corregir).

Uso, desde la raíz del repositorio:

    python herramientas/generar_lista2.py

Escribe en automatas/lista2-afd/ el .jff de cada autómata definido aquí y, para todos los
.jff de esa carpeta (también los copiados de la Práctica 1), su .json y su .xml. Los
autómatas se verifican contra la definición de cada lenguaje en tests/test_lista2.py.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import construcciones as C                      # noqa: E402
import formatos as F                            # noqa: E402
from automata import Automata                   # noqa: E402

CARPETA = RAIZ / "automatas" / "lista2-afd"
S1, S2, S3 = "012", "abc01", "ab"


def desde_tabla(alfabeto, inicial, finales, tabla, nombre=""):
    """AFD a partir de {estado: {símbolo: destino}}; los estados salen en el orden de la tabla."""
    a = Automata(alfabeto, list(tabla), inicial, finales, nombre=nombre)
    for q, fila in tabla.items():
        for s, destino in fila.items():
            a.agregar_transicion(q, s, destino)
    return a


# ---------------------------------------------------------------------------
# Cada función devuelve el autómata de un ejercicio
# ---------------------------------------------------------------------------

def ej099():
    return C.afd_termina_en("001001", S1)


def ej103():
    return C.afd_contiene_todos(["aabbba"], S3)


def ej107():
    return C.afd_contiene_todos(["0101", "021"], S1)


def ej109():
    return C.afd_contiene_todos(["abbcb", "cbaabb"], S2)


def ej111():
    return C.afd_contar_apariciones("01002", S1, 3)


def ej118():
    """a x a b y a: AFND de 5 estados convertido y minimizado (6 estados con la trampa)."""
    a = Automata(S3, [f"q{i}" for i in range(5)], "q0", ["q4"],
                 [("q0", "a", "q1"), ("q1", "a", "q1"), ("q1", "b", "q1"), ("q1", "a", "q2"),
                  ("q2", "b", "q3"), ("q3", "a", "q3"), ("q3", "b", "q3"), ("q3", "a", "q4")])
    return C.minimo(a)


def ej121():
    """Longitud 3n con al menos un 0 en cada bloque de 3. Estado = (posición en el bloque, ya hubo 0)."""
    trampa = "X"

    def delta(e, s):
        if e == trampa:
            return trampa
        k, hubo = e
        hubo = hubo or s == "0"
        if k == 2:
            return (0, False) if hubo else trampa
        return (k + 1, hubo)

    return C.desde_funcion(S1, (0, False), delta, lambda e: e == (0, False))


def ej124():
    """Mecanismo de canicas y palancas. Palanca: 0 = izquierda, 1 = derecha.

    Entrada 0: la palanca 1 manda la canica a A (izquierda) o al centro (derecha).
    Entrada 1: la palanca 2 manda la canica al centro (izquierda) o a R (derecha).
    En el centro, la palanca 3 la manda a A (izquierda) o a R (derecha).
    Cada palanca que toca la canica cambia de posición. Estado = (palancas, última salida);
    el AFD se minimiza, porque dos de esos 13 estados se comportan igual (quedan 12).
    """
    def delta(e, entrada):
        p1, p2, p3, _ = e
        if entrada == "0":
            if p1 == 0:
                return (1, p2, p3, "A")
            salida = "A" if p3 == 0 else "R"
            return (0, p2, 1 - p3, salida)
        if p2 == 0:
            salida = "A" if p3 == 0 else "R"
            return (p1, 1, 1 - p3, salida)
        return (p1, 0, p3, "R")

    return C.minimo(C.desde_funcion("01", (0, 0, 0, None), delta, lambda e: e[3] == "A"))


def ej128():
    """L2 = palabras de L sin el último símbolo, con L el autómata del diagrama.

    Se conserva el autómata del diagrama y cambian los estados de aceptación por los que
    tienen una flecha hacia F: D (con 0) y E (con 1).
    """
    return desde_tabla("01", "A", ["D", "E"], {
        "A": {"0": "B", "1": "C"}, "B": {"0": "C", "1": "D"}, "C": {"0": "D", "1": "E"},
        "D": {"0": "F", "1": "E"}, "E": {"0": "E", "1": "F"}, "F": {"0": "D", "1": "D"}})


def ej131():
    return desde_tabla("01", "q1", ["q2"], {"q1": {"0": "q1", "1": "q2"}, "q2": {"0": "q1", "1": "q2"}})


def ej133():
    return desde_tabla("ab", "q0", ["q0"], {
        "q0": {"a": "q2", "b": "q1"}, "q1": {"a": "q3", "b": "q0"},
        "q2": {"a": "q0", "b": "q3"}, "q3": {"a": "q1", "b": "q2"}})


def ej143a():
    return desde_tabla("ab", "q1", ["q1"], {"q1": {"a": "q1", "b": "q1"}})


def ej143b():
    """AFD parcial: q0 no tiene transición con b."""
    return desde_tabla("ab", "q0", ["q1"], {"q0": {"a": "q1"}, "q1": {"a": "q1", "b": "q0"}})


def ej148():
    """Progreso del alumno. Alfabeto P, N, A, S (ver docs/02-jflap.md para los supuestos)."""
    filas = {  # P, N, A, S
        "q0": "q1 q2 q3 q3", "q1": "q3 q3 q4 q5", "q2": "q6 q7 q3 q3", "q3": "q3 q3 q3 q3",
        "q4": "q4 q4 q4 q4", "q5": "q8 q9 q3 q3", "q6": "q3 q3 q4 q9", "q7": "q10 q0 q3 q3",
        "q8": "q3 q3 q4 q0", "q9": "q11 q0 q3 q3", "q10": "q3 q3 q4 q0", "q11": "q3 q3 q4 q0"}
    return desde_tabla("PNAS", "q0", ["q4"], {q: dict(zip("PNAS", fila.split())) for q, fila in filas.items()})


def ej149():
    return desde_tabla("01", "A", ["C"], {
        "A": {"0": "B", "1": "C"}, "B": {"0": "A", "1": "C"}, "C": {"0": "C", "1": "A"}})


def ej150():
    return desde_tabla("01a", "A", ["B", "C", "D"], {
        "A": {"0": "B", "1": "C", "a": "D"}, "B": {"0": "B", "1": "C", "a": "C"},
        "C": {"0": "A", "1": "A", "a": "D"}, "D": {"0": "B", "1": "B", "a": "B"}})


EJERCICIOS = {
    "Ej_099_termina_en_001001": ej099,
    "Ej_103_contiene_aabbba": ej103,
    "Ej_107_contiene_0101_y_021": ej107,
    "Ej_109_contiene_abbcb_y_cbaabb": ej109,
    "Ej_111_exactamente_3_veces_01002": ej111,
    "Ej_118_forma_axabya": ej118,
    "Ej_121_longitud_3n_y_contiene_un_0": ej121,
    "Ej_124_canicas_y_palancas": ej124,
    "Ej_128_L2_sin_el_ultimo_simbolo": ej128,
    "Ej_131_termina_en_1": ej131,
    "Ej_133_diagrama_de_M": ej133,
    "Ej_143a_todas_las_cadenas": ej143a,
    "Ej_143b_empieza_y_termina_en_a_sin_bb": ej143b,
    "Ej_148_progreso_del_alumno": ej148,
    "Ej_149_tabla": ej149,
    "Ej_150_tabla": ej150,
}


def main():
    CARPETA.mkdir(parents=True, exist_ok=True)
    for nombre, fabrica in EJERCICIOS.items():
        a = fabrica()
        a.nombre = nombre
        F.guardar_archivo(a, CARPETA / f"{nombre}.jff")
        print(f"{nombre + '.jff':60} {a.tipo:5} {len(a.estados):2} estados")
    # .json y .xml de cada .jff, tomados del .jff ya escrito (así los tres coinciden siempre)
    for ruta in sorted(CARPETA.glob("*.jff")):
        a = F.leer_archivo(ruta)
        for extension in (".json", ".xml"):
            F.guardar_archivo(a, ruta.with_suffix(extension))
    print(f"{len(list(CARPETA.glob('*.jff')))} autómatas en {CARPETA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
