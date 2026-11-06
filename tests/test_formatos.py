"""Pruebas de la lectura y escritura de autómatas (src/formatos.py)."""

import json
from itertools import product
from pathlib import Path
from xml.etree import ElementTree

import pytest

import automata as A
import formatos as F
from automata import Automata
from formatos import FormatoInvalido
from test_automata import (anexo3, cadena_de_lambdas, ejercicio_192, multiplos_de, n_desde_el_final,
                           par_de_ceros, termina_en_01)

RAIZ = Path(__file__).resolve().parent.parent

# Los tres archivos del Anexo 3 del enunciado: el mismo AFND-λ de dos estados.
ANEXO_JFF = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<structure>
  <type>fa</type>
  <automaton>
    <state id="0" name="q0">
      <x>80.0</x><y>120.0</y>
      <initial/>
    </state>
    <state id="1" name="q1">
      <x>240.0</x><y>120.0</y>
      <final/>
    </state>
    <transition><from>0</from><to>1</to><read>a</read></transition>
    <transition><from>0</from><to>0</to><read>b</read></transition>
    <transition><from>0</from><to>1</to><read/></transition>
  </automaton>
</structure>
"""

ANEXO_JSON = """{
  "tipo": "AFND-lambda",
  "alfabeto": ["a", "b"],
  "estados": ["q0", "q1"],
  "inicial": "q0",
  "aceptacion": ["q1"],
  "transiciones": [
    { "desde": "q0", "lee": "a", "hacia": ["q1"] },
    { "desde": "q0", "lee": "b", "hacia": ["q0"] },
    { "desde": "q0", "lee": "",  "hacia": ["q1"] }
  ]
}
"""

ANEXO_XML = """<?xml version="1.0" encoding="UTF-8"?>
<automata tipo="AFND-lambda">
  <alfabeto><simbolo>a</simbolo><simbolo>b</simbolo></alfabeto>
  <estados>
    <estado nombre="q0" inicial="true"/>
    <estado nombre="q1" aceptacion="true"/>
  </estados>
  <transiciones>
    <transicion desde="q0" lee="a" hacia="q1"/>
    <transicion desde="q0" lee="b" hacia="q0"/>
    <transicion desde="q0" lee="" hacia="q1"/>
  </transiciones>
</automata>
"""


def con_nombres_dificiles():
    """Nombres con caracteres que XML tiene que escapar, espacios y símbolos no ASCII."""
    a = Automata("ab", ['<q0>', 'q&1', 'ñ"2"', "{q0,q1}", "∅", "con espacio"], "<q0>", ["∅", "ñ\"2\""])
    for desde, lee, hacia in [("<q0>", "a", "q&1"), ("q&1", "b", 'ñ"2"'), ('ñ"2"', "a", "{q0,q1}"),
                              ("{q0,q1}", "", "∅"), ("∅", "b", "con espacio"), ("con espacio", "a", "<q0>")]:
        a.agregar_transicion(desde, lee, hacia)
    return a


def con_simbolos_especiales():
    """Símbolos que XML escapa: < > & ' \" """
    a = Automata("<>&'\"", ["q0", "q1"], "q0", ["q1"])
    for s in "<>&'\"":
        a.agregar_transicion("q0", s, "q1")
    return a


def borrador_sin_inicial():
    return Automata("ab", ["q0", "q1"], None, ["q1"], [("q0", "a", "q1")])


EJEMPLOS = [par_de_ceros, anexo3, termina_en_01, cadena_de_lambdas, ejercicio_192, con_nombres_dificiles,
            con_simbolos_especiales, borrador_sin_inicial, lambda: n_desde_el_final(4), lambda: multiplos_de(6)]


def cadenas(alfabeto, longitud_maxima):
    for n in range(longitud_maxima + 1):
        for t in product(alfabeto, repeat=n):
            yield "".join(t)


# ---------------------------------------------------------------------------
# El Anexo 3: los tres formatos describen el mismo autómata
# ---------------------------------------------------------------------------

def test_los_tres_archivos_del_anexo_3_se_leen_como_el_mismo_automata():
    esperado = anexo3()
    assert F.leer_jff(ANEXO_JFF) == esperado
    assert F.leer_json(ANEXO_JSON) == esperado
    assert F.leer_xml(ANEXO_XML) == esperado
    assert F.leer_jff(ANEXO_JFF) == F.leer_json(ANEXO_JSON) == F.leer_xml(ANEXO_XML)


@pytest.mark.parametrize("leer, contenido", [(F.leer_jff, ANEXO_JFF), (F.leer_json, ANEXO_JSON), (F.leer_xml, ANEXO_XML)])
def test_se_interpretan_los_cinco_componentes_de_la_quintupla(leer, contenido):
    a = leer(contenido)
    assert set(a.alfabeto) == {"a", "b"}
    assert a.estados == ["q0", "q1"]
    assert a.inicial == "q0"
    assert a.aceptacion == frozenset({"q1"})
    assert set(a.transiciones()) == {("q0", "a", "q1"), ("q0", "b", "q0"), ("q0", "", "q1")}
    assert a.tipo == "AFND-lambda"


def test_la_lectura_del_anexo_conserva_el_comportamiento_del_automata():
    a = F.leer_jff(ANEXO_JFF)
    assert a.acepta("") and a.acepta("bba") and not a.acepta("ab")      # la cadena vacía solo por la λ
    assert a.clausuras() == {"q0": ("q0", "q1"), "q1": ("q1",)}


def test_las_coordenadas_del_jff_se_leen_pero_no_cambian_el_automata():
    a = F.leer_jff(ANEXO_JFF)
    assert a.posiciones == {"q0": (80.0, 120.0), "q1": (240.0, 120.0)}
    sin_coordenadas = ANEXO_JFF.replace("<x>80.0</x><y>120.0</y>", "").replace("<x>240.0</x><y>120.0</y>", "")
    b = F.leer_jff(sin_coordenadas)
    assert b == a and b.posiciones == {}


def test_la_escritura_sigue_el_formato_del_anexo_3():
    a = anexo3()
    escrito, esperado_json = json.loads(F.escribir_json(a)), json.loads(ANEXO_JSON)
    assert list(escrito) == list(esperado_json)                                   # mismos campos y mismo orden
    por_clave = lambda ts: sorted(ts, key=lambda t: (t["desde"], t["lee"]))      # el orden de las transiciones no importa
    assert {k: v for k, v in escrito.items() if k != "transiciones"} == \
        {k: v for k, v in esperado_json.items() if k != "transiciones"}
    assert por_clave(escrito["transiciones"]) == por_clave(esperado_json["transiciones"])
    xml = ElementTree.fromstring(F.escribir_xml(a))
    esperado = ElementTree.fromstring(ANEXO_XML)
    assert xml.attrib == esperado.attrib
    assert [e.attrib for e in xml.iter("estado")] == [e.attrib for e in esperado.iter("estado")]
    clave = lambda e: (e["desde"], e["lee"])
    assert sorted((e.attrib for e in xml.iter("transicion")), key=clave) == \
        sorted((e.attrib for e in esperado.iter("transicion")), key=clave)
    assert [s.text for s in xml.iter("simbolo")] == ["a", "b"]
    jff = F.escribir_jff(a)
    assert "<read/>" in jff and "<type>fa</type>" in jff and "<initial/>" in jff and "<final/>" in jff


def test_la_transicion_lambda_es_la_cadena_vacia_en_los_tres_formatos():
    a = anexo3()
    assert '"lee": ""' in F.escribir_json(a)
    assert 'lee=""' in F.escribir_xml(a)
    assert "<read/>" in F.escribir_jff(a)
    # y también se acepta el carácter λ al leer
    con_lambda = ANEXO_JSON.replace('"lee": ""', '"lee": "λ"')
    assert F.leer_json(con_lambda) == a
    assert F.leer_xml(ANEXO_XML.replace('lee="" ', 'lee="λ" ')) == a


# ---------------------------------------------------------------------------
# Exportar e importar son operaciones inversas
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fabrica", EJEMPLOS)
@pytest.mark.parametrize("formato", F.FORMATOS)
def test_importar_lo_exportado_devuelve_el_mismo_automata(fabrica, formato):
    original = fabrica()
    leido = F.leer(F.escribir(original, formato), formato, **({"alfabeto": original.alfabeto} if formato == "jff" else {}))
    assert leido == original
    assert leido.tipo == original.tipo


@pytest.mark.parametrize("fabrica", EJEMPLOS)
def test_pasar_por_los_tres_formatos_y_volver_no_cambia_nada(fabrica):
    original = fabrica()
    a = original
    for formato in ("json", "xml", "jff", "xml", "json", "jff"):
        a = F.leer(F.escribir(a, formato), formato, **({"alfabeto": original.alfabeto} if formato == "jff" else {}))
    assert a == original


@pytest.mark.parametrize("formato", F.FORMATOS)
def test_el_autómata_importado_se_comporta_igual_que_el_original(formato):
    for fabrica in (par_de_ceros, anexo3, termina_en_01, cadena_de_lambdas):
        original = fabrica()
        leido = F.leer(F.escribir(original, formato), formato)
        assert all(leido.acepta(w) == original.acepta(w) for w in cadenas(original.alfabeto, 7))


@pytest.mark.parametrize("formato", F.FORMATOS)
def test_el_resultado_de_una_conversion_tambien_viaja_bien(formato):
    """Los estados del AFD se llaman {q0,q1}: llevan llaves y comas."""
    afd = termina_en_01().a_afd().afd
    assert F.leer(F.escribir(afd, formato), formato) == afd


def test_exportar_dos_veces_da_exactamente_el_mismo_texto():
    for fabrica in EJEMPLOS:
        for formato in F.FORMATOS:
            assert F.escribir(fabrica(), formato) == F.escribir(fabrica(), formato)


def test_un_borrador_sin_estado_inicial_se_puede_guardar_y_recuperar():
    a = borrador_sin_inicial()
    for formato in F.FORMATOS:
        assert F.leer(F.escribir(a, formato), formato).inicial is None
    assert json.loads(F.escribir_json(a))["inicial"] is None


def test_el_jff_no_guarda_el_alfabeto_y_se_deduce_de_las_transiciones():
    a = Automata("abc", ["q0", "q1"], "q0", ["q1"], [("q0", "a", "q1"), ("q1", "b", "q1")])
    assert F.simbolos_que_el_jff_no_conserva(a) == ["c"]
    deducido = F.leer_jff(F.escribir_jff(a))
    assert deducido.alfabeto == ["a", "b"] and deducido != a
    assert F.leer_jff(F.escribir_jff(a), alfabeto=a.alfabeto) == a
    for formato in ("json", "xml"):                       # los otros dos sí lo conservan
        assert F.leer(F.escribir(a, formato), formato).alfabeto == ["a", "b", "c"]
    assert F.simbolos_que_el_jff_no_conserva(par_de_ceros()) == []


def test_las_posiciones_se_conservan_y_si_faltan_se_reparten_por_capas():
    a = par_de_ceros()
    assert a.posiciones == {}
    b = F.leer_jff(F.escribir_jff(a))
    assert set(b.posiciones) == {"q0", "q1"} and b.posiciones["q0"] != b.posiciones["q1"]
    a.posiciones = {"q0": (10.0, 20.0), "q1": (310.5, 20.0)}
    assert F.leer_jff(F.escribir_jff(a)).posiciones == a.posiciones
    grande = multiplos_de(22)
    puntos = set(F.leer_jff(F.escribir_jff(grande)).posiciones.values())
    assert len(puntos) == 22                                # ningún estado cae encima de otro


# ---------------------------------------------------------------------------
# Archivos de JFLAP reales: ids que no empiezan en 0, sin nombres, con elementos extra
# ---------------------------------------------------------------------------

def test_se_lee_un_jff_con_el_estilo_de_jflap():
    texto = """<?xml version="1.0" encoding="UTF-8" standalone="no"?><!--Created with JFLAP 7.1.-->
<structure>&#13;
	<type>fa</type>&#13;
	<!--The list of states.-->
	<automaton>
		<!--The list of states.-->
		<state id="7" name="inicio">
			<x>60.0</x>
			<y>90.0</y>
			<label>etiqueta que se ignora</label>
			<initial/>
		</state>
		<state id="12">
			<x>200.0</x>
			<y>90.0</y>
			<final/>
		</state>
		<note><text>una nota</text><x>1.0</x><y>2.0</y></note>
		<transition>
			<from>7</from>
			<to>12</to>
			<read>1</read>
		</transition>
		<transition>
			<from>12</from>
			<to>12</to>
			<read>0</read>
		</transition>
	</automaton>
</structure>"""
    a = F.leer_jff(texto)
    assert a.estados == ["inicio", "q12"]               # sin nombre se usa q + id
    assert a.inicial == "inicio" and a.aceptacion == frozenset({"q12"})
    assert a.alfabeto == ["0", "1"]
    assert a.acepta("1") and a.acepta("100") and not a.acepta("0")


# ---------------------------------------------------------------------------
# Entradas incorrectas
# ---------------------------------------------------------------------------

JFF_BASE = ("<structure><type>fa</type><automaton>"
            '<state id="0" name="q0"><initial/></state><state id="1" name="q1"><final/></state>'
            "{extra}</automaton></structure>")


def jff(extra="", **cambios):
    texto = JFF_BASE.format(extra=extra)
    for viejo, nuevo in cambios.items():
        texto = texto.replace(viejo.replace("_", " "), nuevo)
    return texto


ERRORES = [
    ("jff", "esto no es xml", "XML válido"),
    ("jff", "", "vacío"),
    ("jff", "<otra/>", "<structure>"),
    ("jff", "<structure><type>pda</type><automaton/></structure>", "autómatas finitos"),
    ("jff", "<structure><type>fa</type></structure>", "<automaton>"),
    ("jff", jff().replace("<final/>", "<initial/>"), "más de un estado inicial"),
    ("jff", jff('<transition><from>0</from><to>9</to><read>a</read></transition>'), "no existe"),
    ("jff", jff('<transition><from>0</from><to>1</to><read>ab</read></transition>'), "varios símbolos"),
    ("jff", jff('<transition><from>0</from><to>1</to></transition>'), "<read>"),
    ("jff", JFF_BASE.format(extra="").replace('name="q1"', 'name="q0"'), "ya existe"),
    ("jff", '<!DOCTYPE x [<!ENTITY a "b">]>' + jff(), "DOCTYPE"),
    ("json", "{no es json", "JSON válido"),
    ("json", "[1, 2]", "objeto"),
    ("json", '{"alfabeto": []}', "Falta el campo"),
    ("json", ANEXO_JSON.replace('"alfabeto": ["a", "b"]', '"alfabeto": "ab"'), "lista de textos"),
    ("json", ANEXO_JSON.replace('"inicial": "q0"', '"inicial": 5'), "inicial"),
    ("json", ANEXO_JSON.replace('"tipo": "AFND-lambda"', '"tipo": "AFP"'), "desconocido"),
    ("json", ANEXO_JSON.replace('"tipo": "AFND-lambda"', '"tipo": "AFD"'), "declara un AFD"),
    ("json", ANEXO_JSON.replace('"hacia": ["q1"] },\n    { "desde": "q0", "lee": "b"', '"x": 1 },\n    { "desde": "q0", "lee": "b"'),
     "«desde», «lee» y «hacia»"),
    ("json", ANEXO_JSON.replace('"hacia": ["q0"]', '"hacia": ["q9"]'), "no existe"),
    ("json", ANEXO_JSON.replace('"lee": "a"', '"lee": "z"'), "alfabeto"),
    ("json", ANEXO_JSON.replace('"estados": ["q0", "q1"]', '"estados": ["q0", "q0", "q1"]'), "ya existe"),
    ("json", ANEXO_JSON.replace('"aceptacion": ["q1"]', '"aceptacion": ["q7"]'), "no existe"),
    ("xml", "<automata", "XML válido"),
    ("xml", "<otro/>", "<automata>"),
    ("xml", "<automata><alfabeto/></automata>", "Falta el elemento"),
    ("xml", ANEXO_XML.replace('<estado nombre="q1" aceptacion="true"/>', '<estado aceptacion="true"/>'), "«nombre»"),
    ("xml", ANEXO_XML.replace('aceptacion="true"', 'aceptacion="quizá"'), "Valor lógico"),
    ("xml", ANEXO_XML.replace('<estado nombre="q1" aceptacion="true"/>', '<estado nombre="q1" inicial="true"/>'),
     "más de un estado inicial"),
    ("xml", ANEXO_XML.replace('<transicion desde="q0" lee="a" hacia="q1"/>', '<transicion desde="q0" hacia="q1"/>'), "«lee»"),
    ("xml", ANEXO_XML.replace('tipo="AFND-lambda"', 'tipo="AFD"'), "declara un AFD"),
    ("xml", '<!DOCTYPE a [<!ENTITY e "x">]>' + ANEXO_XML, "DOCTYPE"),
]


@pytest.mark.parametrize("formato, contenido, fragmento", ERRORES)
def test_los_archivos_incorrectos_se_rechazan_con_un_mensaje_claro(formato, contenido, fragmento):
    with pytest.raises(FormatoInvalido) as error:
        F.leer(contenido, formato)
    assert fragmento in str(error.value)


def test_un_tipo_mas_general_que_el_real_si_se_acepta():
    """Todo AFD es un AFND: declarar AFND o AFND-λ para un autómata determinista no es un error."""
    for tipo in ("AFND", "AFND-lambda", "afd", "AFND-λ"):
        texto = F.escribir_json(par_de_ceros()).replace('"AFD"', f'"{tipo}"')
        assert F.leer_json(texto) == par_de_ceros()


def test_el_tipo_es_opcional_al_leer():
    datos = json.loads(F.escribir_json(par_de_ceros()))
    del datos["tipo"]
    assert F.leer_json(json.dumps(datos)) == par_de_ceros()


def test_hacia_puede_ser_un_solo_texto_o_una_lista():
    datos = json.loads(ANEXO_JSON)
    datos["transiciones"][0]["hacia"] = "q1"
    assert F.leer_json(json.dumps(datos)) == anexo3()


def test_no_se_escriben_nombres_con_caracteres_que_xml_no_admite():
    a = Automata("a", ["q\x01"], "q\x01")
    for formato in ("jff", "xml"):
        with pytest.raises(FormatoInvalido):
            F.escribir(a, formato)
    assert F.leer_json(F.escribir_json(a)) == a                 # JSON sí los admite


def test_un_formato_desconocido_se_rechaza():
    with pytest.raises(FormatoInvalido):
        F.escribir(par_de_ceros(), "pdf")
    with pytest.raises(FormatoInvalido):
        F.leer("", "pdf")


# ---------------------------------------------------------------------------
# Archivos en disco
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("extension", [".jff", ".json", ".xml", ".JFF"])
def test_guardar_y_leer_un_archivo_segun_su_extension(tmp_path, extension):
    ruta = tmp_path / f"ejemplo{extension}"
    original = con_nombres_dificiles()
    F.guardar_archivo(original, ruta)
    leido = F.leer_archivo(ruta, alfabeto=original.alfabeto) if extension.lower() == ".jff" else F.leer_archivo(ruta)
    assert leido == original and leido.nombre == "ejemplo"
    assert b"\r" not in ruta.read_bytes()                       # siempre fin de línea \n


def test_las_extensiones_y_los_archivos_que_no_existen_se_rechazan(tmp_path):
    with pytest.raises(FormatoInvalido):
        F.guardar_archivo(par_de_ceros(), tmp_path / "a.txt")
    with pytest.raises(FormatoInvalido):
        F.leer_archivo(tmp_path / "a.pdf")
    with pytest.raises(FormatoInvalido, match="No se pudo leer"):
        F.leer_archivo(tmp_path / "no_existe.jff")


def test_un_archivo_demasiado_grande_no_se_lee(tmp_path, monkeypatch):
    ruta = tmp_path / "grande.json"
    F.guardar_archivo(par_de_ceros(), ruta)
    monkeypatch.setattr(F, "LIMITE_BYTES", 50)
    with pytest.raises(FormatoInvalido, match="pesa más"):
        F.leer_archivo(ruta)


def test_se_lee_un_json_con_marca_de_orden_de_bytes_y_un_xml_en_latin1(tmp_path):
    json_bom = tmp_path / "bom.json"
    json_bom.write_bytes(b"\xef\xbb\xbf" + F.escribir_json(par_de_ceros()).encode("utf-8"))
    assert F.leer_archivo(json_bom) == par_de_ceros()
    latin1 = tmp_path / "latin1.xml"
    texto = F.escribir_xml(Automata("a", ["año"], "año", ["año"])).replace('encoding="UTF-8"', 'encoding="ISO-8859-1"')
    latin1.write_bytes(texto.encode("latin-1"))
    assert F.leer_archivo(latin1).estados == ["año"]
    malo = tmp_path / "malo.json"
    malo.write_bytes("é".encode("latin-1"))
    with pytest.raises(FormatoInvalido, match="UTF-8"):
        F.leer_archivo(malo)


# ---------------------------------------------------------------------------
# Los autómatas entregados (automatas/): los tres formatos de cada uno coinciden
# ---------------------------------------------------------------------------

ENTREGADOS = sorted((RAIZ / "automatas").rglob("*.jff"))


@pytest.mark.parametrize("ruta", ENTREGADOS, ids=[f"{p.parent.name}/{p.stem}" for p in ENTREGADOS])
def test_cada_jff_entregado_tiene_su_json_y_su_xml_con_el_mismo_automata(ruta):
    principal = F.leer_archivo(ruta)
    assert principal.validar() == [], f"{ruta.name}: definición incompleta"
    for extension in (".json", ".xml"):
        hermano = ruta.with_suffix(extension)
        assert hermano.exists(), f"falta {hermano.name}"
        assert F.leer_archivo(hermano, nombre=principal.nombre) == principal, f"{hermano.name} no coincide con el .jff"
