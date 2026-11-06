"""Pruebas de las expresiones regulares (src/expresiones.py) y de las cadenas de prueba del controlador."""

import itertools
import re

import pytest

import automata as A
import controlador as K
import ejercicios as E
import expresiones as X
from automata import Automata, formatear_conjunto
from test_automata import anexo3, par_de_ceros, termina_en_01

a, b, c = X.simbolo("a"), X.simbolo("b"), X.simbolo("c")


# ---------------------------------------------------------------------------
# Constructores y texto
# ---------------------------------------------------------------------------

def test_la_union_aplana_quita_repetidos_y_el_vacio():
    assert str(X.union(a, X.union(b, a), X.ER_VACIO)) == "a+b"
    assert X.union() == X.ER_VACIO and X.union(a) == a


def test_la_concatenacion_quita_lambda_y_el_vacio_la_anula():
    assert str(X.concat(a, X.ER_LAMBDA, b)) == "ab"
    assert X.concat(a, X.ER_VACIO, b) == X.ER_VACIO and X.concat() == X.ER_LAMBDA


def test_la_estrella_simplifica():
    assert X.estrella(X.ER_VACIO) == X.ER_LAMBDA and X.estrella(X.ER_LAMBDA) == X.ER_LAMBDA
    assert X.estrella(X.estrella(a)) == X.estrella(a)
    assert str(X.estrella(X.union(X.ER_LAMBDA, a))) == "a*"


@pytest.mark.parametrize("e, texto", [(X.union(a, b), "a+b"), (X.concat(a, b), "ab"), (X.estrella(X.union(a, b)), "(a+b)*"),
                                      (X.estrella(X.concat(a, b)), "(ab)*"), (X.concat(X.union(a, b), c), "(a+b)c"),
                                      (X.union(X.concat(a, b), c), "ab+c"), (X.ER_LAMBDA, "λ"), (X.ER_VACIO, "∅"),
                                      (X.concat(a, X.estrella(b)), "ab*")])
def test_la_notacion_del_curso(e, texto):
    assert str(e) == texto


def test_la_expresion_se_compara_con_cadenas():
    e = X.concat(X.estrella(X.union(a, b)), c)
    assert X.acepta(e, "abac") and X.acepta(e, "c") and not X.acepta(e, "abc c".replace(" ", "")[:2] + "a")
    assert X.acepta(X.ER_LAMBDA, "") and not X.acepta(X.ER_LAMBDA, "a") and not X.acepta(X.ER_VACIO, "")


# ---------------------------------------------------------------------------
# Eliminación de estados
# ---------------------------------------------------------------------------

def equivalente(automata, er, longitud):
    return all(automata.acepta(w) == X.acepta(er, w)
               for n in range(longitud + 1) for t in itertools.product(automata.alfabeto, repeat=n) for w in ["".join(t)])


@pytest.mark.parametrize("num", range(254, 259))
def test_la_expresion_obtenida_equivale_al_automata(num):
    automata = E.POR_NOMBRE[f"Ej_{num}_tabla"].fabrica()
    er, orden, pasos = X.desde_automata(automata)
    assert sorted(orden) == sorted(automata.estados) and len(pasos) == len(automata.estados)
    assert equivalente(automata, er, {2: 12, 3: 8}[len(automata.alfabeto)])


@pytest.mark.parametrize("fabrica", [par_de_ceros, anexo3, termina_en_01])
def test_funciona_con_afnd_y_con_transiciones_lambda(fabrica):
    automata = fabrica()
    er, _, _ = X.desde_automata(automata)
    assert equivalente(automata, er, 9)


def test_cualquier_orden_de_eliminacion_da_una_expresion_equivalente():
    automata = E.POR_NOMBRE["Ej_257_tabla"].fabrica()
    textos = set()
    for orden in itertools.permutations(automata.estados):
        er, _ = X.eliminar_en_orden(automata, list(orden))
        textos.add(str(er))
        assert equivalente(automata, er, 8)
    assert len(textos) > 1                                   # distintas formas, el mismo lenguaje


def test_un_automata_sin_estados_de_aceptacion_da_el_lenguaje_vacio():
    automata = Automata("a", ["q0"], "q0", [], [("q0", "a", "q0")])
    er, _, _ = X.desde_automata(automata)
    assert er == X.ER_VACIO


def test_las_expresiones_de_254_y_255_son_las_esperadas():
    er254, _, _ = X.desde_automata(E.POR_NOMBRE["Ej_254_tabla"].fabrica())
    assert all(X.acepta(er254, w) == w.endswith("1") for n in range(10) for t in itertools.product("01", repeat=n) for w in ["".join(t)])
    er255, _, _ = X.desde_automata(E.POR_NOMBRE["Ej_255_tabla"].fabrica())
    assert str(er255) == "((0+1)1*0)*"


# ---------------------------------------------------------------------------
# Cadenas de prueba y textos del controlador
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("nombre", ["Ej_099_afn_termina_en_001001", "Ej_190_afn_11010_y_10100", "Ej_151_original",
                                    "Ej_123_afn_forma_wxw", "Ej_196_tabla", "Ej_261_figura"])
def test_las_cadenas_de_prueba_son_cinco_validas_y_cinco_invalidas_de_distinta_longitud(nombre):
    automata = E.POR_NOMBRE[nombre].fabrica()
    automata.nombre = nombre
    buenas, malas = K.casos_de_prueba(automata)
    assert len(buenas) == 5 and len(malas) == 5
    assert all(automata.acepta(w) for w in buenas) and not any(automata.acepta(w) for w in malas)
    assert len({len(w) for w in buenas}) >= 3 and len({len(w) for w in malas}) >= 3
    assert (buenas, malas) == K.casos_de_prueba(automata)                   # siempre las mismas


def test_si_el_lenguaje_tiene_pocas_cadenas_se_devuelven_las_que_hay():
    for nombre, cuantas in (("Ej_158_figura", 1), ("Ej_262_ab_ba", 2)):
        automata = E.POR_NOMBRE[nombre].fabrica()
        automata.nombre = nombre
        buenas, malas = K.casos_de_prueba(automata)
        assert len(buenas) == cuantas and len(malas) == 5


def test_entre_las_invalidas_hay_una_con_la_que_el_automata_se_bloquea():
    automata = E.POR_NOMBRE["Ej_160_figura"].fabrica()
    automata.nombre = "Ej_160_figura"
    _, malas = K.casos_de_prueba(automata)
    assert any(not automata.simular(w).pasos[-1].conjunto for w in malas if w)


def test_traza_compacta_y_subconjuntos():
    afn = termina_en_01()
    assert K.traza_compacta(afn, afn.simular("101")) == "{q0} –1→ {q0} –0→ {q0, q1} –1→ {q0, q2}"
    conv = afn.a_afd()
    lineas = K.detalle_de_subconjuntos(afn, conv)
    assert lineas[0] == "δ'({q0}, 0) = δ(q0,0) = {q0, q1} = {q0, q1}" and len(lineas) == 2 * len(conv.afd.estados)
    assert any("δ(q0,1) ∪ δ(q2,1)" in x for x in lineas)
    assert K.trazas_de_subconjuntos(afn, {"q0"}, "01") == ["{q0}", "{q0, q1}", "{q0, q2}"]
    assert K.trazas_de_subconjuntos(anexo3(), {"q0"}, "") == [formatear_conjunto(("q0", "q1"))]


# ---------------------------------------------------------------------------
# Analizador de la notación del curso y ejercicios 201 a 240
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("texto, esperado", [("a + b*", "a+b*"), ("(a+b)*c", "(a+b)*c"), ("λa*b", "a*b"), ("(0 + (11 + 00)*)(11 + 10 + 01)*(λ + 110)",
                                                                                                             "(0+(11+00)*)(11+10+01)*(λ+110)"),
                                             ("a**", "a*"), ("(ab)*", "(ab)*"), ("∅", "∅"), ("λ", "λ")])
def test_parsear_y_volver_a_escribir(texto, esperado):
    assert str(X.parsear(texto)) == esperado


@pytest.mark.parametrize("texto", ["(a", "a)", "*a", "a+", "+a", "()", "a++b"])
def test_expresiones_mal_escritas(texto):
    with pytest.raises(X.ErrorDeSintaxis):
        X.parsear(texto)


def test_palabras_del_lenguaje():
    assert X.palabras(X.parsear("a*b"), 2) == ["b", "ab"]
    assert X.palabras(X.parsear("(a+b)*"), 1) == ["", "a", "b"]
    assert X.palabras(X.parsear("∅"), 3) == []


# V/F de los ejercicios 201 a 234, comprobadas a mano contra la definición de cada lenguaje (el 235 es falso: ∅ no es una cadena)
AFIRMACIONES = [
    ("a", "a+b", True), ("a", "ab", False), ("a", "a*+b*", True), ("a", "ab*", True), ("a", "a*b", False),
    ("ab", "a+b", False), ("ab", "ab", True), ("ab", "λa*b", True), ("ab", "∅a*b", False), ("ab", "(a+b)*", True),
    ("ab", "abc*", True), ("ab", "ab*c", False), ("ab", "ab*c*", True), ("ab", "(a+b+c)*", True), ("ab", "(abc)*", False),
    ("ab", "(ab)*c", False), ("ab", "a(bc)*", False), ("ab", "a(b+c)*", True), ("ab", "(a+b)*c", False), ("ab", "(a+b)*c*", True),
    ("aa", "a+b", False), ("aa", "a*+b*", True), ("aa", "a*b*", True), ("aa", "(a+b)*", True), ("aa", "a(a+b)*", True),
    ("", "a", False), ("", "(a+b)*", True), ("", "(a+b)*+a", True), ("", "∅", False), ("", "λ", True),
    ("", "λ+a", True), ("", "λa", False), ("", "ab*", False), ("", "(ab)*", True)]


@pytest.mark.parametrize("w, regex, esperado", AFIRMACIONES, ids=[f"{201 + i}" for i in range(len(AFIRMACIONES))])
def test_afirmaciones_201_a_234(w, regex, esperado):
    assert X.acepta(X.parsear(regex), w) is esperado


@pytest.mark.parametrize("regex, pertenece", [
    ("(0+1)*001(0+1)*", lambda w: "001" in w),
    ("(0+1)*010", lambda w: w.endswith("010")),
    ("(0+1)(0+1)(0+1)(λ+(0+1)(0+1))", lambda w: len(w) in (3, 5)),
    ("01(0+1)*+(0+1)*10", lambda w: w.startswith("01") or w.endswith("10")),
    ("((0+1)(0+1))*01((0+1)(0+1))*+(0+1)((0+1)(0+1))*01(0+1)((0+1)(0+1))*", lambda w: len(w) % 2 == 0 and "01" in w)],
    ids=["236", "237", "238", "239", "240"])
def test_expresiones_de_los_lenguajes_236_a_240(regex, pertenece):
    e = X.parsear(regex)
    assert all(X.acepta(e, w) == pertenece(w) for n in range(13) for t in itertools.product("01", repeat=n) for w in ["".join(t)])


@pytest.mark.parametrize("texto", ["(a", "a)", "*a", "a+", "+a", "()", "a++b"])
def test_los_mensajes_de_error_dan_la_posicion(texto):
    with pytest.raises(X.ErrorDeSintaxis) as info:
        X.parsear(texto)
    assert "posición" in str(info.value)


# ---------------------------------------------------------------------------
# Práctica 4: construcción de Thompson (expresión regular a AFN-λ)
# ---------------------------------------------------------------------------

def equivalente_con_automata(automata, e, longitud):
    return all(automata.acepta(w) == X.acepta(e, w)
               for n in range(longitud + 1) for t in itertools.product(automata.alfabeto, repeat=n) for w in ["".join(t)])


@pytest.mark.parametrize("texto", ["∅", "λ", "a", "a+b", "ab", "a*", "(a+b)*", "a*b", "(ab)*a",
                                   "(a+b)*abb", "a(ba)*+b", "(a+λ)(b+∅)"])
def test_desde_expresion_equivale_a_la_expresion(texto):
    e = X.parsear_sin_simplificar(texto)
    afn, pasos = X.desde_expresion(e, "ab")
    assert equivalente_con_automata(afn, e, 9)
    assert pasos[-1].automata is afn
    assert afn.estados == [f"q{i}" for i in range(len(afn.estados))]      # renombrado secuencial


def test_el_caso_base_vacio_no_tiene_ninguna_transicion():
    afn, pasos = X.desde_expresion(X.ER_VACIO, "a")
    assert len(afn.estados) == 2 and not afn.transiciones()
    assert pasos[0].caso.startswith("Caso básico ∅")


def test_el_caso_base_lambda_tiene_una_transicion_lambda():
    afn, pasos = X.desde_expresion(X.ER_LAMBDA, "a")
    assert afn.transiciones() == [(afn.inicial, "", [q for q in afn.estados if q != afn.inicial][0])]
    assert pasos[0].caso.startswith("Caso básico λ")


def test_cada_operador_del_texto_da_un_paso_de_construccion():
    # (a+b)*abb: a, b, union, estrella, a, b, b, concatenación final: 8 piezas.
    e = X.parsear_sin_simplificar("(a+b)*abb")
    _, pasos = X.desde_expresion(e, "ab")
    assert len(pasos) == 8
    assert [p.expresion for p in pasos] == ["a", "b", "a+b", "(a+b)*", "a", "b", "b", "(a+b)*abb"]


def test_la_estrella_no_reutiliza_el_inicio_ni_el_final_de_la_pieza():
    """Ejercicio 274 de la Lista 4: a diferencia del atajo (hacer final al inicio de la pieza y
    agregar una λ de vuelta desde su final), la construcción correcta usa dos estados nuevos."""
    pieza = X.simbolo("b")
    afn_pieza, _ = X.desde_expresion(pieza, "b")
    e = X.estrella(pieza)
    afn, pasos = X.desde_expresion(e, "b")
    paso_estrella = pasos[-1]
    assert len(paso_estrella.automata.estados) > len(afn_pieza.estados)   # dos estados de más


@pytest.mark.parametrize("nombre", [e.nombre for e in E.EXPRESIONES_LISTA4])
def test_las_expresiones_del_ejercicio_272_y_278_de_la_lista_4(nombre):
    """272(a-e) y 278: cada AFN-λ de Thompson, llevado por las tres etapas de la Práctica 3
    (quitar λ, subconjuntos, minimizar), reconoce el mismo lenguaje que la expresión."""
    entrega = E.POR_NOMBRE_EXPRESION[nombre]
    e = X.parsear_sin_simplificar(entrega.texto)
    afn_lambda, pasos = X.desde_expresion(e, entrega.alfabeto)
    afn = afn_lambda.quitar_lambda()
    afd = afn.a_afd(completo=True).afd
    minimo = afd.minimizar()
    assert equivalente_con_automata(minimo, e, 10)
    assert len(minimo.estados) <= len(afd.estados) <= len(afn.estados) <= len(afn_lambda.estados)


@pytest.mark.parametrize("cadena", E.CADENAS_273)
def test_ejercicio_273_cadenas_contra_272b_y_272c(cadena):
    """Verifica con el procesamiento por λ-clausuras (Automata.acepta, que hace la λ-clausura
    al inicio y después de cada símbolo) si 272(b) y 272(c) aceptan cada cadena."""
    afn_b, _ = X.desde_expresion(X.parsear_sin_simplificar("(ab)*a"), "ab")
    afn_c, _ = X.desde_expresion(X.parsear_sin_simplificar("(a+b)*abb"), "ab")
    assert afn_b.acepta(cadena) == bool(re.fullmatch(r"(ab)*a", cadena))
    assert afn_c.acepta(cadena) == bool(re.fullmatch(r"(?:[ab])*abb", cadena))


def test_los_cinco_autómatas_254_a_258_se_recuperan_con_desde_expresion():
    """Compara, para cada autómata de 254 a 258, su AFD mínimo con el de la expresión obtenida
    por eliminación de estados y reconstruida con Thompson: deben ser equivalentes (Ejercicio 3)."""
    for num in range(254, 259):
        original = E.POR_NOMBRE[f"Ej_{num}_tabla"].fabrica()
        er, _, _ = X.desde_automata(original)
        reconstruido, _ = X.desde_expresion(X.parsear_sin_simplificar(str(er)), original.alfabeto)
        resultado = A.comparar_por_minimo(original.minimizar(), reconstruido.quitar_lambda().a_afd().afd)
        assert resultado.equivalentes, (num, resultado.motivo)


@pytest.mark.parametrize("nombre", ["Ej_276_tabla", "Ej_277_tabla"])
def test_ejercicios_276_y_277_de_la_lista_4(nombre):
    """El AFD mínimo del original equivale al AFN-λ de Thompson construido con la expresión que
    obtiene desde_automata (eliminación de estados), reducido por las etapas de la Práctica 3."""
    original = E.POR_NOMBRE_LISTA4[nombre].fabrica()
    assert original.motivo_no_determinista() is None     # son AFD
    er, _, _ = X.desde_automata(original)
    reconstruido, _ = X.desde_expresion(X.parsear_sin_simplificar(str(er)), original.alfabeto)
    resultado = A.comparar_por_minimo(original.minimizar(), reconstruido.quitar_lambda().a_afd().afd)
    assert resultado.equivalentes, resultado.motivo


def test_parsear_sin_simplificar_conserva_la_union_con_vacio_y_lambda():
    """A diferencia de parsear(), que simplificaría (b+∅) a «b», parsear_sin_simplificar deja el
    árbol tal como se escribió: lo necesita desde_expresion para el ejercicio 272(e)."""
    simplificado = X.parsear("(a+λ)(b+∅)")
    crudo = X.parsear_sin_simplificar("(a+λ)(b+∅)")
    assert simplificado.tipo == "concat" and len(simplificado.valor) == 2
    assert simplificado.valor[1].tipo == "simbolo"              # ∅ ya se simplificó dentro de la unión
    assert crudo.valor[1].tipo == "union" and len(crudo.valor[1].valor) == 2   # b y ∅, intactos
    assert str(crudo) == "(a+λ)(b+∅)"                 # el texto conserva lo que se escribió
    assert str(simplificado) == "(a+λ)b"              # el simplificado ya perdió el «+∅»
