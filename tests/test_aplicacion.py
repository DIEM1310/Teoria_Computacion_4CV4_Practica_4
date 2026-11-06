"""Ejercicio 5: el autómata del fantasma de Pac-Man (automatas/aplicacion/).

Los resultados esperados de CASOS se razonaron a mano con la Figura 3 de Gribkoff (2013) y la
ampliación descrita en docs/05-del-articulo-al-automata.md, sin usar el simulador; aquí se
comparan con lo que el simulador obtiene al leer el .jff, el .json y el .xml.
"""

import sys
from pathlib import Path

import pytest

import formatos as F

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))
import generar_aplicacion as G                  # noqa: E402

CARPETA = RAIZ / "automatas" / "aplicacion"
FORMATOS = [".jff", ".json", ".xml"]

# (cadena de eventos, estado final esperado, ¿se acepta?, por qué)
CASOS = [
    ("", "q0", False, "sin eventos el fantasma sigue en Vagar"),
    ("v", "q1", True, "ve a Pac-Man y lo persigue"),
    ("vp", "q0", False, "lo pierde y vuelve a vagar"),
    ("vpv", "q1", True, "lo pierde y lo vuelve a ver"),
    ("vvvv", "q1", True, "ver a Pac-Man estando en Perseguir no cambia nada"),
    ("vc", "q2", False, "Pac-Man come pastilla mientras lo persigue: huye"),
    ("cam", "q3", False, "huye, alerta de fin, Pac-Man se lo come: vuelve a la base"),
    ("ce", "q2", False, "la pastilla no puede expirar sin pasar por la alerta (ampliación)"),
    ("caebv", "q1", True, "alerta, expira, llegar a la base no cambia nada en Vagar, ve a Pac-Man"),
    ("cmbrv", "q1", True, "se lo comen, llega a la base, se regenera, vuelve a perseguir"),
    ("cmv", "q3", False, "convertido en ojos, no persigue aunque vea a Pac-Man"),
    ("cmbv", "q5", False, "regenerándose en la base, tampoco persigue"),
    ("cacm", "q3", False, "otra pastilla en la alerta reinicia la huida; luego lo comen"),
    ("vcaev", "q1", True, "persigue, huye, alerta, expira y vuelve a perseguir"),
]


@pytest.fixture(scope="module")
def automata():
    return F.leer_archivo(CARPETA / f"{G.NOMBRE}.jff")


@pytest.mark.parametrize("extension", FORMATOS)
def test_los_archivos_entregados_son_los_que_genera_el_generador(extension):
    """Los archivos de automatas/aplicacion/ coinciden con lo que construye generar_aplicacion.py."""
    assert F.leer_archivo(CARPETA / f"{G.NOMBRE}{extension}") == G.construir()


def estado_final(a, w):
    return a.simular(w).pasos[-1].conjunto


@pytest.mark.parametrize("w, final, acepta, motivo", CASOS)
def test_casos_de_prueba(automata, w, final, acepta, motivo):
    assert automata.acepta(w) is acepta, motivo
    assert estado_final(automata, w) == frozenset({final}), motivo


@pytest.mark.parametrize("extension", FORMATOS)
@pytest.mark.parametrize("w, final, acepta, motivo", CASOS)
def test_los_tres_formatos_dan_lo_mismo(extension, w, final, acepta, motivo):
    a = F.leer_archivo(CARPETA / f"{G.NOMBRE}{extension}")
    assert a.acepta(w) is acepta


def test_es_un_afd_completo_de_seis_estados_y_ocho_eventos(automata):
    assert automata.tipo == "AFD"
    assert automata.es_completo()
    assert len(automata.estados) == 6
    assert len(automata.alfabeto) == 8
    assert automata.inicial == "q0"
    assert automata.aceptacion == frozenset({"q1"})


def test_la_ampliacion_agrega_dos_estados_y_dos_eventos_a_la_figura_3(automata):
    assert len(automata.estados) - 4 >= 2 and len(automata.alfabeto) - 6 >= 2
    # las siete flechas de la Figura 3 (q3 -> q0 se parte en q3 -> q5 -> q0 y q2 -> q0 en q2 -> q4 -> q0)
    figura = [("q0", "v", "q1"), ("q1", "p", "q0"), ("q0", "c", "q2"), ("q1", "c", "q2"),
              ("q2", "m", "q3")]
    for desde, evento, hacia in figura:
        assert automata.destinos(desde, evento) == (hacia,)
    assert automata.destinos("q2", "a") == ("q4",) and automata.destinos("q4", "e") == ("q0",)
    assert automata.destinos("q3", "b") == ("q5",) and automata.destinos("q5", "r") == ("q0",)


def test_todos_los_estados_son_accesibles_y_distinguibles(automata):
    assert len(automata.accesibles()) == 6
    assert len(automata.minimizar().estados) == 6


def test_se_puede_volver_a_vagar_desde_cualquier_estado(automata):
    """Ningún estado es una trampa: de cada uno hay una secuencia de eventos que lleva a Vagar."""
    for q in automata.estados:
        alcanzables, pendientes = {q}, [q]
        while pendientes:
            actual = pendientes.pop()
            for s in automata.alfabeto:
                for t in automata.destinos(actual, s):
                    if t not in alcanzables:
                        alcanzables.add(t)
                        pendientes.append(t)
        assert "q0" in alcanzables
