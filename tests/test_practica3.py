"""Práctica 3: pruebas de los algoritmos del Ejercicio 2.

Casos de prueba: Lista 3, ejercicios 151 a 157 (AFD), 192 a 194 y 260 a 263 (AFN) y 196 a 200 (AFN-λ).
El ejercicio 191 no tiene autómata que probar en esta práctica (véase docs/practica3/02-software.md).
"""

import itertools

import pytest

import controlador as K
import ejercicios as E
from automata import (
    Automata, AutomataInvalido, SimboloFueraDelAlfabeto, comparar_por_minimo, isomorfismo, lenguajes_iguales,
)
from construcciones import cadenas_hasta

# Casos de prueba de la Práctica 3 (nombre en el registro de ejercicios.py)
CASOS = (
    [f"Ej_{n}_original" for n in range(151, 158)]
    + ["Ej_192_tabla", "Ej_193_tabla", "Ej_194_tabla"]
    + [f"Ej_{n}_tabla" for n in range(196, 201)]
    + ["Ej_260_tabla", "Ej_261_figura", "Ej_262_ab_ba", "Ej_263_figura"]
)


def cadena_de(texto):
    return K.texto_de_cadena(texto)


def las_cuatro_versiones(nombre):
    """(original, AFN sin λ, AFD de subconjuntos, AFD mínimo) del caso."""
    original = E.POR_NOMBRE[nombre].fabrica()
    sin_lambda = original.quitar_lambda()
    afd = sin_lambda.a_afd().afd
    minimo = afd.minimizar()
    return original, sin_lambda, afd, minimo


def longitud_de_prueba(afd, minimo):
    """Longitud máxima de las cadenas que se comparan.

    Por el teorema de Moore, dos AFD completos de p y q estados que difieren aceptan de distinta forma
    alguna cadena de longitud <= p + q - 2. Se compara el AFD de subconjuntos con el mínimo (ambos
    completados) hasta esa longitud; el original y el AFN sin λ comparten estados con el AFD por construcción
    y además se comparan con el AFD con el decisor exacto (lenguajes_iguales). Se pide al menos 6."""
    p = len(afd.completar()[0].estados)
    q = len(minimo.completar()[0].estados)
    return max(p + q - 2, 6)


@pytest.mark.parametrize("nombre", CASOS)
def test_original_afn_sin_lambda_afd_y_minimo_aceptan_las_mismas_cadenas(nombre):
    original, sin_lambda, afd, minimo = las_cuatro_versiones(nombre)
    n = longitud_de_prueba(afd, minimo)
    for w in cadenas_hasta(original.alfabeto, n):
        esperado = original.acepta(w)
        assert sin_lambda.acepta(w) == esperado, f"AFN sin λ difiere en {w!r}"
        assert afd.acepta(w) == esperado, f"AFD de subconjuntos difiere en {w!r}"
        assert minimo.acepta(w) == esperado, f"AFD mínimo difiere en {w!r}"


@pytest.mark.parametrize("nombre", CASOS)
def test_las_cuatro_versiones_equivalen_segun_el_decisor_exacto(nombre):
    original, sin_lambda, afd, minimo = las_cuatro_versiones(nombre)
    assert lenguajes_iguales(original, sin_lambda)
    assert lenguajes_iguales(original, afd)
    assert lenguajes_iguales(original, minimo)


@pytest.mark.parametrize("nombre", CASOS)
def test_el_minimo_no_tiene_mas_estados_que_el_afd_del_que_procede(nombre):
    _, _, afd, minimo = las_cuatro_versiones(nombre)
    assert len(minimo.estados) <= len(afd.estados)


@pytest.mark.parametrize("nombre", CASOS)
def test_el_afn_sin_lambda_no_tiene_transiciones_lambda_ni_mas_estados(nombre):
    original, sin_lambda, _, _ = las_cuatro_versiones(nombre)
    assert not sin_lambda.tiene_lambda
    assert sin_lambda.estados == original.estados


@pytest.mark.parametrize("nombre", CASOS)
def test_el_afd_es_determinista_y_el_minimo_ya_no_se_puede_reducir(nombre):
    _, _, afd, minimo = las_cuatro_versiones(nombre)
    assert afd.es_determinista() and minimo.es_determinista()
    assert len(minimo.minimizar().estados) == len(minimo.estados)
    assert minimo.accesibles() == tuple(minimo.estados)


# ---------------------------------------------------------------------------
# 2.1 Simulación directa: estados antes y después de la λ-clausura
# ---------------------------------------------------------------------------

def test_cada_paso_guarda_los_estados_antes_y_despues_de_la_clausura():
    a = E.POR_NOMBRE["Ej_196_tabla"].fabrica()
    r = a.simular("110")
    assert r.pasos[0].antes == frozenset({a.inicial})
    assert r.pasos[0].conjunto == a.clausura({a.inicial})
    for anterior, paso in zip(r.pasos, r.pasos[1:]):
        assert paso.antes == a.mover(anterior.conjunto, paso.simbolo)
        assert paso.conjunto == a.clausura(paso.antes)
        assert paso.antes <= paso.conjunto


@pytest.mark.parametrize("nombre", [f"Ej_{n}_tabla" for n in range(196, 201)])
def test_la_simulacion_directa_coincide_con_la_del_afd_equivalente(nombre):
    a = E.POR_NOMBRE[nombre].fabrica()
    afd = a.quitar_lambda().a_afd(completo=True).afd
    for w in cadenas_hasta(a.alfabeto, 8):
        recorrido = a.simular(w)
        assert recorrido.aceptada == afd.acepta(w)


def test_la_descripcion_de_un_paso_muestra_antes_y_despues_de_la_clausura():
    a = E.POR_NOMBRE["Ej_196_tabla"].fabrica()
    r = a.simular("1")
    texto = K.descripcion_de_paso(a, r, 1)
    assert "Antes de la λ-clausura" in texto and "Después de la λ-clausura" in texto
    assert "antes de la λ-clausura" in r.texto(a.estados)


def test_clausura_de_un_estado_elegido():
    a = E.POR_NOMBRE["Ej_197_tabla"].fabrica()
    for q in a.estados:
        linea = K.clausura_de_estado(a, q)
        assert linea.startswith(f"Cl({q}) = ")
    with pytest.raises(AutomataInvalido):
        K.clausura_de_estado(a, "no_existe")


# ---------------------------------------------------------------------------
# 2.2 Eliminación de transiciones λ
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("nombre", [f"Ej_{n}_tabla" for n in range(196, 201)])
def test_el_detalle_de_quitar_lambda_es_coherente_con_el_resultado(nombre):
    original = E.POR_NOMBRE[nombre].fabrica()
    r = original.quitar_lambda_detalle()
    assert r.afn == original.quitar_lambda()
    assert set(r.anadidas) | (set(original.transiciones()) - set(r.quitadas)) == set(r.afn.transiciones())
    assert all(lee == "" for _, lee, _ in r.quitadas)
    assert all(lee != "" for _, lee, _ in r.anadidas)
    for q in r.nuevas_aceptacion:
        assert not original.es_aceptacion(q) and r.afn.es_aceptacion(q)
        assert original.clausura({q}) & original.aceptacion
    assert r.afn.aceptacion == original.aceptacion | set(r.nuevas_aceptacion)


def test_quitar_lambda_en_197_agrega_lo_que_se_alcanza_por_lambda():
    a = E.POR_NOMBRE["Ej_197_tabla"].fabrica()
    r = a.quitar_lambda_detalle()
    assert r.nuevas_aceptacion == ("A", "B", "C")
    assert ("A", "1", "D") in r.anadidas and ("C", "0", "A") in r.anadidas
    assert len(r.quitadas) == 3
    lineas = K.lineas_de_quitar_lambda(a, r)
    assert any("pasa a ser de aceptación" in x for x in lineas)


def test_un_autonata_sin_lambda_no_cambia_al_quitar_lambda():
    a = E.POR_NOMBRE["Ej_192_tabla"].fabrica()
    r = a.quitar_lambda_detalle()
    assert r.anadidas == () and r.quitadas == () and r.nuevas_aceptacion == ()
    assert r.afn == a


# ---------------------------------------------------------------------------
# 2.3 Construcción de subconjuntos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("nombre", CASOS)
def test_la_tabla_paso_a_paso_reproduce_el_afd(nombre):
    a = E.POR_NOMBRE[nombre].fabrica().quitar_lambda()
    conv = a.a_afd()
    pasos = a.pasos_subconjuntos()
    transiciones = {(p.origen, p.simbolo, p.destino) for p in pasos if p.destino}
    assert transiciones == {(d, l, h) for d, l, h in conv.afd.transiciones()}
    # los destinos «nuevos» son los subconjuntos que se descubren, en el orden en que aparecen en el AFD
    assert [p.destino for p in pasos if p.nuevo] == [q for q in conv.afd.estados if q != conv.afd.inicial]
    assert {p.origen for p in pasos if p.aceptacion} == set(conv.afd.aceptacion)


def test_solo_se_construyen_los_subconjuntos_alcanzables():
    a = E.POR_NOMBRE["Ej_193_tabla"].fabrica()
    conv = a.a_afd()
    assert len(conv.afd.estados) < 2 ** len(a.estados)
    assert conv.afd.accesibles() == tuple(conv.afd.estados)


def test_la_razon_de_aceptacion_dice_que_estado_la_causa():
    a = E.POR_NOMBRE["Ej_193_tabla"].fabrica()     # F = {D}
    conv = a.a_afd()
    for nombre, subconjunto in conv.subconjuntos.items():
        razon = a.razon_de_aceptacion(subconjunto)
        assert ("es de aceptación porque contiene D" in razon) == ("D" in subconjunto)
        assert (conv.afd.es_aceptacion(nombre)) == ("D" in subconjunto)
    assert len(K.lineas_de_aceptacion(a, conv)) == len(conv.subconjuntos)


def test_con_completo_aparece_el_conjunto_vacio():
    a = E.POR_NOMBRE["Ej_262_ab_ba"].fabrica()
    sin = a.pasos_subconjuntos()
    con = a.pasos_subconjuntos(completo=True)
    assert any(p.destino is None for p in sin) and all(p.destino for p in con)
    assert any(p.destino == "∅" for p in con)


# ---------------------------------------------------------------------------
# 2.4 Minimización y equivalencia de AFD
# ---------------------------------------------------------------------------

def renombrado(a, prefijo="z"):
    """El mismo AFD con los estados renombrados y en otro orden."""
    nombres = {q: f"{prefijo}{i}" for i, q in enumerate(reversed(a.estados))}
    nuevo = Automata(a.alfabeto, [nombres[q] for q in reversed(a.estados)], nombres[a.inicial],
                     [nombres[q] for q in a.aceptacion], [(nombres[d], l, nombres[h]) for d, l, h in a.transiciones()])
    return nuevo


@pytest.mark.parametrize("nombre", [f"Ej_{n}_original" for n in range(151, 158)])
def test_un_afd_y_su_minimo_son_equivalentes_pero_no_isomorfos_si_se_redujo(nombre):
    a = E.POR_NOMBRE[nombre].fabrica()
    resultado = comparar_por_minimo(a, a.minimizar())
    assert resultado.equivalentes and resultado.correspondencia
    assert lenguajes_iguales(a, a.minimizar())


@pytest.mark.parametrize("nombre", [f"Ej_{n}_original" for n in range(151, 158)])
def test_el_minimo_es_el_mismo_salvo_nombres_si_se_renombran_los_estados(nombre):
    m = E.POR_NOMBRE[nombre].fabrica().minimizar()
    mapa = isomorfismo(m, renombrado(m))
    assert mapa is not None and len(mapa) == len(m.estados)


def test_dos_afd_de_distinto_lenguaje_no_son_equivalentes():
    pares = list(itertools.combinations([f"Ej_{n}_original" for n in range(151, 158)], 2))
    for x, y in pares:
        a, b = E.POR_NOMBRE[x].fabrica(), E.POR_NOMBRE[y].fabrica()
        if a.alfabeto != b.alfabeto:
            continue
        # la decisión por mínimos coincide con el decisor exacto
        assert comparar_por_minimo(a, b).equivalentes == lenguajes_iguales(a, b)


def test_afd_distintos_con_igual_numero_de_estados_no_son_isomorfos():
    a = Automata("ab", ["p", "q"], "p", ["q"], [("p", "a", "q"), ("p", "b", "p"), ("q", "a", "q"), ("q", "b", "p")])
    b = Automata("ab", ["p", "q"], "p", ["q"], [("p", "a", "p"), ("p", "b", "q"), ("q", "a", "p"), ("q", "b", "q")])
    r = comparar_por_minimo(a, b)
    assert not r.equivalentes and len(r.minimo_a.estados) == len(r.minimo_b.estados) == 2
    assert not lenguajes_iguales(a, b)
    assert "NO SON EQUIVALENTES" in K.lineas_de_equivalencia(r)[1]


def test_dos_afd_distintos_pero_del_mismo_lenguaje_son_equivalentes():
    # «termina en a» con 2 estados y con 3 (uno redundante)
    a = Automata("ab", ["p", "q"], "p", ["q"], [("p", "a", "q"), ("p", "b", "p"), ("q", "a", "q"), ("q", "b", "p")])
    b = Automata("ab", ["x", "y", "z"], "x", ["y", "z"],
                 [("x", "a", "y"), ("x", "b", "x"), ("y", "a", "z"), ("y", "b", "x"), ("z", "a", "y"), ("z", "b", "x")])
    r = comparar_por_minimo(a, b)
    assert r.equivalentes and len(r.minimo_b.estados) == 2
    assert "SON EQUIVALENTES" in K.lineas_de_equivalencia(r)[1]


def test_el_isomorfismo_exige_afd():
    with pytest.raises(AutomataInvalido):
        isomorfismo(E.POR_NOMBRE["Ej_192_tabla"].fabrica(), E.POR_NOMBRE["Ej_192_tabla"].fabrica())


def test_minimizar_muestra_una_particion_por_ronda_hasta_estabilizarse():
    resultado = E.POR_NOMBRE["Ej_155_original"].fabrica().particiones()
    clases = [len(r) for r in resultado.rondas]
    assert clases == sorted(clases) and clases[0] == 2 and len(set(clases)) == len(clases)


# ---------------------------------------------------------------------------
# 2.5 Validación de varias cadenas
# ---------------------------------------------------------------------------

def test_leer_cadenas_ignora_lineas_en_blanco_y_entiende_lambda():
    assert K.leer_cadenas("01\n\n  10  \nλ\r\n0\n") == ["01", "10", "", "0"]
    assert K.leer_cadenas("") == []


def test_validar_lote_da_un_resultado_por_cadena_y_no_se_detiene_en_los_errores():
    a = E.POR_NOMBRE["Ej_263_figura"].fabrica()           # termina en 01
    cadenas = ["01", "101", "10", "", "012", "x"]
    resultados = K.validar_lote(a, cadenas)
    assert [w for w, _, _ in resultados] == cadenas
    assert [v for _, v, _ in resultados] == ["ACEPTADA", "ACEPTADA", "RECHAZADA", "RECHAZADA", "ERROR", "ERROR"]
    assert all(v == ("ACEPTADA" if a.acepta(w) else "RECHAZADA") for w, v, _ in resultados if v != "ERROR")
    assert "no pertenece al alfabeto" in resultados[4][2]


def test_informe_de_lote_resume_y_se_guarda(tmp_path, monkeypatch):
    monkeypatch.setattr(K, "CARPETA_SALIDAS", tmp_path / "salidas")
    monkeypatch.setattr(K, "RAIZ", tmp_path)
    a = E.POR_NOMBRE["Ej_263_figura"].fabrica()
    resultados = K.validar_lote(a, ["01", "10", "2"])
    texto = K.informe_de_lote(a, resultados, "cadenas.txt")
    assert "Total: 3. Aceptadas: 1. Rechazadas: 1. Con error: 1." in texto and "cadenas.txt" in texto
    ruta = K.guardar_informe(a, resultados, "informe", "cadenas.txt")
    assert ruta == "salidas/informe.txt" and (tmp_path / ruta).read_text(encoding="utf-8") == texto


def test_cargar_cadenas_desde_un_archivo(tmp_path):
    archivo = tmp_path / "cadenas.txt"
    archivo.write_text("﻿01\n10\n\nλ\n", encoding="utf-8")
    assert K.cargar_cadenas(str(archivo)) == ["01", "10", ""]
    with pytest.raises(Exception):
        K.cargar_cadenas(str(tmp_path / "no_existe.txt"))


def test_una_cadena_con_simbolo_ajeno_levanta_error_en_el_nucleo_pero_no_en_el_lote():
    a = E.POR_NOMBRE["Ej_263_figura"].fabrica()
    with pytest.raises(SimboloFueraDelAlfabeto):
        a.simular("2")
    assert K.validar_lote(a, ["2"])[0][1] == "ERROR"


# ---------------------------------------------------------------------------
# Archivos entregados en automatas/practica3/
# ---------------------------------------------------------------------------

import formatos as F  # noqa: E402
from pathlib import Path  # noqa: E402

CARPETA_P3 = Path(__file__).resolve().parent.parent / "automatas" / "practica3"


def test_los_casos_de_prueba_entregados_son_los_de_la_practica():
    nombres = sorted(p.stem for p in (CARPETA_P3 / "casos-de-prueba").glob("*.jff"))
    assert nombres == sorted(CASOS)


@pytest.mark.parametrize("ruta", sorted((CARPETA_P3 / "casos-de-prueba").glob("*.jff"))
                         + sorted((CARPETA_P3 / "afd-a-er").glob("*.jff")), ids=lambda p: p.stem)
def test_cada_jff_de_la_practica_3_reconoce_el_mismo_lenguaje_que_el_del_registro(ruta):
    del_archivo = F.leer_archivo(ruta, alfabeto=E.POR_NOMBRE[ruta.stem].fabrica().alfabeto)
    assert lenguajes_iguales(del_archivo, E.POR_NOMBRE[ruta.stem].fabrica())
