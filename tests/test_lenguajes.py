"""Pruebas del núcleo (lenguajes.py). Se ejecutan con: pytest -q"""

import pytest

import lenguajes
from lenguajes import (
    LAMBDA,
    LONGITUD_MAXIMA,
    LimiteExcedido,
    cantidad_cadenas,
    cantidad_maxima_subcadenas,
    cantidad_prefijos,
    cerradura_kleene,
    cerradura_positiva,
    formatear_cadena,
    parsear_alfabeto,
    prefijos,
    subcadenas,
    sufijos,
    texto_cerradura,
    texto_operacion1,
)


# ---------------------------------------------------------------------------
# Casos que pide el enunciado
# ---------------------------------------------------------------------------

def test_cadena_vacia():
    assert prefijos("") == [""]
    assert sufijos("") == [""]
    assert subcadenas("") == [""]


def test_alfabeto_de_un_solo_simbolo():
    assert cerradura_kleene(["a"], 3) == ["", "a", "aa", "aaa"]
    assert cerradura_positiva(["a"], 3) == ["a", "aa", "aaa"]


def test_prefijos_y_sufijos_de_una_cadena_de_longitud_1():
    assert prefijos("a") == ["", "a"]
    assert sufijos("a") == ["", "a"]


def test_kleene_y_positiva_difieren_en_la_longitud_cero():
    assert cerradura_kleene(["a", "b"], 0) == [""]
    assert cerradura_positiva(["a", "b"], 0) == []


# ---------------------------------------------------------------------------
# Operación 1: prefijos, sufijos y subcadenas
# ---------------------------------------------------------------------------

def test_prefijos_sufijos_y_subcadenas_de_abc():
    assert prefijos("abc") == ["", "a", "ab", "abc"]
    assert sufijos("abc") == ["", "c", "bc", "abc"]
    assert subcadenas("abc") == ["", "a", "b", "c", "ab", "bc", "abc"]


def test_las_subcadenas_repetidas_se_cuentan_una_sola_vez():
    assert subcadenas("aba") == ["", "a", "b", "ab", "ba", "aba"]
    assert len(subcadenas("abab")) == 8        # λ, a, b, ab, ba, aba, bab, abab


@pytest.mark.parametrize("n", range(0, 9))
def test_cantidades_con_simbolos_todos_distintos(n):
    w = "abcdefgh"[:n]
    assert len(prefijos(w)) == len(sufijos(w)) == cantidad_prefijos(n) == n + 1
    assert len(subcadenas(w)) == cantidad_maxima_subcadenas(n) == n * (n + 1) // 2 + 1


def test_con_simbolos_repetidos_hay_menos_subcadenas_que_el_maximo():
    assert len(subcadenas("aaaa")) == 5        # λ, a, aa, aaa, aaaa
    assert len(subcadenas("aaaa")) < cantidad_maxima_subcadenas(4)


@pytest.mark.parametrize("w", ["", "a", "aa", "abab", "mississippi"])
def test_los_resultados_son_prefijos_sufijos_y_subcadenas_de_verdad(w):
    assert all(w.startswith(p) for p in prefijos(w))
    assert all(w.endswith(s) for s in sufijos(w))
    assert all(s in w for s in subcadenas(w))
    for resultado in (prefijos(w), sufijos(w), subcadenas(w)):
        assert "" in resultado and w in resultado
    assert set(prefijos(w)) <= set(subcadenas(w))
    assert set(sufijos(w)) <= set(subcadenas(w))


# ---------------------------------------------------------------------------
# Operación 2: cerradura de Kleene y cerradura positiva
# ---------------------------------------------------------------------------

def test_kleene_y_positiva_con_dos_simbolos():
    assert cerradura_kleene("ab", 2) == ["", "a", "b", "aa", "ab", "ba", "bb"]
    assert cerradura_positiva("ab", 2) == ["a", "b", "aa", "ab", "ba", "bb"]


@pytest.mark.parametrize("alfabeto", ["a", "ab", "abc", "0123"])
@pytest.mark.parametrize("n", range(0, 5))
def test_positiva_es_kleene_sin_la_cadena_vacia(alfabeto, n):
    kleene = cerradura_kleene(alfabeto, n)
    positiva = cerradura_positiva(alfabeto, n)
    assert "" in kleene and "" not in positiva
    assert set(kleene) - {""} == set(positiva)
    assert len(kleene) == len(set(kleene))                       # sin repetidas
    assert all(len(c) <= n and set(c) <= set(alfabeto) for c in kleene)
    esperadas = sum(len(alfabeto) ** k for k in range(n + 1))    # |Σ|⁰ + ... + |Σ|ⁿ
    assert len(kleene) == cantidad_cadenas(len(alfabeto), n) == esperadas
    assert len(positiva) == cantidad_cadenas(len(alfabeto), n, incluir_vacia=False)


def test_el_alfabeto_puede_ser_texto_o_lista_y_se_quitan_repetidos():
    assert cerradura_kleene("aab", 1) == cerradura_kleene(["a", "b"], 1) == ["", "a", "b"]


def test_parsear_alfabeto():
    assert parsear_alfabeto("a, b ,c") == ["a", "b", "c"]
    assert parsear_alfabeto("01") == ["0", "1"]
    assert parsear_alfabeto("a a b") == ["a", "b"]
    with pytest.raises(ValueError):
        parsear_alfabeto("  , ")


# ---------------------------------------------------------------------------
# Límites: más de 200,000 cadenas se rechazan
# ---------------------------------------------------------------------------

def test_se_rechaza_lo_que_pasa_de_doscientas_mil_cadenas():
    assert len(cerradura_kleene("ab", 16)) == 131_071      # 2^17 - 1: cabe
    with pytest.raises(LimiteExcedido, match="200,000"):
        cerradura_kleene("ab", 17)                         # serían 262,143
    with pytest.raises(LimiteExcedido):
        cerradura_positiva("ab", 17)                       # serían 262,142


def test_una_cantidad_enorme_se_rechaza_sin_intentar_generarla():
    with pytest.raises(LimiteExcedido):
        cerradura_kleene("abcdefghij", LONGITUD_MAXIMA)


def test_el_limite_es_exacto(monkeypatch):
    monkeypatch.setattr(lenguajes, "LIMITE_CADENAS", 15)
    assert len(cerradura_kleene("ab", 3)) == 15            # justo en el límite: se acepta
    with pytest.raises(LimiteExcedido):
        cerradura_kleene("ab", 4)                          # son 31


def test_el_limite_de_sigma_positiva_no_cuenta_la_cadena_vacia(monkeypatch):
    monkeypatch.setattr(lenguajes, "LIMITE_CADENAS", 14)
    assert len(cerradura_positiva("ab", 3)) == 14          # Σ⁺ tiene 14 cadenas
    with pytest.raises(LimiteExcedido):
        cerradura_kleene("ab", 3)                          # Σ* tiene 15


def test_longitud_maxima():
    assert len(cerradura_kleene("a", LONGITUD_MAXIMA)) == LONGITUD_MAXIMA + 1
    with pytest.raises(LimiteExcedido):
        cerradura_kleene("a", LONGITUD_MAXIMA + 1)
    assert len(prefijos("a" * LONGITUD_MAXIMA)) == LONGITUD_MAXIMA + 1
    with pytest.raises(LimiteExcedido):
        prefijos("a" * (LONGITUD_MAXIMA + 1))


# ---------------------------------------------------------------------------
# Entradas no válidas
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [-1, 1.5, "3", None, True])
def test_longitud_no_valida(n):
    with pytest.raises(ValueError):
        cerradura_kleene("ab", n)


@pytest.mark.parametrize("alfabeto", ["", [], ["ab"], ["a", ""], [LAMBDA]])
def test_alfabeto_no_valido(alfabeto):
    with pytest.raises(ValueError):
        cerradura_kleene(alfabeto, 2)


def test_la_cadena_debe_ser_texto_y_no_puede_contener_lambda():
    with pytest.raises(ValueError):
        prefijos(None)
    with pytest.raises(ValueError):
        subcadenas("a" + LAMBDA)


# ---------------------------------------------------------------------------
# Presentación y texto para guardar
# ---------------------------------------------------------------------------

def test_formatear_cadena():
    assert formatear_cadena("") == LAMBDA == "λ"
    assert formatear_cadena("ab") == "ab"


def test_texto_operacion1():
    texto = texto_operacion1("ab")
    assert texto.splitlines() == [
        "Operación 1: prefijos, sufijos y subcadenas",
        "Cadena: ab",
        "Longitud: 2",
        "",
        "Prefijos (3):", "  λ", "  a", "  ab",
        "",
        "Sufijos (3):", "  λ", "  b", "  ab",
        "",
        "Subcadenas distintas (4):", "  λ", "  a", "  b", "  ab",
    ]
    assert texto.endswith("\n")
    assert texto_operacion1("").splitlines()[1] == "Cadena: λ"


def test_texto_cerradura():
    cadenas = cerradura_positiva("ab", 1)
    assert texto_cerradura("ab", 1, cadenas, positiva=True).splitlines() == [
        "Operación 2: Σ⁺ (cerradura positiva)",
        "Alfabeto: {a, b}",
        "Longitud máxima: 1",
        "Cantidad de cadenas: 2",
        "",
        "a",
        "b",
    ]
    assert texto_cerradura("ab", 0, [""], positiva=False).splitlines()[-1] == "λ"
