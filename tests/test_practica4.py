"""Práctica 4: pruebas de integración del teorema de Kleene en sus dos direcciones.

Ejercicio 2 (expresión → AFN-λ → AFN → AFD → AFD mínimo) y Ejercicio 3 (AFD → expresión por
eliminación de estados), encadenados y comparados entre sí y con los resultados ya verificados
de la Práctica 3 (docs/practica3/01-afd-a-er-jflap.md).
"""

import itertools

import pytest

import ejercicios as E
import expresiones as X
from automata import comparar_por_minimo
from construcciones import cadenas_hasta


# ---------------------------------------------------------------------------
# Ejercicio 3: el orden de eliminación documentado en la Práctica 3 reproduce
# exactamente la misma expresión que ese documento (sin volver a elegirlo al azar).
# ---------------------------------------------------------------------------

ORDEN_Y_EXPRESION_DOCUMENTADOS = [
    ("Ej_254_tabla", ["B", "A"], "(0+11*0)*11*"),
    ("Ej_255_tabla", ["B", "A"], "((0+1)1*0)*"),
    ("Ej_256_tabla", ["A", "B"], "(1+2)*0(0+1+2(1+2)*0)*"),
    ("Ej_257_tabla", ["B", "C", "A"], "((1+01*0)(0+1))*(01*+1+01*0)"),
    ("Ej_258_tabla", ["B", "A", "C"], "(0+1)(01+(1+00)(0+1))*"),
]


@pytest.mark.parametrize("nombre, orden, esperada", ORDEN_Y_EXPRESION_DOCUMENTADOS,
                         ids=[n for n, _, _ in ORDEN_Y_EXPRESION_DOCUMENTADOS])
def test_el_orden_de_la_practica_3_da_la_misma_expresion_del_documento(nombre, orden, esperada):
    a = E.POR_NOMBRE[nombre].fabrica()
    er, pasos = X.eliminar_en_orden(a, orden)
    assert str(er) == esperada
    assert len(pasos) == len(orden)


@pytest.mark.parametrize("nombre", [n for n, _, _ in ORDEN_Y_EXPRESION_DOCUMENTADOS])
def test_verificar_determinismo_antes_de_eliminar_estados(nombre):
    """Ejercicio 3: los cinco autómatas del Ejercicio 1 de la Práctica 3 son AFD (lo que exige
    la eliminación de estados), y motivo_no_determinista lo confirma antes de aplicarla."""
    a = E.POR_NOMBRE[nombre].fabrica()
    assert a.es_determinista() and a.motivo_no_determinista() is None


# ---------------------------------------------------------------------------
# Ida y vuelta: expresión -> AFN-λ -> AFD mínimo -> expresión -> AFN-λ -> AFD mínimo
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("texto, alfabeto", [
    ("a+b*", "ab"), ("(ab)*a", "ab"), ("(a+b)*abb", "ab"), ("a(ba)*+b", "ab"),
    ("(a+b)*b", "ab"), ("0*1(1+00*1)*", "01"), ("((0+1)1*0)*", "01"),
])
def test_ida_y_vuelta_expresion_automata_expresion(texto, alfabeto):
    """Construye el AFD mínimo de una expresión (Ejercicio 2), obtiene su expresión por
    eliminación de estados (Ejercicio 3) y comprueba que el AFD mínimo de ESA expresión
    reconoce el mismo lenguaje que el primero: las dos direcciones del teorema son inversas
    una de la otra salvo la forma de escribir la expresión."""
    e1 = X.parsear(texto)
    afn1, _ = X.desde_expresion(e1, alfabeto)
    minimo1 = afn1.quitar_lambda().a_afd(completo=True).afd.minimizar()

    e2, _, _ = X.desde_automata(minimo1)
    afn2, _ = X.desde_expresion(e2, alfabeto)
    minimo2 = afn2.quitar_lambda().a_afd(completo=True).afd.minimizar()

    resultado = comparar_por_minimo(minimo1, minimo2)
    assert resultado.equivalentes, (texto, resultado.motivo)


# ---------------------------------------------------------------------------
# El motor completo contra una muestra amplia de expresiones (sustituye a los
# ejercicios 241 a 253 de la Lista 3, que son opcionales y no están en la entrega
# del curso: ver el comentario en ejercicios.py).
# ---------------------------------------------------------------------------

EXPRESIONES_DE_MUESTRA = [
    "a", "ab", "a+b", "a*", "(a+b)*", "a*b*", "(ab)*", "a(a+b)*b", "(a+b)(a+b)*",
    "a+ab+abb", "(a+b)*a(a+b)(a+b)", "λ+a", "a*+b*", "(a*b*)*", "ab+ba",
    "(0+1)*00", "(0+1)*11(0+1)*", "0(0+1)*1", "(01+10)*", "(0+1)*0(0+1)",
]


@pytest.mark.parametrize("texto", EXPRESIONES_DE_MUESTRA)
def test_el_motor_completo_equivale_a_la_expresion_por_fuerza_bruta(texto):
    alfabeto = sorted(set(texto) - set("()+*λ∅ "))
    e = X.parsear(texto)
    afn, _ = X.desde_expresion(e, alfabeto)
    minimo = afn.quitar_lambda().a_afd(completo=True).afd.minimizar()
    for w in cadenas_hasta(alfabeto, 10):
        assert minimo.acepta(w) == X.acepta(e, w), (texto, w)
