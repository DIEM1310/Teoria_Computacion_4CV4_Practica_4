"""Pruebas de los validadores de la Práctica 4 (src/validadores.py), Ejercicio 4.

La prueba de congruencia (al menos 500 cadenas por validador) es el requisito explícito del
enunciado: que el autómata obtenido por el Ejercicio 2 y re.fullmatch sobre la traducción a
Python coincidan en todas. Se repite para cada uno de los tres validadores.
"""

import re

import pytest

import validadores as V
from automata import SimboloFueraDelAlfabeto


@pytest.fixture(scope="module")
def etapas_por_clave():
    """Construye el autómata de cada validador una sola vez (no en cada cadena de la prueba)."""
    return {v.clave: V.construir_automata(v) for v in V.VALIDADORES}


def test_hay_al_menos_tres_validadores():
    assert len(V.VALIDADORES) >= 3
    assert len({v.clave for v in V.VALIDADORES}) == len(V.VALIDADORES)       # claves distintas


@pytest.mark.parametrize("v", V.VALIDADORES, ids=[v.clave for v in V.VALIDADORES])
def test_cada_validador_tiene_notacion_justificacion_y_traduccion_a_re(v):
    assert v.notacion_abreviada and v.leyenda and v.justificacion
    assert len(v.alfabeto) > 0
    re.compile(v.python_re)                                                   # es un patrón válido de re


@pytest.mark.parametrize("v", V.VALIDADORES, ids=[v.clave for v in V.VALIDADORES])
def test_la_minimizacion_no_aumenta_el_numero_de_estados(v, etapas_por_clave):
    etapas = etapas_por_clave[v.clave]
    assert len(etapas.minimo.estados) <= len(etapas.afd.estados) <= len(etapas.afn.estados) <= len(etapas.afn_lambda.estados)
    assert etapas.afd.es_determinista() and etapas.minimo.es_determinista()


@pytest.mark.parametrize("v", V.VALIDADORES, ids=[v.clave for v in V.VALIDADORES])
def test_congruencia_con_re_fullmatch_sobre_quinientas_cadenas(v, etapas_por_clave):
    """Para quinientas cadenas generadas (al menos la mitad del lenguaje y la otra mitad
    corrompidas o al azar), el AFD mínimo y re.fullmatch sobre la traducción a Python deben
    coincidir en todas."""
    etapas = etapas_por_clave[v.clave]
    casos = V.generar_casos(v, 500)
    assert len(casos) >= 500
    discrepancias = [w for w in casos if etapas.minimo.acepta(w) != V.coincide_con_re(v, w)]
    assert discrepancias == []
    # La mitad "válida" de la generación no debe ser trivial: hay cadenas aceptadas y rechazadas.
    aceptadas = sum(1 for w in casos if etapas.minimo.acepta(w))
    assert 0 < aceptadas < len(casos)


@pytest.mark.parametrize("v", V.VALIDADORES, ids=[v.clave for v in V.VALIDADORES])
def test_generar_casos_es_determinista_para_la_misma_semilla(v):
    assert V.generar_casos(v, 50, "misma") == V.generar_casos(v, 50, "misma")
    assert V.generar_casos(v, 50, "una") != V.generar_casos(v, 50, "otra")


def test_fecha_acepta_formatos_validos_y_rechaza_valores_fuera_de_rango(etapas_por_clave):
    minimo = etapas_por_clave["fecha"].minimo
    for valida in ("01/01/2027", "31/12/2026", "2027-01-01", "2026-12-31"):
        assert minimo.acepta(valida), valida
    for invalida in ("32/01/2027", "01/13/2027", "00/01/2027", "1/1/2027", "01-01-2027"):
        assert not minimo.acepta(invalida), invalida


def test_telefono_acepta_diez_digitos_seguidos_o_con_guiones(etapas_por_clave):
    minimo = etapas_por_clave["telefono"].minimo
    assert minimo.acepta("5512345678")
    assert minimo.acepta("55-1234-5678")
    assert not minimo.acepta("551234567")        # faltan dígitos
    with pytest.raises(SimboloFueraDelAlfabeto):  # el espacio no es un símbolo del alfabeto
        minimo.acepta("55 1234 5678")


def test_contrasena_exige_letra_inicial_digito_final_y_longitud_ocho(etapas_por_clave):
    minimo = etapas_por_clave["contrasena"].minimo
    assert minimo.acepta("ab3fg7h9")
    assert not minimo.acepta("1b3fg7h9")   # no empieza en letra
    assert not minimo.acepta("ab3fg7hh")   # no termina en dígito
    assert not minimo.acepta("ab3fg7h")    # longitud 7
