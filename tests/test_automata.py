"""Pruebas del núcleo de autómatas (src/automata.py).

Los autómatas de prueba son pequeños y su lenguaje se conoce, así que casi todas las
pruebas comparan contra la definición del lenguaje para todas las cadenas hasta cierta
longitud, en vez de unos pocos ejemplos.
"""

import re
from itertools import product

import pytest

import automata as A
from automata import Automata, AutomataInvalido, SimboloFueraDelAlfabeto
from lenguajes import LimiteExcedido


def cadenas(alfabeto, longitud_maxima):
    for n in range(longitud_maxima + 1):
        for t in product(alfabeto, repeat=n):
            yield "".join(t)


# ---------------------------------------------------------------------------
# Autómatas de prueba
# ---------------------------------------------------------------------------

def par_de_ceros():
    """AFD: cadenas de {0,1} con un número par de ceros."""
    return Automata("01", ["q0", "q1"], "q0", ["q0"],
                    [("q0", "0", "q1"), ("q0", "1", "q0"), ("q1", "0", "q0"), ("q1", "1", "q1")])


def anexo3():
    """AFND-λ del Anexo 3 del enunciado. Su lenguaje es b*(a + λ)."""
    return Automata("ab", ["q0", "q1"], "q0", ["q1"],
                    [("q0", "a", "q1"), ("q0", "b", "q0"), ("q0", "", "q1")])


def termina_en_01():
    """AFND (ejercicio 263): cadenas de {0,1} que terminan en 01."""
    return Automata("01", ["q0", "q1", "q2"], "q0", ["q2"],
                    [("q0", "0", "q0"), ("q0", "1", "q0"), ("q0", "0", "q1"), ("q1", "1", "q2")])


def cadena_de_lambdas():
    """AFND-λ: q0 –λ→ q1 –λ→ q2 (aceptación), q2 lee a y vuelve a q0 por λ (un ciclo de λ)."""
    return Automata("a", ["q0", "q1", "q2"], "q0", ["q2"],
                    [("q0", "", "q1"), ("q1", "", "q2"), ("q2", "a", "q2"), ("q2", "", "q0")])


def ejercicio_192():
    """AFN del ejercicio 192 de la Lista 3."""
    return Automata("01", ["A", "B", "C"], "A", ["C"],
                    [("A", "0", "B"), ("A", "1", "B"), ("A", "1", "C"),
                     ("B", "0", "A"), ("B", "0", "B"),
                     ("C", "0", "A"), ("C", "0", "C")])


def n_desde_el_final(n):
    """AFND de n+1 estados: el n-ésimo símbolo desde el final es 1."""
    a = Automata("01", [f"q{i}" for i in range(n + 1)], "q0", [f"q{n}"])
    a.agregar_transicion("q0", "0", "q0")
    a.agregar_transicion("q0", "1", "q0")
    a.agregar_transicion("q0", "1", "q1")
    for i in range(1, n):
        a.agregar_transicion(f"q{i}", "0", f"q{i + 1}")
        a.agregar_transicion(f"q{i}", "1", f"q{i + 1}")
    return a


def multiplos_de(k):
    """AFD de k estados: números binarios (bit más significativo primero) múltiplos de k."""
    a = Automata("01", [f"r{i}" for i in range(k)], "r0", ["r0"])
    for r in range(k):
        for bit in (0, 1):
            a.agregar_transicion(f"r{r}", str(bit), f"r{(2 * r + bit) % k}")
    return a


def valor(w):
    return int(w, 2) if w else 0


TODOS = [par_de_ceros, anexo3, termina_en_01, cadena_de_lambdas, ejercicio_192]


# ---------------------------------------------------------------------------
# Definición, edición y validación
# ---------------------------------------------------------------------------

def test_el_tipo_se_deduce_de_las_transiciones():
    assert par_de_ceros().tipo == "AFD"
    assert termina_en_01().tipo == "AFND"
    assert anexo3().tipo == "AFND-lambda"
    assert cadena_de_lambdas().tipo == "AFND-lambda"


def test_un_afd_parcial_sigue_siendo_afd_pero_no_es_completo():
    a = Automata("ab", ["q0", "q1"], "q0", ["q1"], [("q0", "a", "q1")])
    assert a.tipo == "AFD" and not a.es_completo()
    assert par_de_ceros().es_completo()
    assert not termina_en_01().es_completo()


def test_se_rechazan_definiciones_incorrectas():
    with pytest.raises(AutomataInvalido):
        Automata("aλ")                                  # λ no puede ser símbolo
    with pytest.raises(AutomataInvalido):
        Automata("ab")._validar_simbolo("ab")           # más de un carácter
    with pytest.raises(AutomataInvalido):
        Automata("aa")                                  # símbolo repetido
    with pytest.raises(AutomataInvalido):
        Automata("a", ["q0", "q0"])                     # estado repetido
    with pytest.raises(AutomataInvalido):
        Automata("a", [""])                             # nombre vacío
    with pytest.raises(AutomataInvalido):
        Automata("a", ["q0"], "q9")                     # inicial inexistente
    with pytest.raises(AutomataInvalido):
        Automata("a", ["q0"], "q0", ["q9"])             # aceptación inexistente
    with pytest.raises(AutomataInvalido):
        Automata("a", ["q0"], "q0", [], [("q0", "b", "q0")])   # símbolo fuera del alfabeto
    with pytest.raises(AutomataInvalido):
        Automata("a", ["q0"], "q0", [], [("q0", "a", "q9")])   # destino inexistente


def test_validar_senala_lo_que_falta_y_no_se_simula_sin_inicial():
    a = Automata("ab", ["q0"])
    assert "Falta el estado inicial." in a.validar()
    with pytest.raises(AutomataInvalido):
        a.acepta("a")
    assert Automata().validar()                       # vacío: alfabeto, estados e inicial
    assert par_de_ceros().validar() == []


def test_quitar_un_estado_quita_sus_transiciones_y_su_papel():
    a = termina_en_01()
    a.quitar_estado("q1")
    assert a.estados == ["q0", "q2"]
    assert all("q1" not in (d, h) for d, _, h in a.transiciones())
    a.quitar_estado("q0")
    assert a.inicial is None


def test_renombrar_un_estado_conserva_el_autómata():
    a, b = par_de_ceros(), par_de_ceros()
    b.renombrar_estado("q1", "impar")
    assert b.estados == ["q0", "impar"]
    assert ("q0", "0", "impar") in b.transiciones()
    assert A.lenguajes_iguales(a, b)
    with pytest.raises(AutomataInvalido):
        b.renombrar_estado("impar", "q0")


def test_quitar_un_simbolo_quita_sus_transiciones():
    a = par_de_ceros()
    a.quitar_simbolo("1")
    assert a.alfabeto == ["0"] and all(lee == "0" for _, lee, _ in a.transiciones())


def test_la_igualdad_no_depende_del_orden_ni_del_nombre():
    a = par_de_ceros()
    b = Automata("10", ["q1", "q0"], "q0", ["q0"],
                 [("q1", "1", "q1"), ("q1", "0", "q0"), ("q0", "1", "q0"), ("q0", "0", "q1")], "otro nombre")
    assert a == b
    b.marcar_aceptacion("q1")
    assert a != b


def test_la_tabla_incluye_la_columna_lambda_solo_si_hay_transiciones_lambda():
    columnas, filas = par_de_ceros().tabla()
    assert columnas == ["0", "1"]
    columnas, filas = anexo3().tabla()
    assert columnas == ["", "a", "b"]
    assert dict(filas)["q0"][""] == ("q1",)


# ---------------------------------------------------------------------------
# Aceptación y rechazo en un AFD
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("w", ["", "1", "11", "00", "0110", "1001", "0101010"])
def test_el_afd_acepta_las_cadenas_con_numero_par_de_ceros(w):
    assert par_de_ceros().acepta(w)


@pytest.mark.parametrize("w", ["0", "10", "01", "000", "0111", "1011", "0010111"])
def test_el_afd_rechaza_las_cadenas_con_numero_impar_de_ceros(w):
    assert not par_de_ceros().acepta(w)


def test_el_afd_coincide_con_la_definicion_en_todas_las_cadenas_hasta_longitud_10():
    a = par_de_ceros()
    assert all(a.acepta(w) == (w.count("0") % 2 == 0) for w in cadenas("01", 10))


def test_un_afd_parcial_rechaza_al_faltar_la_transicion():
    a = Automata("ab", ["q0", "q1"], "q0", ["q1"], [("q0", "a", "q1")])
    assert a.acepta("a")
    assert not a.acepta("b") and not a.acepta("aa") and not a.acepta("")


def test_los_simbolos_fuera_del_alfabeto_y_las_cadenas_enormes_se_rechazan_con_error():
    a = par_de_ceros()
    with pytest.raises(SimboloFueraDelAlfabeto):
        a.acepta("012")
    with pytest.raises(SimboloFueraDelAlfabeto):
        a.acepta("λ")
    with pytest.raises(LimiteExcedido):
        a.acepta("0" * 1_001)
    with pytest.raises(ValueError):
        a.acepta(None)


# ---------------------------------------------------------------------------
# AFND-λ: la aceptación requiere la λ-clausura
# ---------------------------------------------------------------------------

def test_las_clausuras_lambda_de_cada_estado():
    assert anexo3().clausuras() == {"q0": ("q0", "q1"), "q1": ("q1",)}
    # la clausura es transitiva y termina aunque haya un ciclo de λ
    assert cadena_de_lambdas().clausuras() == {"q0": ("q0", "q1", "q2"), "q1": ("q0", "q1", "q2"),
                                              "q2": ("q0", "q1", "q2")}


def test_la_clausura_de_un_conjunto_es_la_union_de_las_clausuras():
    a = anexo3()
    assert a.clausura({"q1"}) == frozenset({"q1"})
    assert a.clausura({"q0", "q1"}) == frozenset({"q0", "q1"})
    assert a.clausura(set()) == frozenset()
    with pytest.raises(AutomataInvalido):
        a.clausura({"q9"})


def test_la_cadena_vacia_se_acepta_solo_gracias_a_la_clausura():
    a = anexo3()
    assert "q0" not in a.aceptacion                   # el inicial no es de aceptación...
    assert a.acepta("")                               # ...pero q1 sí, y está en Cl({q0}) por la λ
    sin_lambda = anexo3()
    sin_lambda.quitar_transicion("q0", "", "q1")
    assert not sin_lambda.acepta("")                  # sin la transición λ, la cadena vacía se rechaza


def test_la_clausura_tambien_se_aplica_despues_de_leer_un_simbolo():
    """Tras leer b se está en q0, y la λ lleva a q1 (aceptación): 'b' y 'bb' se aceptan."""
    a = anexo3()
    assert a.acepta("b") and a.acepta("bbb") and a.acepta("bba")
    assert not a.acepta("ab") and not a.acepta("aa")


def test_el_afnd_lambda_coincide_con_su_lenguaje_en_todas_las_cadenas_hasta_longitud_10():
    a = anexo3()
    assert all(a.acepta(w) == (re.fullmatch("b*a?", w) is not None) for w in cadenas("ab", 10))


def test_un_ciclo_de_lambdas_no_cuelga_la_simulacion():
    a = cadena_de_lambdas()
    assert all(a.acepta(w) for w in cadenas("a", 6))   # lenguaje a*, con cadena vacía
    assert a.simular("aaa").aceptada
    assert a.caminos("aa").caminos                      # termina y devuelve caminos


def test_el_afnd_acepta_si_algun_camino_acepta():
    a = termina_en_01()
    assert all(a.acepta(w) == w.endswith("01") for w in cadenas("01", 11))


# ---------------------------------------------------------------------------
# δ̂ y recorrido paso a paso
# ---------------------------------------------------------------------------

def test_delta_hat_del_ejercicio_192():
    a = ejercicio_192()
    assert a.delta_hat({"A"}, "0111") == frozenset()          # inciso a) de la Lista 3
    assert a.delta_hat({"B", "C"}, "010111") == frozenset()   # inciso b)
    assert a.delta_hat({"A"}, "0") == frozenset({"B"})
    assert a.delta_hat({"A"}, "10") == frozenset({"A", "B", "C"})
    assert a.delta_hat({"B", "C"}, "01") == frozenset({"B", "C"})
    assert a.delta_hat({"A"}, "") == frozenset({"A"})


def test_delta_hat_incluye_la_clausura():
    assert anexo3().delta_hat({"q0"}, "") == frozenset({"q0", "q1"})
    assert anexo3().delta_hat({"q0"}, "b") == frozenset({"q0", "q1"})


def test_el_recorrido_tiene_un_paso_por_simbolo_mas_el_inicial():
    r = anexo3().simular("ba")
    assert [p.simbolo for p in r.pasos] == [None, "b", "a"]
    assert r.pasos[0].tomadas == (("q0", "", "q1"),)                 # la λ del inicio
    assert r.pasos[0].conjunto == frozenset({"q0", "q1"})
    assert ("q0", "b", "q0") in r.pasos[1].tomadas and ("q0", "", "q1") in r.pasos[1].tomadas
    assert r.pasos[2].conjunto == frozenset({"q1"})
    assert r.aceptada and r.consumida


def test_el_recorrido_indica_cuando_el_automata_se_bloquea():
    r = anexo3().simular("aab")
    assert not r.aceptada and not r.consumida                       # se bloquea al leer la segunda a
    assert r.pasos[-1].conjunto == frozenset()
    r = anexo3().simular("ab")
    assert not r.aceptada and r.consumida                           # se vacía justo al leer la última


def test_el_texto_del_recorrido_explica_el_resultado():
    a = anexo3()
    texto = a.simular("ba").texto(a.estados)
    assert "ACEPTADA" in texto and "q0 –b→ q0" in texto and "q0 –λ→ q1" in texto
    texto = a.simular("aab").texto(a.estados)
    assert "RECHAZADA" in texto and "se bloqueó" in texto
    assert "λ (0 símbolos)" in a.simular("").texto(a.estados)


@pytest.mark.parametrize("fabrica", TODOS)
def test_simular_y_acepta_siempre_coinciden(fabrica):
    a = fabrica()
    assert all(a.simular(w).aceptada == a.acepta(w) for w in cadenas(a.alfabeto, 7))


# ---------------------------------------------------------------------------
# Caminos múltiples
# ---------------------------------------------------------------------------

def test_dos_caminos_para_la_misma_cadena():
    a = Automata("0", ["q0", "q1", "q2"], "q0", ["q1", "q2"], [("q0", "0", "q1"), ("q0", "0", "q2")])
    r = a.caminos("0")
    assert len(r.caminos) == 2 and all(c.aceptado for c in r.caminos) and not r.truncado


def test_en_un_afnd_hay_ramas_que_mueren_y_una_que_acepta():
    a = termina_en_01()
    r = a.caminos("0101")
    assert sum(c.aceptado for c in r.caminos) == 1
    assert any("se bloquea" in c.motivo for c in r.caminos)
    assert any("no es de aceptación" in c.motivo for c in r.caminos)


@pytest.mark.parametrize("fabrica", TODOS)
def test_hay_un_camino_que_acepta_exactamente_cuando_el_autómata_acepta(fabrica):
    a = fabrica()
    assert all(any(c.aceptado for c in a.caminos(w).caminos) == a.acepta(w) for w in cadenas(a.alfabeto, 6))


def test_la_enumeracion_de_caminos_se_corta_en_el_limite():
    r = termina_en_01().caminos("0" * 12, limite=3)
    assert r.truncado and len(r.caminos) == 3


# ---------------------------------------------------------------------------
# Conversiones
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fabrica", TODOS)
def test_quitar_lambda_conserva_el_lenguaje_y_elimina_las_transiciones_lambda(fabrica):
    original = fabrica()
    sin = original.quitar_lambda()
    assert not sin.tiene_lambda and sin.estados == original.estados
    assert A.lenguajes_iguales(original, sin)
    assert all(sin.acepta(w) == original.acepta(w) for w in cadenas(original.alfabeto, 7))


@pytest.mark.parametrize("fabrica", TODOS)
def test_el_afd_equivalente_acepta_las_mismas_cadenas(fabrica):
    original = fabrica()
    afd = original.a_afd().afd
    assert afd.tipo == "AFD"
    assert all(afd.acepta(w) == original.acepta(w) for w in cadenas(original.alfabeto, 8))
    assert A.lenguajes_iguales(original, afd)


def test_la_construccion_de_subconjuntos_del_ejercicio_263():
    conv = termina_en_01().a_afd()
    assert conv.subconjuntos == {"{q0}": frozenset({"q0"}), "{q0,q1}": frozenset({"q0", "q1"}),
                                 "{q0,q2}": frozenset({"q0", "q2"})}
    afd = conv.afd
    assert afd.inicial == "{q0}" and afd.aceptacion == frozenset({"{q0,q2}"})
    assert ("{q0,q1}", "1", "{q0,q2}") in afd.transiciones()


def test_el_inicio_del_afd_es_la_clausura_del_inicial_del_afnd_lambda():
    conv = anexo3().a_afd()
    assert conv.afd.inicial == "{q0,q1}"
    assert conv.afd.es_aceptacion("{q0,q1}")             # por eso se acepta la cadena vacía


def test_el_conjunto_vacio_solo_aparece_si_se_pide_el_afd_completo():
    parcial = anexo3().a_afd().afd
    completo = anexo3().a_afd(completo=True).afd
    assert A.NOMBRE_VACIO not in parcial.estados and not parcial.es_completo()
    assert A.NOMBRE_VACIO in completo.estados and completo.es_completo()
    assert A.lenguajes_iguales(parcial, completo)


def test_la_conversion_se_rechaza_si_el_afd_seria_enorme(monkeypatch):
    monkeypatch.setattr(A, "LIMITE_ESTADOS_AFD", 10)
    with pytest.raises(LimiteExcedido):
        n_desde_el_final(6).a_afd()


# ---------------------------------------------------------------------------
# La cota 2^n y la minimización
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_la_cota_2_a_la_n_se_alcanza_en_el_n_esimo_simbolo_desde_el_final(n):
    """Familia de la bibliografía: el AFND tiene n+1 estados y el AFD mínimo, 2^n."""
    afnd = n_desde_el_final(n)
    assert len(afnd.estados) == n + 1
    assert all(afnd.acepta(w) == (len(w) >= n and w[-n] == "1") for w in cadenas("01", 9))
    minimo = afnd.a_afd().afd.minimizar()
    assert len(minimo.estados) == 2 ** n


def test_el_afd_de_termina_en_01_no_crece_mas_que_el_afnd():
    assert len(termina_en_01().a_afd().afd.estados) == 3 == len(termina_en_01().estados)


@pytest.mark.parametrize("k, esperados", [(2, 2), (3, 3), (5, 5), (6, 4), (7, 7)])
def test_minimizar_multiplos_de_k(k, esperados):
    """Los múltiplos de 6 necesitan solo 4 estados (el residuo módulo 6 repite comportamiento)."""
    a = multiplos_de(k)
    minimo = a.minimizar()
    assert len(minimo.estados) == esperados
    assert A.lenguajes_iguales(a, minimo)
    assert all(minimo.acepta(format(n, "b")) == (n % k == 0) for n in range(1, 200))


def test_minimizar_quita_los_inaccesibles_y_fusiona_equivalentes():
    a = Automata("01", ["A", "B", "C", "X"], "A", ["C"],
                 [("A", "0", "B"), ("A", "1", "C"), ("B", "0", "A"), ("B", "1", "C"),
                  ("C", "0", "C"), ("C", "1", "C"), ("X", "0", "A"), ("X", "1", "X")])
    assert a.accesibles() == ("A", "B", "C")
    assert "X" not in a.quitar_inaccesibles().estados
    minimo = a.minimizar()
    assert sorted(minimo.estados) == ["C", "{A,B}"]
    assert A.lenguajes_iguales(a, minimo)


def test_minimizar_un_afd_parcial_devuelve_un_afd_parcial():
    a = Automata("ab", ["q0", "q1", "q2", "q3"], "q0", ["q2", "q3"],
                 [("q0", "a", "q1"), ("q0", "b", "q1"), ("q1", "a", "q2"), ("q1", "b", "q3")])
    minimo = a.minimizar()
    assert len(minimo.estados) == 3 and not minimo.es_completo()
    assert A.NOMBRE_VACIO not in minimo.estados
    assert A.lenguajes_iguales(a, minimo)


def test_particiones_empiezan_separando_la_aceptacion_y_terminan_en_el_minimo():
    r = multiplos_de(6).particiones()
    assert len(r.rondas[0]) == 2 and len(r.rondas[-1]) == 4 and r.trampa is None
    assert [len(x) for x in r.rondas] == sorted(len(x) for x in r.rondas)
    assert set().union(*[set(c) for c in r.rondas[-1]]) == set(multiplos_de(6).estados)


def test_el_lenguaje_vacio_se_minimiza_a_un_solo_estado():
    a = Automata("a", ["q0", "q1"], "q0", [], [("q0", "a", "q1"), ("q1", "a", "q0")])
    assert len(a.minimizar().estados) == 1


def test_solo_se_minimiza_un_afd():
    with pytest.raises(AutomataInvalido):
        termina_en_01().minimizar()
    with pytest.raises(AutomataInvalido):
        anexo3().particiones()


# ---------------------------------------------------------------------------
# Comparación de lenguajes
# ---------------------------------------------------------------------------

def test_cadena_distintiva_es_la_mas_corta_que_distingue_a_dos_autómatas():
    termina_01, termina_11 = termina_en_01(), n_desde_el_final(2)
    w = A.cadena_distintiva(termina_01, termina_11)
    assert w is not None and termina_01.acepta(w) != termina_11.acepta(w)
    assert all(termina_01.acepta(x) == termina_11.acepta(x) for x in cadenas("01", len(w) - 1))


def test_dos_formas_del_mismo_lenguaje_son_iguales_y_se_distinguen_de_otro():
    assert A.lenguajes_iguales(termina_en_01(), termina_en_01().a_afd().afd)
    assert not A.lenguajes_iguales(par_de_ceros(), anexo3())
    assert A.cadena_distintiva(par_de_ceros(), par_de_ceros()) is None
