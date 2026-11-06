"""Pruebas de la lógica de la interfaz (src/controlador.py) y del dibujo (src/dibujo.py)."""

from pathlib import Path
from xml.etree import ElementTree

import pytest

import controlador as K
import dibujo as D
import formatos as F
from automata import Automata, AutomataInvalido
from test_automata import anexo3, par_de_ceros, termina_en_01
from test_formatos import con_nombres_dificiles, con_simbolos_especiales

RAIZ = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Edición del alfabeto, los estados y las transiciones
# ---------------------------------------------------------------------------

def test_el_autómata_nuevo_es_valido_y_se_puede_completar():
    a = K.automata_nuevo()
    assert a.validar() == [] and a.alfabeto == ["a", "b"] and a.inicial == "q0"
    assert K.nombre_de_estado_libre(a) == "q1"
    a.agregar_estado("q1")
    assert K.nombre_de_estado_libre(a) == "q2"
    a.quitar_estado("q0")                              # quedan q1; q0 vuelve a estar libre
    assert K.nombre_de_estado_libre(a) == "q2"         # el contador parte de cuántos estados hay
    assert K.nombre_de_estado_libre(a) not in a.estados


@pytest.mark.parametrize("texto, esperado", [("a, b", ["a", "b"]), ("ab", ["a", "b"]), ("b a", ["b", "a"]), ("a,a,b", ["a", "b"])])
def test_aplicar_alfabeto_acepta_varias_formas_de_escribirlo(texto, esperado):
    a = Automata("xyz", ["q0"], "q0")
    K.aplicar_alfabeto(a, texto)
    assert a.alfabeto == esperado


def test_aplicar_alfabeto_informa_de_lo_agregado_y_lo_quitado():
    a = par_de_ceros()                                 # Σ = {0, 1} con 4 transiciones
    agregados, quitados, perdidas = K.aplicar_alfabeto(a, "1, 2")
    assert (agregados, quitados, perdidas) == (["2"], ["0"], 2)
    assert a.alfabeto == ["1", "2"] and all(lee == "1" for _, lee, _ in a.transiciones())


@pytest.mark.parametrize("texto", ["", "  ", ",,", "a, λ"])
def test_aplicar_alfabeto_rechaza_textos_no_validos_sin_cambiar_nada(texto):
    a = par_de_ceros()
    with pytest.raises(ValueError):
        K.aplicar_alfabeto(a, texto)
    assert a == par_de_ceros()


def test_destinos_de_texto_entiende_listas_conjuntos_y_vacio():
    a = Automata("a", ["q0", "q1", "q2", "{q0,q1}", "{q2}"], "q0")
    assert K.destinos_de_texto(a, "q0, q1") == ["q0", "q1"]
    assert K.destinos_de_texto(a, "q0;q1  q2") == ["q0", "q1", "q2"]
    assert K.destinos_de_texto(a, "q1, q1") == ["q1"]
    assert K.destinos_de_texto(a, "{q1, q2}") == ["q1", "q2"]            # notación de conjunto
    assert K.destinos_de_texto(a, "{q0,q1}") == ["{q0,q1}"]              # un estado que se llama así
    assert K.destinos_de_texto(a, "{q0,q1}, {q2}") == ["{q0,q1}", "{q2}"]
    for vacio in ("", "  ", "∅", "-", None):
        assert K.destinos_de_texto(a, vacio) == []
    with pytest.raises(AutomataInvalido, match="q9"):
        K.destinos_de_texto(a, "q0, q9")


def test_fijar_transicion_reemplaza_los_destinos_y_no_cambia_nada_si_hay_un_error():
    a = termina_en_01()
    assert K.texto_de_destinos(a, "q0", "0") == "q0, q1"
    K.fijar_transicion(a, "q0", "0", "q2")
    assert a.destinos("q0", "0") == ("q2",)
    with pytest.raises(AutomataInvalido):
        K.fijar_transicion(a, "q0", "0", "q1, zzz")
    assert a.destinos("q0", "0") == ("q2",)                                # el error no dejó la celda a medias
    K.fijar_transicion(a, "q0", "0", "∅")
    assert a.destinos("q0", "0") == ()
    K.fijar_transicion(a, "q0", "", "q1")                                  # transición λ
    assert a.tipo == "AFND-lambda" and K.texto_de_destinos(a, "q0", "") == "q1"


# ---------------------------------------------------------------------------
# Archivos
# ---------------------------------------------------------------------------

@pytest.fixture
def carpeta_de_trabajo(tmp_path, monkeypatch):
    (tmp_path / "automatas" / "lista").mkdir(parents=True)
    monkeypatch.setattr(K, "RAIZ", tmp_path)
    monkeypatch.setattr(K, "CARPETA_AUTOMATAS", tmp_path / "automatas")
    monkeypatch.setattr(K, "CARPETA_SALIDAS", tmp_path / "salidas")
    return tmp_path


def test_guardar_en_salidas_escribe_los_tres_formatos_y_se_puede_volver_a_cargar(carpeta_de_trabajo):
    rutas = K.guardar_en_salidas(anexo3(), "mi autómata (1)")
    assert rutas == ["salidas/mi_aut_mata_1.jff", "salidas/mi_aut_mata_1.json", "salidas/mi_aut_mata_1.xml"] or \
        all(r.startswith("salidas/") for r in rutas) and len(rutas) == 3
    for ruta in rutas:
        assert K.cargar(ruta) == anexo3()
    solo_json = K.guardar_en_salidas(par_de_ceros(), "otro", formatos=("json",))
    assert solo_json == ["salidas/otro.json"]


@pytest.mark.parametrize("nombre, base", [("ejemplo", "ejemplo"), ("ejemplo.jff", "ejemplo"), ("../../fuera", "fuera"),
                                          ("a/b\\c", "a_b_c"), ("  con espacios  ", "con_espacios")])
def test_los_nombres_de_archivo_no_pueden_salir_de_salidas(nombre, base):
    assert K.nombre_de_archivo_valido(nombre) == base


@pytest.mark.parametrize("nombre", ["", "   ", "...", "///"])
def test_un_nombre_sin_letras_se_rechaza(nombre):
    with pytest.raises(F.FormatoInvalido):
        K.nombre_de_archivo_valido(nombre)


def test_archivos_disponibles_lista_los_tres_formatos_de_las_dos_carpetas(carpeta_de_trabajo):
    F.guardar_archivo(par_de_ceros(), carpeta_de_trabajo / "automatas" / "lista" / "uno.jff")
    F.guardar_archivo(par_de_ceros(), carpeta_de_trabajo / "automatas" / "lista" / "uno.json")
    K.guardar_en_salidas(anexo3(), "dos", formatos=("xml",))
    (carpeta_de_trabajo / "automatas" / "lista" / "notas.txt").write_text("no es un autómata")
    etiquetas = [e for e, _ in K.archivos_disponibles()]
    assert etiquetas == ["automatas/lista/uno.jff", "automatas/lista/uno.json", "salidas/dos.xml"]


def test_cargar_acepta_rutas_relativas_al_proyecto_y_absolutas_y_explica_los_errores(carpeta_de_trabajo):
    ruta = carpeta_de_trabajo / "automatas" / "lista" / "uno.json"
    F.guardar_archivo(par_de_ceros(), ruta)
    assert K.cargar("automatas/lista/uno.json") == par_de_ceros()
    assert K.cargar(f'"{ruta}"') == par_de_ceros()
    for malo in ("", "   ", "no_existe.jff", "automatas/lista/uno.pdf"):
        with pytest.raises(F.FormatoInvalido):
            K.cargar(malo)


def test_guardar_diagrama_escribe_un_svg_valido(carpeta_de_trabajo):
    ruta = K.guardar_diagrama(anexo3(), "diagrama")
    assert ruta == "salidas/diagrama.svg"
    ElementTree.fromstring((carpeta_de_trabajo / ruta).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Textos de la simulación y de las conversiones
# ---------------------------------------------------------------------------

def test_descripcion_de_cada_paso_del_afnd_lambda():
    a = anexo3()
    r = a.simular("ba")
    assert K.titulo_de_paso(r, 0) == "Inicio" and K.titulo_de_paso(r, 2) == "Paso 2: lee «a»"
    inicio = K.descripcion_de_paso(a, r, 0)
    assert "q0" in inicio and "λ-clausura: {q0, q1}" in inicio and "q0 –λ→ q1" in inicio
    paso = K.descripcion_de_paso(a, r, 1)
    assert "«b»" in paso and "q0 –b→ q0" in paso and "{q0, q1}" in paso
    assert K.lineas_de_traza(a, r) == ["Inicio  →  {q0, q1}", "Paso 1: lee «b»  →  {q0, q1}", "Paso 2: lee «a»  →  {q1}"]


def test_descripcion_cuando_el_automata_se_bloquea():
    a = anexo3()
    r = a.simular("aab")
    assert "No hay ninguna transición posible" in K.descripcion_de_paso(a, r, 2)
    assert "se bloqueó" in K.descripcion_de_paso(a, r, 2)
    assert K.veredicto(a, r) == ("RECHAZADA", "El autómata se bloqueó antes de terminar de leer la cadena.")


def test_veredicto_en_cada_caso():
    a = anexo3()
    assert K.veredicto(a, a.simular("ba"))[0] == "ACEPTADA" and "q1" in K.veredicto(a, a.simular("ba"))[1]
    assert "no quedó ningún estado activo" in K.veredicto(a, a.simular("ab"))[1]
    p = par_de_ceros()
    assert K.veredicto(p, p.simular("0")) == ("RECHAZADA", "Terminó de leer la cadena en {q1}, que no es de aceptación.")


def test_la_cadena_vacia_se_escribe_lambda_o_nada():
    assert K.texto_de_cadena("λ") == "" and K.texto_de_cadena("  λ ") == "" and K.texto_de_cadena("") == ""
    assert K.texto_de_cadena(None) == "" and K.texto_de_cadena("ab") == "ab"


def test_caminos_en_texto_muestra_ramas_y_el_limite():
    lineas, aviso = K.caminos_en_texto(termina_en_01(), "0101")
    assert lineas and aviso == "" and sum("ACEPTA" in x for x in lineas) == 1
    assert any("se bloquea" in x for x in lineas)
    _, aviso = K.caminos_en_texto(termina_en_01(), "0" * 3)
    assert aviso == ""


def test_filas_de_clausuras_y_de_subconjuntos():
    assert K.filas_de_clausuras(anexo3()) == [("q0", "{q0, q1}"), ("q1", "{q1}")]
    a = termina_en_01()
    filas = K.filas_de_subconjuntos(a, a.a_afd())
    assert filas == [("{q0}", "{q0}"), ("{q0,q1}", "{q0, q1}"), ("{q0,q2}", "{q0, q2}")]


def test_lineas_de_particiones_de_un_afd_parcial_mencionan_la_trampa():
    parcial = Automata("ab", ["q0", "q1"], "q0", ["q1"], [("q0", "a", "q1")])
    lineas = K.lineas_de_particiones(parcial.particiones())
    assert lineas[0].startswith("Partición 0:") and "trampa" in lineas[-1]
    completo = par_de_ceros().particiones()
    assert "trampa" not in " ".join(K.lineas_de_particiones(completo))


# ---------------------------------------------------------------------------
# Dibujo SVG
# ---------------------------------------------------------------------------

SVG = "{http://www.w3.org/2000/svg}"


def elementos(svg, etiqueta):
    return ElementTree.fromstring(svg).findall(f".//{SVG}{etiqueta}")


def test_el_svg_es_xml_valido_y_dibuja_cada_estado():
    a = par_de_ceros()
    svg = D.svg_automata(a)
    raiz = ElementTree.fromstring(svg)
    assert raiz.tag == f"{SVG}svg" and raiz.get("viewBox")
    assert len(elementos(svg, "circle")) == 3                  # 2 estados y 1 círculo extra del de aceptación
    textos = [t.text for t in elementos(svg, "text")]
    assert "q0" in textos and "q1" in textos


def test_el_doble_circulo_marca_la_aceptacion_y_una_flecha_el_inicial():
    svg = D.svg_automata(termina_en_01())
    assert len(elementos(svg, "circle")) == 4                  # 3 estados + 1 de aceptación
    assert len(elementos(svg, "polygon")) >= 1                 # las puntas de flecha, incluida la del inicial


def test_las_etiquetas_juntan_los_simbolos_de_una_misma_flecha_y_escriben_lambda():
    textos = [t.text for t in elementos(D.svg_automata(anexo3()), "text")]
    assert "a,λ" in textos or "λ,a" in textos
    assert "b" in textos
    assert "0,1" in [t.text for t in elementos(D.svg_automata(termina_en_01()), "text")]


def test_los_estados_activos_y_las_transiciones_resaltadas_cambian_de_color():
    a = termina_en_01()
    normal = D.svg_automata(a)
    activo = D.svg_automata(a, activos={"q1"}, resaltadas=[("q0", "0", "q1")])
    assert D.ACTIVO_RELLENO not in normal and D.RESALTADO not in normal
    assert D.ACTIVO_RELLENO in activo and D.RESALTADO in activo
    assert activo.count(D.ACTIVO_RELLENO) == 1                 # solo el estado q1


def test_una_flecha_de_ida_y_vuelta_se_dibuja_curva_y_una_sola_ida_recta():
    ida_y_vuelta = Automata("ab", ["p", "q"], "p", [], [("p", "a", "q"), ("q", "b", "p")])
    assert any(" Q " in e.get("d") for e in elementos(D.svg_automata(ida_y_vuelta), "path"))
    solo_ida = Automata("a", ["p", "q"], "p", [], [("p", "a", "q")])
    assert not any(" Q " in e.get("d") for e in elementos(D.svg_automata(solo_ida), "path"))


def test_los_nombres_con_caracteres_especiales_se_escapan():
    for a in (con_nombres_dificiles(), con_simbolos_especiales()):
        svg = D.svg_automata(a)
        textos = {t.text for t in elementos(svg, "text")}            # el XML se puede leer
        assert set(a.estados) <= textos
    assert "&lt;q0&gt;" in D.svg_automata(con_nombres_dificiles())


def test_un_estado_con_nombre_largo_tiene_un_circulo_mas_grande():
    assert D.radio_de("q0") == 26.0 and D.radio_de("{q0,q1,q2,q3}") > 26.0 and D.radio_de("x" * 100) == 64.0


def test_un_autómata_sin_estados_muestra_un_aviso_en_vez_de_fallar():
    svg = D.svg_automata(Automata("ab"))
    assert "Aún no hay estados" in svg and ElementTree.fromstring(svg) is not None


def test_el_dibujo_cabe_en_su_marco():
    """Ningún estado queda fuera del viewBox, aunque haya flechas curvas y bucles."""
    for ruta in sorted((RAIZ / "automatas").rglob("*.jff")):
        a = F.leer_archivo(ruta)
        raiz = ElementTree.fromstring(D.svg_automata(a))
        x0, y0, ancho, alto = (float(v) for v in raiz.get("viewBox").split())
        for c in raiz.findall(f".//{SVG}circle"):
            cx, cy, r = float(c.get("cx")), float(c.get("cy")), float(c.get("r"))
            assert x0 <= cx - r and cx + r <= x0 + ancho and y0 <= cy - r and cy + r <= y0 + alto, ruta.name
        assert len([t for t in raiz.findall(f".//{SVG}text") if t.text in a.estados]) == len(a.estados), ruta.name


def test_todos_los_autómatas_entregados_se_pueden_dibujar():
    rutas = sorted((RAIZ / "automatas").rglob("*.jff"))
    assert rutas, "no hay autómatas entregados"
    for ruta in rutas:
        a = F.leer_archivo(ruta)
        svg = D.svg_automata(a, activos={a.inicial})
        assert ElementTree.fromstring(svg).tag == f"{SVG}svg"
