"""Verifica cada autómata entregado de la Lista 2 (automatas/lista2-afd/) contra la definición
exacta de su lenguaje, no contra unos cuantos ejemplos: se prueban todas las cadenas hasta
cierta longitud y muchas cadenas largas al azar. Donde hay un patrón, además se compara con un
AFND construido por otro camino usando cadena_distintiva, que es una comparación exacta."""

import random
import re
from itertools import product
from pathlib import Path

import pytest

import automata as A
import construcciones as C
import formatos as F
from automata import Automata

CARPETA = Path(__file__).resolve().parent.parent / "automatas" / "lista2-afd"
S1, S2, S3 = "012", "abc01", "ab"


def cargar(numero):
    rutas = sorted(CARPETA.glob(f"Ej_{numero}_*.jff"))
    assert len(rutas) == 1, f"debe haber exactamente un .jff para el ejercicio {numero}"
    return F.leer_archivo(rutas[0])


def apariciones(w, patron):
    return [i for i in range(len(w) - len(patron) + 1) if w.startswith(patron, i)]


def apariciones_sin_traslape(w, patron):
    cuenta = i = 0
    while (j := w.find(patron, i)) >= 0:
        cuenta, i = cuenta + 1, j + len(patron)
    return cuenta


def todos_los_bloques_tienen_un_cero(w):
    return len(w) % 3 == 0 and all("0" in w[i:i + 3] for i in range(0, len(w), 3))


def canicas(w):
    """Mecanismo del ejercicio 124 (palanca: 0 izquierda, 1 derecha)."""
    p, ultima = [0, 0, 0], None
    for c in w:
        if c == "0":
            if p[0] == 0:
                p[0], ultima = 1, "A"
            else:
                p[0], ultima = 0, "A" if p[2] == 0 else "R"
                p[2] ^= 1
        elif p[1] == 0:
            p[1], ultima = 1, "A" if p[2] == 0 else "R"
            p[2] ^= 1
        else:
            p[1], ultima = 0, "R"
    return ultima == "A"


# Diagrama del ejercicio 128 (completo, con las flechas de F hacia D), transcrito del enunciado.
DIAGRAMA_128 = Automata("01", list("ABCDEF"), "A", ["F"],
                        [("A", "0", "B"), ("A", "1", "C"), ("B", "0", "C"), ("B", "1", "D"), ("C", "0", "D"),
                         ("C", "1", "E"), ("D", "0", "F"), ("D", "1", "E"), ("E", "0", "E"), ("E", "1", "F"),
                         ("F", "0", "D"), ("F", "1", "D")])

# Tabla del ejercicio 133 tal como la da el enunciado.
TABLA_133 = {("q0", "a"): "q2", ("q3", "a"): "q1", ("q2", "b"): "q3", ("q1", "a"): "q3",
             ("q0", "b"): "q1", ("q3", "b"): "q2", ("q2", "a"): "q0", ("q1", "b"): "q0"}


def tabla_133(w):
    q = "q0"
    for c in w:
        q = TABLA_133[(q, c)]
    return q == "q0"


# número del ejercicio -> (alfabeto, función que dice si la cadena pertenece al lenguaje)
CASOS = {
    "097": (S1, lambda w: len(w) % 3 == 0),
    "099": (S1, lambda w: w.endswith("001001")),
    "102": (S3, lambda w: "abbbab" in w),
    "103": (S3, lambda w: "aabbba" in w),
    "106": (S1, lambda w: "1101001" in w),
    "107": (S1, lambda w: "0101" in w and "021" in w),
    "109": (S2, lambda w: "abbcb" in w and "cbaabb" in w),
    "111": (S1, lambda w: len(apariciones(w, "01002")) == 3),
    "112": (S1, lambda w: apariciones_sin_traslape(w, "010") == 2),
    "113": (S1, lambda w: len(apariciones(w, "010")) == 2),
    "118": (S3, lambda w: re.fullmatch("a[ab]*ab[ab]*a", w) is not None),
    "120": (S1, lambda w: len(w) >= 2 and w[0] != w[-1]),
    "121": (S1, todos_los_bloques_tienen_un_cero),
    "122": (S1, lambda w: all("0" in w[i:i + 3] for i in range(len(w) - 2))),
    "123": (S3, lambda w: len(w) >= 4 and w[:2] == w[-2:]),
    "124": ("01", canicas),
    "128": ("01", lambda w: any(DIAGRAMA_128.acepta(w + a) for a in "01")),
    "131": ("01", lambda w: w.endswith("1")),
    "133": ("ab", tabla_133),
    "135": ("ab", lambda w: re.fullmatch("b+ab+", w) is not None),
    "137": ("ab", lambda w: w.startswith("ab")),
    "139": ("01", lambda w: w.count("0") % 2 == 0),
    "141": ("01", lambda w: re.fullmatch("(1|01)*", w) is not None),
    "143a": ("ab", lambda w: True),
    "143b": ("ab", lambda w: re.fullmatch("a(a|ba)*", w) is not None),
    "145": ("01", lambda w: (int(w[::-1], 2) if w else 0) % 5 == 0),
    "147": ("01", lambda w: (int(w, 2) if w else 0) % 6 == 0),
}


LONGITUD_EXHAUSTIVA = {2: 15, 3: 10, 5: 7}      # según el tamaño del alfabeto: todas las cadenas hasta esa longitud


def corredor(a):
    """Función rápida cadena -> bool para un AFD, con la tabla de transiciones en un dict."""
    tabla = {(d, lee): h for d, lee, h in a.transiciones()}
    inicial, finales = a.inicial, a.aceptacion

    def acepta(w):
        q = inicial
        for c in w:
            q = tabla.get((q, c))
            if q is None:
                return False
        return q in finales
    return acepta


@pytest.mark.parametrize("numero", list(CASOS))
def test_el_automata_reconoce_exactamente_el_lenguaje_del_ejercicio(numero):
    alfabeto, pertenece = CASOS[numero]
    a = cargar(numero)
    assert a.tipo == "AFD", "los ejercicios de la Lista 2 piden un AFD"
    assert set(a.alfabeto) == set(alfabeto)
    rapido = corredor(a)
    longitud = LONGITUD_EXHAUSTIVA[len(alfabeto)]
    for n in range(longitud + 1):
        for t in product(alfabeto, repeat=n):
            w = "".join(t)
            assert rapido(w) == pertenece(w), f"{numero}: {w!r}"
    azar = random.Random(int.from_bytes(numero.encode(), "big"))
    for _ in range(2_000):                                  # cadenas largas, con la API pública
        w = "".join(azar.choice(alfabeto) for _ in range(azar.randint(longitud, 60)))
        assert a.acepta(w) == rapido(w) == pertenece(w), f"{numero}: {w!r}"


def test_todos_los_automatas_obligatorios_de_la_lista_2_estan_entregados():
    esperados = set(CASOS) | {"148", "149", "150"}
    entregados = {p.name.split("_")[1] for p in CARPETA.glob("*.jff")}
    assert esperados == entregados


@pytest.mark.parametrize("numero", [n for n in CASOS if n != "143b"])
def test_los_afd_son_completos_menos_el_parcial_del_ejercicio_143b(numero):
    assert cargar(numero).es_completo()
    assert not cargar("143b").es_completo()


# ---------------------------------------------------------------------------
# Comparación exacta con un AFND construido por otro camino
# ---------------------------------------------------------------------------

def test_99_termina_en_001001_coincide_con_su_afnd():
    assert A.lenguajes_iguales(cargar("099"), C.termina_en("001001", S1))
    assert len(cargar("099").estados) == 7


def test_103_contiene_aabbba_coincide_con_su_afnd():
    assert A.lenguajes_iguales(cargar("103"), C.contiene("aabbba", S3))


def test_107_contiene_los_dos_patrones_coincide_con_la_union_de_los_dos_ordenes():
    """0101 y 021 no pueden traslaparse, así que aparecen uno después del otro."""
    afnd = C.union(C.secuencia("0101", "021", S1), C.secuencia("021", "0101", S1))
    assert A.lenguajes_iguales(cargar("107"), afnd)
    assert len(cargar("107").estados) == 13


def test_109_con_traslape_coincide_con_el_afnd_que_incluye_las_cadenas_fundidas():
    """abbcb y cbaabb se traslapan en dos formas: abbcbaabb (comparten «cb») y cbaabbcb (comparten «abb»)."""
    p, q = "abbcb", "cbaabb"
    afnd = C.union(C.secuencia(p, q, S2), C.secuencia(q, p, S2), C.contiene("abbcbaabb", S2), C.contiene("cbaabbcb", S2))
    assert A.lenguajes_iguales(cargar("109"), afnd)
    assert len(cargar("109").estados) == 22
    for w in ("abbcbaabb", "cbaabbcb", "abbcbcbaabb", "cbaabbabbcb"):      # las que fallaba la Práctica 1
        assert cargar("109").acepta(w)
    assert not cargar("109").acepta("abbcb") and not cargar("109").acepta("cbaabb")


def test_118_a_x_abya_coincide_con_su_afnd_y_la_cadena_mas_corta_es_aaba():
    a = Automata(S3, [f"q{i}" for i in range(5)], "q0", ["q4"],
                 [("q0", "a", "q1"), ("q1", "a", "q1"), ("q1", "b", "q1"), ("q1", "a", "q2"),
                  ("q2", "b", "q3"), ("q3", "a", "q3"), ("q3", "b", "q3"), ("q3", "a", "q4")])
    assert A.lenguajes_iguales(cargar("118"), a)
    assert cargar("118").acepta("aaba") and not cargar("118").acepta("aba")      # no se comparte la `a` inicial
    assert len(cargar("118").estados) == 6


def test_121_acepta_la_cadena_vacia_y_la_trampa_no_es_de_aceptacion():
    a = cargar("121")
    assert a.acepta("") and a.acepta("000") and a.acepta("021020200")
    assert not a.acepta("111") and not a.acepta("2101021")
    assert len(a.estados) == 6 and a.inicial in a.aceptacion


def test_111_exactamente_tres_apariciones_tiene_21_estados():
    a = cargar("111")
    assert len(a.estados) == 21                       # (progreso del patrón 0..4) x (apariciones 0..3) + trampa
    assert a.acepta("010020100201002") and not a.acepta("01002010020100201002")


def test_el_afd_del_124_equivale_a_la_tabla_de_12_estados_de_la_practica_1():
    t = {0: (1, 2), 1: (3, 4), 2: (4, 5), 3: (6, 7), 4: (7, 8), 5: (6, 7), 6: (0, 9), 7: (10, 0),
         8: (0, 9), 9: (2, 11), 10: (2, 11), 11: (3, 4)}
    p1 = Automata("01", [f"q{i}" for i in t], "q0", [f"q{i}" for i in (1, 2, 3, 4, 6, 10)],
                  [(f"q{q}", s, f"q{d}") for q, (a, b) in t.items() for s, d in (("0", a), ("1", b))])
    assert A.lenguajes_iguales(cargar("124"), p1)
    assert len(cargar("124").estados) == 12 and not cargar("124").acepta("")     # sin canicas no hay última salida


# ---------------------------------------------------------------------------
# Ejercicios con preguntas concretas
# ---------------------------------------------------------------------------

def test_128_los_estados_de_aceptacion_de_l2_son_d_y_e():
    a = cargar("128")
    assert a.aceptacion == frozenset({"D", "E"}) and a.estados == list("ABCDEF")
    assert not DIAGRAMA_128.acepta("00100") and DIAGRAMA_128.acepta("001001")      # el ejemplo del enunciado
    assert a.acepta("00100") and not a.acepta("001001")
    assert ("F", "0", "D") in a.transiciones() and ("D", "1", "E") in a.transiciones()


def test_133_tiene_las_ocho_transiciones_del_enunciado():
    a = cargar("133")
    assert {(d, l): h for d, l, h in a.transiciones()} == TABLA_133


def test_131_el_estado_depende_solo_del_ultimo_simbolo():
    a = cargar("131")
    assert a.inicial == "q1" and a.aceptacion == frozenset({"q2"})
    assert a.delta_hat({"q1"}, "0") == a.delta_hat({"q2"}, "0") == frozenset({"q1"})
    assert a.delta_hat({"q1"}, "1") == a.delta_hat({"q2"}, "1") == frozenset({"q2"})


def test_143b_se_bloquea_al_leer_b_en_el_estado_inicial():
    a = cargar("143b")
    assert a.simular("b").pasos[-1].conjunto == frozenset()
    assert not a.simular("abba").consumida                  # se bloquea al leer la tercera letra, quedando una por leer


def test_149_valores_pedidos():
    a = cargar("149")
    assert a.delta("B", "0") == frozenset({"A"}) and a.delta("C", "1") == frozenset({"A"})
    assert a.delta_hat({"A"}, "1101") == frozenset({"C"})
    assert a.delta_hat({"A"}, "01001") == frozenset({"A"})
    assert a.aceptacion == frozenset({"C"})


def test_150_valores_pedidos():
    a = cargar("150")
    assert a.delta_hat({"B"}, "10a11") == frozenset({"C"})
    assert a.delta_hat({"B"}, "aa1100") == frozenset({"B"})
    assert a.delta_hat({"A"}, "a01a01") == frozenset({"C"})
    assert a.delta_hat({"C"}, "a11a00") == frozenset({"B"})
    assert a.aceptacion == frozenset({"B", "C", "D"}) and a.inicial == "A"


def test_148_progreso_del_alumno():
    a = cargar("148")
    for w in ("PA", "NPA", "PSPA", "NNPA"):                         # terminan aprobando
        assert a.acepta(w), w
    for w in ("PP", "A", "S", "PSA", ""):                           # secuencia inválida o sin aprobar
        assert not a.acepta(w), w
    assert a.simular("PSPS").pasos[-1].conjunto == frozenset({"q0"})        # dos aplazamientos: se reinicia el año
    assert a.simular("NNN").pasos[-1].conjunto == frozenset({"q0"})        # tres convocatorias sin presentarse: se reinicia
    assert all(a.acepta(w + "PA") for w in ("PSPS", "NNN", "NNNN"))        # tras reiniciar se puede aprobar
    assert a.simular("PA").pasos[-1].conjunto == frozenset({"q4"}) and a.aceptacion == frozenset({"q4"})
