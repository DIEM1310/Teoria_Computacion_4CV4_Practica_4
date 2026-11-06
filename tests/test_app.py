"""Pruebas de la interfaz (src/app.py) sin abrir ninguna ventana.

Se usa una página simulada y se llama a los mismos manejadores que ejecutan los botones, con la
misma interfaz real de Flet debajo: así se comprueba que la pantalla se arma y que cada acción
cambia el autómata o muestra el error correcto.
"""

from types import SimpleNamespace
from xml.etree import ElementTree

import flet as ft
import pytest

import app as ui
import controlador as K
import formatos as F
from test_automata import anexo3, ejercicio_192, par_de_ceros, termina_en_01

RAIZ_REAL = K.RAIZ


class PaginaFalsa:
    """Lo mínimo de ft.Page que usa la aplicación."""

    def __init__(self):
        self.controls = []
        self.actualizaciones = 0
        self.title = self.theme_mode = self.padding = None

    def add(self, *controles):
        self.controls += controles

    def update(self):
        self.actualizaciones += 1


def evento(valor):
    return SimpleNamespace(control=SimpleNamespace(value=valor))


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Aplicación recién abierta, con salidas/ en una carpeta temporal."""
    monkeypatch.setattr(K, "CARPETA_SALIDAS", tmp_path / "salidas")
    monkeypatch.setattr(K, "RAIZ", tmp_path)
    monkeypatch.setattr(K, "CARPETA_AUTOMATAS", tmp_path / "automatas")
    aplicacion = ui.Aplicacion(PaginaFalsa())
    aplicacion.tmp = tmp_path
    return aplicacion


def cargar(app, automata, nombre="prueba"):
    """Carga un autómata en la aplicación como lo haría el botón Cargar (pasando por un archivo)."""
    automata.nombre = nombre
    ruta = app.tmp / f"{nombre}.json"
    F.guardar_archivo(automata, ruta)
    app.campo_ruta.value = str(ruta)
    app.cargar()
    assert app.mensaje_arch.color == ui.VERDE, app.mensaje_arch.value


def celda(valor):
    return SimpleNamespace(value=valor, error_text=None)


# ---------------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------------

def test_la_pantalla_se_arma_con_las_cinco_pestanas_y_un_automata_nuevo(app):
    assert app.page.title == "Simulador de autómatas finitos"
    assert len(app.page.controls) == 4                                  # título, resumen, problemas y pestañas
    assert app.resumen.value.startswith("nuevo · AFD · 1 estados")
    assert not app.problemas.visible
    assert len(app.lista_estados.controls) == 1
    assert len(app.tabla_editable.controls) == 2                        # encabezado y la fila de q0
    assert app.campo_alfabeto.value == "a, b"


# ---------------------------------------------------------------------------
# 3.1 Definición interactiva
# ---------------------------------------------------------------------------

def test_se_define_un_afd_completo_desde_cero(app):
    """AFD de {0,1} con número par de ceros, definido solo con las acciones de la pantalla."""
    app.campo_alfabeto.value = "0, 1"
    app.aplicar_alfabeto()
    assert app.a.alfabeto == ["0", "1"] and app.mensaje_def.color == ui.VERDE
    app.campo_estado.value = "q1"
    app.agregar_estado()
    app.marcar_aceptacion("q0", True)
    for q, lee, destino in [("q0", "0", "q1"), ("q0", "1", "q0"), ("q1", "0", "q0"), ("q1", "1", "q1")]:
        app.aplicar_celda(q, lee, celda(destino))
    assert app.a == par_de_ceros()
    assert app.a.es_completo() and app.resumen.value.endswith("completo")
    assert len(app.tabla_editable.controls) == 3 and len(app.lista_estados.controls) == 2


def test_un_estado_sin_nombre_recibe_el_siguiente_nombre_libre(app):
    app.campo_estado.value = ""
    app.agregar_estado()
    assert app.a.estados == ["q0", "q1"]
    app.campo_estado.value = "q1"
    app.agregar_estado()                                                # repetido
    assert app.mensaje_def.color == ui.ROJO and "ya existe" in app.mensaje_def.value and len(app.a.estados) == 2


def test_una_celda_con_un_estado_inexistente_no_cambia_nada_y_marca_el_error(app):
    campo = celda("zzz")
    app.aplicar_celda("q0", "a", campo)
    assert app.a.transiciones() == [] and campo.error_text and app.mensaje_def.color == ui.ROJO
    assert "zzz" in app.mensaje_def.value


def test_varios_destinos_en_una_celda_dan_un_afnd_y_la_columna_lambda_un_afnd_lambda(app):
    app.campo_estado.value = "q1"
    app.agregar_estado()
    app.aplicar_celda("q0", "a", celda("q0, q1"))
    assert app.a.tipo == "AFND" and app.resumen.value.startswith("nuevo · AFND ·")
    assert len(app.tabla_editable.controls[0].controls) == 1 + 2          # Estado, a, b
    app.cambiar_lambda(evento(True))                                      # el usuario activa la columna λ
    assert len(app.tabla_editable.controls[0].controls) == 1 + 3          # Estado, λ, a, b
    app.aplicar_celda("q0", "", celda("q1"))
    assert app.a.tipo == "AFND-lambda" and "AFND-λ" in app.resumen.value
    assert app.mostrar_lambda and app.interruptor_lambda.value


def test_cambiar_el_alfabeto_quita_las_transiciones_de_los_simbolos_que_ya_no_estan(app):
    cargar(app, par_de_ceros())
    app.campo_alfabeto.value = "1"
    app.aplicar_alfabeto()
    assert app.a.alfabeto == ["1"] and "2 transiciones" in app.mensaje_def.value
    app.campo_alfabeto.value = ""
    app.aplicar_alfabeto()
    assert app.mensaje_def.color == ui.ROJO and app.a.alfabeto == ["1"]


def test_renombrar_cambiar_el_inicial_la_aceptacion_y_quitar_estados(app):
    cargar(app, termina_en_01())
    campo = celda("inicio")
    app.renombrar("q0", campo)
    assert app.a.inicial == "inicio" and "inicio" in app.a.estados
    app.marcar_inicial("q1")
    assert app.a.inicial == "q1"
    app.marcar_aceptacion("q1", True)
    assert app.a.es_aceptacion("q1")
    app.quitar_estado("q2")
    assert "q2" not in app.a.estados and all("q2" not in (d, h) for d, _, h in app.a.transiciones())
    choque = celda("q1")
    app.renombrar("inicio", choque)                                   # nombre repetido
    assert app.mensaje_def.color == ui.ROJO and choque.value == "inicio" and "inicio" in app.a.estados


def test_la_definicion_incompleta_se_avisa_arriba(app):
    app.quitar_estado("q0")
    assert app.problemas.visible and "estado inicial" in app.problemas.value


def test_nuevo_automata_descarta_todo(app):
    cargar(app, termina_en_01())
    app.nuevo_automata()
    assert app.a.estados == ["q0"] and app.a.alfabeto == ["a", "b"] and app.recorrido is None


# ---------------------------------------------------------------------------
# 3.2 y 3.4 Importar y exportar
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("extension", ["jff", "json", "xml"])
def test_se_carga_un_autómata_de_cada_formato(app, extension):
    ruta = app.tmp / f"anexo.{extension}"
    F.guardar_archivo(anexo3(), ruta)
    app.campo_ruta.value = str(ruta)
    app.cargar()
    assert app.a == anexo3() and app.mensaje_arch.color == ui.VERDE
    assert app.resumen.value.startswith("anexo · AFND-λ · 2 estados · 3 transiciones")
    assert app.mostrar_lambda and app.campo_nombre.value == "anexo"


def test_se_cargan_los_autómatas_entregados_con_su_ruta_relativa(app, monkeypatch):
    monkeypatch.setattr(K, "RAIZ", RAIZ_REAL)                              # aquí sí se usan los de automatas/
    monkeypatch.setattr(K, "CARPETA_AUTOMATAS", RAIZ_REAL / "automatas")
    app.campo_ruta.value = "automatas/lista2-afd/Ej_097_longitud_multiplo_de_3.jff"
    app.cargar()
    assert app.mensaje_arch.color == ui.VERDE and len(app.a.estados) == 3
    opciones = {o.key for o in app.lista_archivos.options}
    assert "automatas/lista2-afd/Ej_097_longitud_multiplo_de_3.jff" in opciones
    app.lista_archivos.value = "automatas/lista2-afd/Ej_139_numero_par_de_ceros.jff"
    app.cargar_elegido()
    assert len(app.a.estados) == 2


@pytest.mark.parametrize("ruta", ["", "no_existe.jff", "archivo.pdf"])
def test_cargar_algo_incorrecto_muestra_el_error_y_conserva_el_autómata(app, ruta):
    antes = app.a.copiar()
    app.campo_ruta.value = ruta
    app.cargar()
    assert app.mensaje_arch.color == ui.ROJO and app.mensaje_arch.visible and app.a == antes


def test_cargar_sin_elegir_nada_de_la_lista_avisa(app):
    app.lista_archivos.value = None
    app.cargar_elegido()
    assert app.mensaje_arch.color == ui.ROJO and "Elige" in app.mensaje_arch.value


def test_un_archivo_corrupto_se_rechaza_con_su_motivo(app):
    ruta = app.tmp / "malo.json"
    ruta.write_text('{"alfabeto": ["a"]}', encoding="utf-8")
    app.campo_ruta.value = str(ruta)
    app.cargar()
    assert app.mensaje_arch.color == ui.ROJO and "Falta el campo" in app.mensaje_arch.value


def test_guardar_escribe_los_tres_formatos_y_lo_guardado_se_puede_cargar(app):
    cargar(app, termina_en_01())
    app.campo_nombre.value = "mi_copia"
    app.guardar(F.FORMATOS)
    assert app.mensaje_arch.color == ui.VERDE
    for extension in F.FORMATOS:
        assert (app.tmp / "salidas" / f"mi_copia.{extension}").exists()
    app.campo_ruta.value = "salidas/mi_copia.xml"
    app.cargar()
    assert app.a == termina_en_01()
    assert "salidas/mi_copia.jff" in {o.key for o in app.lista_archivos.options}


def test_guardar_con_un_nombre_vacio_avisa_y_guardar_el_diagrama_escribe_un_svg(app):
    app.campo_nombre.value = "  "
    app.guardar(("json",))
    assert app.mensaje_arch.color == ui.ROJO
    app.campo_nombre.value = "dibujo"
    app.guardar_svg()
    ElementTree.fromstring((app.tmp / "salidas" / "dibujo.svg").read_text(encoding="utf-8"))


def test_se_avisa_cuando_el_jff_perderia_simbolos_del_alfabeto(app):
    app.campo_alfabeto.value = "a, b, c"
    app.aplicar_alfabeto()
    assert app.aviso_jff.visible and "c" in app.aviso_jff.value


# ---------------------------------------------------------------------------
# 3.3 Simulación y validación
# ---------------------------------------------------------------------------

def test_validar_una_cadena_muestra_el_resultado_y_la_traza_completa(app):
    cargar(app, par_de_ceros())
    app.campo_cadena.value = "0110"
    app.validar()
    assert app.recorrido.aceptada and app.paso == 4 and app.banner.visible
    assert app.texto_banner.value.startswith("ACEPTADA") and app.banner.bgcolor == ui.ft.Colors.GREEN_100
    assert len(app.traza.controls) == 5
    app.campo_cadena.value = "0"
    app.validar()
    assert app.texto_banner.value.startswith("RECHAZADA") and app.banner.bgcolor == ui.ft.Colors.RED_100


def test_paso_a_paso_avanza_y_retrocede_y_deshabilita_los_extremos(app):
    cargar(app, par_de_ceros())
    app.campo_cadena.value = "010"
    app.empezar_paso_a_paso()
    assert app.paso == 0 and not app.banner.visible
    assert app.boton_inicio.disabled and app.boton_anterior.disabled and not app.boton_siguiente.disabled
    assert app.etiqueta_paso.value == "Inicio  (de 3)"
    app.ir_a(1)
    assert "Paso 1: lee «0»" in app.etiqueta_paso.value and "q0 –0→ q1" in app.descripcion.value
    assert not app.boton_inicio.disabled and not app.boton_anterior.disabled
    app.ir_a(3)
    assert app.banner.visible and app.boton_siguiente.disabled and app.boton_final.disabled
    app.ir_a(4)                                                         # no hay paso 4: no pasa nada
    app.ir_a(-1)
    assert app.paso == 3
    app.ir_a(0)
    assert app.paso == 0 and not app.banner.visible


def test_el_diagrama_del_paso_resalta_los_estados_activos_y_las_transiciones_usadas(app):
    cargar(app, anexo3())
    app.campo_cadena.value = "ba"
    app.empezar_paso_a_paso()
    app.ir_a(1)
    contenedor = app.dibujo_sim.content
    assert isinstance(contenedor, ft.Container)
    imagen = contenedor.content.content
    assert isinstance(imagen, ft.Image) and imagen.src.startswith("data:image/svg+xml;base64,")
    import base64
    svg = base64.b64decode(imagen.src.split(",", 1)[1]).decode("utf-8")
    assert svg.count("#ffe082") == 2 and "#d84315" in svg               # q0 y q1 activos, flechas resaltadas


def test_la_cadena_vacia_se_escribe_vacia_o_lambda(app):
    cargar(app, anexo3())
    for texto in ("", "λ", "  λ "):
        app.campo_cadena.value = texto
        app.validar()
        assert app.recorrido.aceptada and app.recorrido.cadena == "" and app.mensaje_sim.visible is False
        assert len(app.recorrido.pasos) == 1


def test_una_cadena_con_simbolos_fuera_del_alfabeto_muestra_el_error(app):
    cargar(app, par_de_ceros())
    app.campo_cadena.value = "012"
    app.validar()
    assert app.mensaje_sim.color == ui.ROJO and "«2»" in app.mensaje_sim.value and app.recorrido is None
    assert app.boton_siguiente.disabled


def test_el_automata_que_se_bloquea_lo_dice(app):
    cargar(app, anexo3())
    app.campo_cadena.value = "aab"
    app.validar()
    assert app.texto_banner.value.startswith("RECHAZADA") and "bloque" in app.texto_banner.value


def test_simular_sin_definir_el_inicial_avisa(app):
    app.quitar_estado("q0")
    app.campo_cadena.value = "a"
    app.validar()
    assert app.mensaje_sim.color == ui.ROJO and "inicial" in app.mensaje_sim.value


def test_el_boton_de_caminos_solo_aparece_en_los_autómatas_no_deterministas(app):
    cargar(app, par_de_ceros())
    assert not app.boton_caminos.visible
    cargar(app, termina_en_01())
    assert app.boton_caminos.visible
    app.campo_cadena.value = "0101"
    app.ver_caminos()
    textos = [c.value for c in app.caminos.controls]
    assert textos[0].startswith("Caminos de cómputo para 0101") and sum("ACEPTA" in t for t in textos) == 1


def test_modificar_el_autómata_descarta_la_simulacion_en_curso(app):
    cargar(app, par_de_ceros())
    app.campo_cadena.value = "01"
    app.validar()
    assert app.recorrido is not None
    app.marcar_aceptacion("q1", True)
    assert app.recorrido is None and app.boton_siguiente.disabled and not app.banner.visible


def test_la_decision_de_diseno_para_el_no_determinismo_esta_en_pantalla():
    assert "todos los caminos a la vez" in ui.DECISION_NO_DETERMINISMO and "2ⁿ" in ui.DECISION_NO_DETERMINISMO


# ---------------------------------------------------------------------------
# Conversiones
# ---------------------------------------------------------------------------

def test_convertir_a_afd_muestra_la_tabla_de_subconjuntos_y_se_puede_usar_el_resultado(app):
    cargar(app, termina_en_01())
    app.convertir(False)
    assert app.resultado is not None and app.resultado.tipo == "AFD" and len(app.resultado.estados) == 3
    assert "2^3 = 8" in app.detalle_conv.controls[0].value and app.acciones_conv.visible
    assert app.campo_nombre_conv.value == "prueba_afd"
    app.usar_resultado()
    assert app.a.tipo == "AFD" and app.resultado is None and not app.acciones_conv.visible
    assert app.a.acepta("1101") and not app.a.acepta("10")


def test_un_afnd_lambda_pasa_primero_a_afnd_y_despues_a_afd(app):
    cargar(app, anexo3())
    app.quitar_lambda()
    assert app.resultado.tipo != "AFND-lambda" and not app.resultado.tiene_lambda
    app.usar_resultado()
    app.convertir(True)
    assert app.resultado.tipo == "AFD" and app.resultado.es_completo()
    assert F.leer_json(F.escribir_json(app.resultado)) == app.resultado


def test_minimizar_un_afd_muestra_las_particiones(app):
    cargar(app, ejercicio_192())
    app.convertir(False)
    app.usar_resultado()
    app.minimizar()
    textos = [c.value for c in app.detalle_conv.controls]
    assert any(t.startswith("Partición 0") for t in textos) and "→" in textos[0]
    assert len(app.resultado.estados) <= 5


def test_minimizar_un_afnd_se_rechaza_con_el_motivo(app):
    cargar(app, termina_en_01())
    app.minimizar()
    assert app.mensaje_conv.color == ui.ROJO and "Solo se simplifica un AFD" in app.mensaje_conv.value
    assert app.resultado is None


def test_las_clausuras_y_quitar_inaccesibles(app):
    cargar(app, anexo3())
    app.ver_clausuras()
    assert app.titulo_conv.value.startswith("λ-clausura") and app.resultado is None
    cargar(app, Automata_con_inaccesible())
    app.quitar_inaccesibles()
    assert "x" in app.detalle_conv.controls[0].value and "x" not in app.resultado.estados


def Automata_con_inaccesible():
    a = par_de_ceros()
    a.agregar_estado("x")
    a.agregar_transicion("x", "0", "q0")
    return a


def test_guardar_el_resultado_de_una_conversion(app):
    cargar(app, termina_en_01())
    app.convertir(False)
    app.campo_nombre_conv.value = "convertido"
    app.guardar_resultado()
    assert app.mensaje_conv.color == ui.VERDE
    assert F.leer_archivo(app.tmp / "salidas" / "convertido.json") == app.resultado


def test_una_conversion_sin_inicial_muestra_el_error(app):
    app.quitar_estado("q0")
    app.convertir(False)
    assert app.mensaje_conv.color == ui.ROJO and app.resultado is None


# ---------------------------------------------------------------------------
# Operaciones sobre cadenas y lenguajes (Práctica 1)
# ---------------------------------------------------------------------------

def test_prefijos_sufijos_y_subcadenas(app):
    app.entrada1.value = "abc"
    app.calcular1()
    assert len(app.resultados1.controls) == 3 and not app.guardar1.disabled
    assert "Prefijos: 4" in app.resumen1.value and "Subcadenas distintas: 7" in app.resumen1.value
    app.guardar_op1()
    assert any((app.tmp / "salidas").glob("prefijos_sufijos_subcadenas_*.txt"))
    app.entrada1.value = "λ" * 1
    app.calcular1()
    assert app.mensaje1.color == ui.ROJO and app.guardar1.disabled


def test_cerraduras_de_kleene_y_positiva(app):
    app.alfabeto2.value = "a, b"
    app.longitud2.value = "2"
    app.calcular2(False)(None)
    assert "7 cadenas" in app.resumen2.value and not app.guardar2.disabled
    app.calcular2(True)(None)
    assert "6 cadenas" in app.resumen2.value
    app.guardar_op2()
    assert any((app.tmp / "salidas").glob("cerradura_positiva_*.txt"))
    app.longitud2.value = "mucho"
    app.calcular2(False)(None)
    assert app.mensaje2.color == ui.ROJO and app.guardar2.disabled
    app.longitud2.value = "1000"
    app.alfabeto2.value = "a, b, c"
    app.calcular2(False)(None)
    assert app.mensaje2.color == ui.ROJO and "máximo permitido" in app.mensaje2.value


# ---------------------------------------------------------------------------
# Recuadro del diagrama
# ---------------------------------------------------------------------------

def test_un_diagrama_ancho_se_reduce_hasta_la_mitad_para_caber_en_el_recuadro():
    import dibujo as D
    grande = D.svg_automata(F.leer_archivo(RAIZ_REAL / "automatas" / "lista2-afd" / "Ej_109_contiene_abbcb_y_cbaabb.jff"))
    imagen = ui.imagen_del_automata(grande, 700, 380).content.content
    w, h = D.dimensiones_svg(grande)
    escala = max(0.5, min(1.0, (700 - 24) / w))
    assert w > 700 and 0.5 <= escala < 1.0
    assert imagen.width == pytest.approx(w * escala) and imagen.height == pytest.approx(h * escala)
    chico = D.svg_automata(par_de_ceros())
    assert ui.imagen_del_automata(chico).content.content.width == D.dimensiones_svg(chico)[0]


# ---------------------------------------------------------------------------
# Práctica 3
# ---------------------------------------------------------------------------

def test_la_pantalla_tiene_la_pestana_de_varias_cadenas(app):
    pestanas = app.page.controls[-1].content.controls[0].tabs
    assert [t.label for t in pestanas][4] == "Varias cadenas"


def test_la_clausura_de_un_estado_elegido_se_muestra(app):
    cargar(app, anexo3())
    app.campo_estado_clausura.value = "q0"
    app.ver_clausura_de_estado()
    assert app.titulo_conv.value == "λ-clausura de q0"
    assert "Cl(q0) = {q0, q1}" in app.detalle_conv.controls[0].value
    app.campo_estado_clausura.value = "zz"
    app.ver_clausura_de_estado()
    assert app.mensaje_conv.color == ui.ROJO and "zz" in app.mensaje_conv.value


def test_quitar_lambda_muestra_lo_que_se_anade_y_los_estados_que_pasan_a_aceptacion(app):
    cargar(app, anexo3())
    app.quitar_lambda()
    textos = [c.value for c in app.detalle_conv.controls]
    assert any("Transiciones λ que desaparecen" in t for t in textos)
    assert any("Transiciones que se añaden" in t for t in textos)
    assert any("pasa a ser de aceptación" in t or "Ningún estado pasa" in t for t in textos)
    assert app.resultado is not None and not app.resultado.tiene_lambda


def test_la_construccion_de_subconjuntos_se_muestra_renglon_por_renglon(app):
    cargar(app, ejercicio_192())
    app.convertir(False)
    conv, pasos = app.subconjuntos
    assert len(pasos) > 2
    assert "Renglón 1 de" in " ".join(getattr(c, "value", "") or "" for c in app.detalle_conv.controls[1].controls)
    app._dibujar_subconjuntos(2)
    tabla = app.detalle_conv.controls[2].controls[0]
    assert len(tabla.rows) == 2
    app._dibujar_subconjuntos(len(pasos))
    assert len(app.detalle_conv.controls[2].controls[0].rows) == len(pasos)
    assert any("de aceptación" in (getattr(c, "value", "") or "") for c in app.detalle_conv.controls)


def test_comparar_dos_afd_por_sus_minimos(app):
    cargar(app, par_de_ceros(), "a")
    otro = par_de_ceros()
    otro.nombre = "b"
    F.guardar_archivo(otro, app.tmp / "b.json")
    app.campo_ruta_b.value = str(app.tmp / "b.json")
    app.comparar_con_otro()
    assert app.titulo_conv.value.startswith("Equivalencia")
    assert any("SON EQUIVALENTES" in (c.value or "") for c in app.detalle_conv.controls)
    app.campo_ruta_b.value = str(app.tmp / "no_existe.json")
    app.comparar_con_otro()
    assert app.mensaje_conv.color == ui.ROJO


def test_validar_varias_cadenas_y_guardar_el_informe(app):
    cargar(app, termina_en_01())
    app.campo_cadenas.value = "01\n10\n\nλ\n2"
    app.validar_cadenas()
    assert "5 cadenas" in app.resumen_lote.value or "4 cadenas" in app.resumen_lote.value
    assert not app.boton_informe.disabled
    app.campo_nombre_informe.value = "lote"
    app.guardar_informe_de_lote()
    assert app.mensaje_lote.color == ui.VERDE
    texto = (app.tmp / "salidas" / "lote.txt").read_text(encoding="utf-8")
    assert "ACEPTADA" in texto and "RECHAZADA" in texto and "ERROR" in texto


def test_cargar_un_archivo_de_cadenas(app):
    archivo = app.tmp / "cadenas.txt"
    archivo.write_text("01\n10\n", encoding="utf-8")
    app.campo_ruta_cadenas.value = str(archivo)
    app.cargar_archivo_de_cadenas()
    assert app.campo_cadenas.value == "01\n10" and app.mensaje_lote.color == ui.VERDE
    app.campo_ruta_cadenas.value = str(app.tmp / "no_existe.txt")
    app.cargar_archivo_de_cadenas()
    assert app.mensaje_lote.color == ui.ROJO


def test_validar_sin_cadenas_avisa(app):
    app.campo_cadenas.value = "  \n"
    app.validar_cadenas()
    assert app.mensaje_lote.color == ui.ROJO
