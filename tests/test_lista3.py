"""Verifica los autómatas de la Lista 3 (src/ejercicios.py) y los archivos entregados en automatas/.

Los diseños propios se prueban contra el lenguaje del enunciado (predicados independientes), los AFN de la
Lista 2 contra el AFD ya entregado con una comparación exacta, las conversiones contra su AFN, y las respuestas de
los ejercicios 196 a 200 contra valores calculados a mano."""

import importlib.util
import itertools
from pathlib import Path

import pytest

import automata as A
import construcciones as C
import controlador as K
import ejercicios as E
import formatos as F
from automata import Automata

RAIZ = Path(__file__).resolve().parent.parent
LONGITUD = {2: 11, 3: 7}


def referencia(nombre):
    a = E.POR_NOMBRE[nombre].fabrica()
    a.nombre = nombre
    return a


def lista2(numero):
    return F.leer_archivo(next((RAIZ / "automatas" / "lista2-afd").glob(f"Ej_{numero}_*.jff")))


# ---------------------------------------------------------------------------
# El registro
# ---------------------------------------------------------------------------

def test_cantidad_de_autómatas_por_carpeta():
    cuenta = {}
    for e in E.ENTREGAS:
        cuenta[e.carpeta] = cuenta.get(e.carpeta, 0) + 1
    assert cuenta == {"lista3-afd": 4 + 7 + 7 + 2 + 5 + 1, "lista3-afnd": 7 + 2 + 7, "lista3-afnd-lambda": 5,
                      "conversiones": 17 + 10}
    assert len(E.ENTREGAS) == 74


def test_cada_autómata_se_construye_y_esta_completamente_definido():
    for e in E.ENTREGAS:
        a = e.fabrica()
        assert a.validar() == [], e.nombre
        assert a.inicial in a.estados and a.aceptacion <= set(a.estados), e.nombre


@pytest.mark.parametrize("nombre", [e.nombre for e in E.ENTREGAS if e.pertenece])
def test_el_diseño_reconoce_el_lenguaje_del_enunciado(nombre):
    e = E.POR_NOMBRE[nombre]
    a = referencia(nombre)
    alfabeto = e.alfabeto or "".join(a.alfabeto)
    for n in range(LONGITUD[len(alfabeto)] + 1):
        for t in itertools.product(alfabeto, repeat=n):
            w = "".join(t)
            assert a.acepta(w) == bool(e.pertenece(w)), f"{nombre}: {w!r}"


@pytest.mark.parametrize("numero, nombre", [("099", "Ej_099_afn_termina_en_001001"), ("102", "Ej_102_afn_contiene_abbbab"),
                                            ("103", "Ej_103_afn_contiene_aabbba"), ("106", "Ej_106_afn_contiene_1101001"),
                                            ("118", "Ej_118_afn_forma_axabya"), ("120", "Ej_120_afn_primer_y_ultimo_distintos"),
                                            ("123", "Ej_123_afn_forma_wxw")])
def test_el_afn_equivale_exactamente_al_afd_de_la_lista_2_y_es_mas_simple(numero, nombre):
    afn, afd = referencia(nombre), lista2(numero)
    assert afn.tipo == "AFND" and A.lenguajes_iguales(afn, afd)
    assert len(afn.estados) <= len(afd.estados)
    assert len(afn.transiciones()) < len(afd.transiciones())            # el diagrama es más simple


def test_los_ejercicios_que_reutilizan_el_afd_estan_en_la_lista_2():
    for numero in E.AFD_COMO_AFN:
        assert lista2(f"{int(numero):03d}").tipo == "AFD"


def test_el_afn_de_190_equivale_al_afd_por_producto_de_los_dos_patrones():
    assert A.lenguajes_iguales(referencia("Ej_190_afn_11010_y_10100"), C.afd_contiene_todos(["11010", "10100"], "01"))
    assert len(C.afd_contiene_todos(["11010", "10100"], "01").estados) == 19


def test_el_diagrama_de_la_palabra_de_189_y_190_tiene_los_caminos_esperados():
    a = referencia("Ej_189_afn_00101_o_00110")
    r = a.caminos("1001011")
    assert len(r.caminos) == 4 and sum(c.aceptado for c in r.caminos) == 1
    b = referencia("Ej_190_afn_11010_y_10100")
    assert b.acepta("01101010100") and any(c.aceptado for c in b.caminos("01101010100").caminos)


def test_los_traslapes_de_190_estan_cubiertos():
    a = referencia("Ej_190_afn_11010_y_10100")
    assert a.acepta("110100") and a.acepta("11010100") and a.acepta("1101010100")     # los dos traslapes y sin traslape
    assert not a.acepta("11010") and not a.acepta("10100") and not a.acepta("1101")


# ---------------------------------------------------------------------------
# 151 a 157: simplificación
# ---------------------------------------------------------------------------

INACCESIBLES = {"151": [], "152": [], "153": [], "154": ["J"], "155": ["I", "L"], "156": [], "157": []}
MINIMOS = {"151": 5, "152": 5, "153": 6, "154": 7, "155": 5, "156": 3, "157": 4}


@pytest.mark.parametrize("numero", list(INACCESIBLES))
def test_estados_inaccesibles_y_minimo_de_cada_tabla(numero):
    original = referencia(f"Ej_{numero}_original")
    assert [q for q in original.estados if q not in original.accesibles()] == INACCESIBLES[numero]
    minimo = referencia(f"Ej_{numero}_minimo")
    assert len(minimo.estados) == MINIMOS[numero] and A.lenguajes_iguales(original, minimo)
    assert original.es_completo() and original.tipo == "AFD"
    if INACCESIBLES[numero]:
        sin = referencia(f"Ej_{numero}_sin_inaccesibles")
        assert len(sin.estados) == len(original.estados) - len(INACCESIBLES[numero])
        assert A.lenguajes_iguales(original, sin)
    else:
        assert f"Ej_{numero}_sin_inaccesibles" not in E.POR_NOMBRE


def test_en_156_los_estados_equivalentes_son_a_c_y_b_d():
    r = referencia("Ej_156_original").particiones()
    assert [sorted(c) for c in r.rondas[-1]] == [["A", "C"], ["B", "D"], ["E"]]
    assert [len(x) for x in r.rondas] == [2, 3]


def test_en_157_b_c_d_son_equivalentes():
    r = referencia("Ej_157_original").particiones()
    assert sorted(map(sorted, r.rondas[-1])) == [["A"], ["B", "C", "D"], ["E"], ["F"]]


def test_las_tablas_transcritas_tienen_todas_las_transiciones_del_enunciado():
    assert len(referencia("Ej_151_original").transiciones()) == 20 and len(referencia("Ej_152_original").transiciones()) == 18
    assert len(referencia("Ej_155_original").transiciones()) == 24
    t151 = referencia("Ej_151_original")
    assert t151.destinos("A", "0") == ("C",) and t151.destinos("A", "1") == ("E",) and t151.aceptacion == frozenset("CEF")


# ---------------------------------------------------------------------------
# Conversiones
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("nombre", E.CONVERSIONES_AFN)
def test_el_afd_de_cada_conversion_equivale_a_su_afn(nombre):
    num = nombre.split("_")[1]
    afn, afd = referencia(nombre), referencia(f"Ej_{num}_afd")
    assert afd.tipo == "AFD" and A.lenguajes_iguales(afn, afd)
    assert len(afd.estados) <= 2 ** len(afn.estados)
    if num != "262":
        assert not afd.es_completo() or A.NOMBRE_VACIO not in afd.estados


def test_tamanos_de_las_conversiones_que_aparecen_en_la_tabla_2_4():
    esperados = {"099": (7, 7), "102": (7, 12), "103": (7, 12), "106": (8, 14), "118": (5, 5), "120": (5, 7), "123": (12, 15),
                 "189": (8, 24), "190": (21, 48), "192": (3, 5), "193": (4, 7), "194": (4, 4), "195": (5, 12), "260": (5, 7),
                 "261": (5, 5), "262": (4, 5), "263": (3, 3)}
    for nombre in E.CONVERSIONES_AFN:
        num = nombre.split("_")[1]
        assert (len(referencia(nombre).estados), len(referencia(f"Ej_{num}_afd").estados)) == esperados[num], num


def test_el_afn_de_263_y_261_aceptan_las_cadenas_que_terminan_en_01_y_00():
    assert referencia("Ej_263_figura").acepta("1101") and not referencia("Ej_263_figura").acepta("10")
    assert referencia("Ej_261_figura").acepta("1100") and not referencia("Ej_261_figura").acepta("0011")
    assert A.NOMBRE_VACIO in referencia("Ej_262_afd").estados                       # se completó con el estado ∅


def test_en_262_el_afn_es_determinista_y_solo_acepta_ab_y_ba():
    a = referencia("Ej_262_ab_ba")
    assert a.tipo == "AFD" and {w for n in range(5) for w in map("".join, itertools.product("ab", repeat=n)) if a.acepta(w)} == {"ab", "ba"}


@pytest.mark.parametrize("num", ["196", "197", "198", "199", "200"])
def test_la_conversion_de_un_afnd_lambda_pasa_por_un_afnd_sin_lambda(num):
    lam, sin, afd = referencia(f"Ej_{num}_tabla"), referencia(f"Ej_{num}_afnd"), referencia(f"Ej_{num}_afd")
    assert lam.tipo == "AFND-lambda" and not sin.tiene_lambda and afd.tipo == "AFD"
    assert sin.estados == lam.estados
    assert A.lenguajes_iguales(lam, sin) and A.lenguajes_iguales(sin, afd)


# ---------------------------------------------------------------------------
# Respuestas a las preguntas (192 a 200)
# ---------------------------------------------------------------------------

def conjunto(texto):
    return frozenset(texto)


# calculados a mano a partir de las tablas del enunciado
A_MANO = {
    "196": {"a": "", "b": "AB", "c": "B", "d": "AB", "e": "A"},
    "197": {"a": "ABCD", "b": "BD", "c": "ABCD", "d": "BD", "e": "ABCD"},
    "198": {"a": "ABC", "b": "BCD", "c": "ABCD", "e": "BCD"},
    "199": {"a": "ABCE", "b": "CE", "c": "D"},
    "200": {"a": "AB", "b": "CDEF", "c": "ABCDEF"},
    "192": {"a": "", "b": ""},
}


@pytest.mark.parametrize("num", list(A_MANO))
def test_respuestas_calculadas_a_mano(num):
    a = referencia(f"Ej_{num}_tabla")
    for inciso, consulta in E.CONSULTAS[num]:
        assert E.responder(a, consulta) == conjunto(A_MANO[num][inciso]), f"{num} {inciso}"


@pytest.mark.parametrize("num", ["192", "193", "194", "195"])
def test_delta_hat_del_afn_y_delta_hat_d_del_afd_coinciden(num):
    afn = referencia(f"Ej_{num}_tabla")
    for inciso, consulta in E.CONSULTAS[num]:
        _, Z, w = consulta
        recorrido = K.trazas_de_subconjuntos(afn, set(Z), w)
        assert recorrido[-1] == A.formatear_conjunto(afn._ordenar(E.responder(afn, consulta)))
        assert len(recorrido) == len(w) + 1


def test_todas_las_consultas_del_enunciado_estan_en_el_registro():
    assert {k: len(v) for k, v in E.CONSULTAS.items()} == {"192": 2, "193": 3, "194": 4, "195": 4, "196": 5, "197": 5,
                                                          "198": 4, "199": 3, "200": 3}


def test_clausuras_de_196_a_200():
    a = referencia("Ej_197_tabla")
    assert a.clausuras() == {"A": ("A", "B", "C", "D"), "B": ("B", "D"), "C": ("B", "C", "D"), "D": ("D",)}
    assert referencia("Ej_200_tabla").clausuras()["D"] == ("D", "E", "F")


# ---------------------------------------------------------------------------
# Los archivos entregados (también los que se dibujen en JFLAP)
# ---------------------------------------------------------------------------

CARPETAS = ["lista3-afd", "lista3-afnd", "lista3-afnd-lambda", "conversiones"]
ENTREGADOS = sorted(p for c in CARPETAS for p in (RAIZ / "automatas" / c).glob("*.jff"))


@pytest.mark.parametrize("ruta", ENTREGADOS, ids=[f"{p.parent.name}/{p.stem}" for p in ENTREGADOS])
def test_cada_jff_entregado_reconoce_el_lenguaje_de_su_ejercicio(ruta):
    assert ruta.stem in E.POR_NOMBRE, "el nombre del archivo no corresponde a ningún ejercicio"
    assert E.POR_NOMBRE[ruta.stem].carpeta == ruta.parent.name, "el archivo está en la carpeta equivocada"
    tuyo = F.leer_archivo(ruta)
    esperado = referencia(ruta.stem)
    distintiva = A.cadena_distintiva(tuyo, esperado)
    assert distintiva is None, f"con {distintiva!r} no coincide"
    assert A.TIPOS.index(tuyo.tipo) <= A.TIPOS.index(esperado.tipo), f"es un {tuyo.tipo} y debería ser un {esperado.tipo}"


def test_estan_todos_los_archivos_del_registro():
    esperados = {f"{e.carpeta}/{e.nombre}.jff" for e in E.ENTREGAS}
    hay = {f"{p.parent.name}/{p.name}" for p in ENTREGADOS}
    assert esperados == hay


# ---------------------------------------------------------------------------
# El verificador de herramientas/verificar_entregas.py
# ---------------------------------------------------------------------------

def cargar_verificador():
    spec = importlib.util.spec_from_file_location("verificar_entregas", RAIZ / "herramientas" / "verificar_entregas.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_el_verificador_acepta_un_dibujo_correcto_y_senala_uno_incorrecto(tmp_path):
    v = cargar_verificador()
    bueno = tmp_path / "Ej_263_figura.jff"
    F.guardar_archivo(referencia("Ej_263_figura"), bueno)
    assert v.revisar(bueno, False)[0] == "OK"
    malo = referencia("Ej_263_figura")
    malo.quitar_transicion("q1", "1", "q2")                      # falta la transición que cierra el patrón 01
    ruta = tmp_path / "Ej_263_figura.jff"
    F.guardar_archivo(malo, ruta)
    estado, mensaje = v.revisar(ruta, False)
    assert estado == "MAL" and "no reconoce el mismo lenguaje" in mensaje and "'01'" in mensaje


def test_el_verificador_avisa_de_nombres_desconocidos_tipos_y_tamanos(tmp_path):
    v = cargar_verificador()
    ruta = tmp_path / "mi_dibujo.jff"
    F.guardar_archivo(referencia("Ej_263_figura"), ruta)
    assert v.revisar(ruta, False)[0] == "AVISO" and "ningún ejercicio" in v.revisar(ruta, False)[1]
    ruta = tmp_path / "Ej_139_original.jff"
    F.guardar_archivo(referencia("Ej_263_figura"), ruta)
    assert v.revisar(ruta, False)[0] == "AVISO" or v.revisar(ruta, False)[0] == "OK"
    # un AFD esperado que se dibujó con una transición no determinista pero el mismo lenguaje
    dibujo = referencia("Ej_262_ab_ba")
    dibujo.agregar_estado("extra")
    dibujo.agregar_transicion("q0", "a", "extra")
    ruta = tmp_path / "Ej_262_ab_ba.jff"
    F.guardar_archivo(dibujo, ruta)
    estado, mensaje = v.revisar(ruta, False)
    assert estado == "AVISO" and "AFND" in mensaje and "5 estados" in mensaje


def test_el_verificador_escribe_el_json_y_el_xml_de_un_dibujo_correcto(tmp_path):
    v = cargar_verificador()
    ruta = tmp_path / "Ej_263_figura.jff"
    F.guardar_archivo(referencia("Ej_263_figura"), ruta)
    assert v.revisar(ruta, True)[0] == "OK"
    for extension in (".json", ".xml"):
        assert F.leer_archivo(ruta.with_suffix(extension)) == referencia("Ej_263_figura")
