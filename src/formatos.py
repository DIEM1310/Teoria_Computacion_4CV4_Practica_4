"""Lectura y escritura de autómatas en .jff (JFLAP), .json y .xml.

No depende de Flet. Los tres formatos representan los cinco componentes de la
quíntupla (alfabeto, estados, estado inicial, estados de aceptación y función de
transición) y la escritura y la lectura son operaciones inversas.

Convención para λ: la transición λ se escribe con la cadena vacía como símbolo leído
(`<read/>` en .jff, `"lee": ""` en .json y `lee=""` en .xml). Al leer también se
acepta el carácter «λ», que no puede ser símbolo del alfabeto, así que no hay ambigüedad.

Particularidad del .jff: JFLAP no guarda el alfabeto, así que al leerlo se deduce de los
símbolos de las transiciones. Un símbolo del alfabeto que ninguna transición lee se pierde
en ese formato (ver simbolos_que_el_jff_no_conserva) a menos que se indique con el
parámetro `alfabeto`. Las coordenadas x e y del .jff solo sirven para dibujar: se leen en
Automata.posiciones y no influyen en el alfabeto ni en la función de transición.
"""

import json
import re
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape, quoteattr

from automata import TIPO_AFND_LAMBDA, TIPOS, Automata, AutomataInvalido
from lenguajes import LAMBDA

LIMITE_BYTES = 5_000_000           # tamaño máximo de un archivo que se acepta leer
FORMATOS = ("jff", "json", "xml")
_ALIAS_TIPO = {**{t.upper(): t for t in TIPOS}, "AFND-Λ": TIPO_AFND_LAMBDA}   # sin distinguir mayúsculas
_ILEGAL_EN_XML = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f￾￿]")


class FormatoInvalido(ValueError):
    """El archivo no tiene el formato esperado o describe un autómata incorrecto."""


# ---------------------------------------------------------------------------
# Piezas comunes
# ---------------------------------------------------------------------------

def _simbolo_leido(texto):
    """Símbolo leído por una transición: "" para λ."""
    return "" if texto in ("", LAMBDA) else texto


def _comprobar_tipo(automata, declarado):
    """El tipo declarado debe ser igual o más general que el real: todo AFD es un AFND
    y todo AFND es un AFND-λ, pero no al revés."""
    if declarado is None:
        return
    declarado = _ALIAS_TIPO.get(str(declarado).upper(), declarado)
    if declarado not in TIPOS:
        raise FormatoInvalido(f"Tipo de autómata desconocido: {declarado!r}. Se esperaba uno de {', '.join(TIPOS)}.")
    if TIPOS.index(automata.tipo) > TIPOS.index(declarado):
        raise FormatoInvalido(f"El archivo declara un {declarado}, pero sus transiciones son las de un {automata.tipo}.")


def _construir(alfabeto, estados, inicial, aceptacion, transiciones, declarado=None, nombre=""):
    """Arma el autómata y traduce los errores de definición a FormatoInvalido."""
    try:
        a = Automata(alfabeto, estados, inicial, aceptacion, transiciones, nombre)
    except AutomataInvalido as error:
        raise FormatoInvalido(str(error)) from None
    _comprobar_tipo(a, declarado)
    return a


def _exigir_tamano(contenido):
    if len(contenido) > LIMITE_BYTES:
        raise FormatoInvalido(f"El archivo pesa más de {LIMITE_BYTES // 1_000_000} MB y no se lee.")


def _parsear_xml(contenido):
    """Parsea un XML rechazando las declaraciones DOCTYPE y ENTITY (evita la expansión de
    entidades). Acepta texto o bytes."""
    _exigir_tamano(contenido)
    if isinstance(contenido, str):
        contenido = re.sub(r"^﻿?\s*<\?xml[^>]*\?>", "", contenido, count=1)
        bruto = contenido.encode("utf-8")
    else:
        bruto = contenido
    if not bruto.strip():
        raise FormatoInvalido("El archivo está vacío.")
    if re.search(rb"<!\s*(DOCTYPE|ENTITY)", bruto, re.IGNORECASE):
        raise FormatoInvalido("No se aceptan archivos XML con declaraciones DOCTYPE o ENTITY.")
    try:
        return ElementTree.fromstring(bruto if isinstance(contenido, bytes) else contenido)
    except ElementTree.ParseError as error:
        raise FormatoInvalido(f"El archivo no es un XML válido: {error}.") from None


def _exigir_escribible_en_xml(automata):
    textos = list(automata.estados) + list(automata.alfabeto)
    for texto in textos:
        if _ILEGAL_EN_XML.search(texto):
            raise FormatoInvalido(f"El nombre {texto!r} tiene caracteres de control que XML no admite.")


def _booleano(texto, donde):
    t = (texto or "").strip().lower()
    if t in ("true", "1"):
        return True
    if t in ("false", "0", ""):
        return False
    raise FormatoInvalido(f"Valor lógico no válido en {donde}: {texto!r} (se esperaba true o false).")


def simbolos_que_el_jff_no_conserva(automata):
    """Símbolos del alfabeto que ninguna transición lee: el .jff no los guarda."""
    usados = {lee for _, lee, _ in automata.transiciones()}
    return [s for s in automata.alfabeto if s not in usados]


def posiciones_de_dibujo(automata):
    """Coordenadas para dibujar: las del autómata si las tiene todas y, si no, los estados
    repartidos en columnas según su distancia al estado inicial (de izquierda a derecha,
    como se dibuja un diagrama en JFLAP). Los inaccesibles quedan en la última columna."""
    if not automata.estados:
        return {}
    if all(q in automata.posiciones for q in automata.estados):
        return {q: automata.posiciones[q] for q in automata.estados}
    raiz = automata.inicial if automata.inicial in automata.estados else automata.estados[0]
    sucesores = {q: [] for q in automata.estados}
    for desde, _, hacia in automata.transiciones():
        sucesores[desde].append(hacia)
    nivel = {raiz: 0}
    cola = [raiz]
    for q in cola:
        for r in sucesores[q]:
            if r not in nivel:
                nivel[r] = nivel[q] + 1
                cola.append(r)
    ultimo = max(nivel.values()) + 1
    for q in automata.estados:
        nivel.setdefault(q, ultimo)
    columnas = {}
    for q in automata.estados:
        columnas.setdefault(nivel[q], []).append(q)
    alto = max(len(c) for c in columnas.values())
    posiciones = {}
    for n, estados in columnas.items():
        for j, q in enumerate(estados):
            posiciones[q] = (80.0 + 150.0 * n, round(80.0 + 110.0 * (j + (alto - len(estados)) / 2), 1))
    return posiciones


# ---------------------------------------------------------------------------
# .jff (JFLAP)
# ---------------------------------------------------------------------------

def escribir_jff(automata):
    _exigir_escribible_en_xml(automata)
    pos = posiciones_de_dibujo(automata)
    ids = {q: i for i, q in enumerate(automata.estados)}
    lineas = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
              "<structure>", "  <type>fa</type>", "  <automaton>"]
    for q in automata.estados:
        x, y = pos[q]
        lineas.append(f"    <state id=\"{ids[q]}\" name={quoteattr(q)}>")
        lineas.append(f"      <x>{x:.1f}</x><y>{y:.1f}</y>")
        if q == automata.inicial:
            lineas.append("      <initial/>")
        if automata.es_aceptacion(q):
            lineas.append("      <final/>")
        lineas.append("    </state>")
    for desde, lee, hacia in automata.transiciones():
        leido = f"<read>{escape(lee)}</read>" if lee else "<read/>"
        lineas.append(f"    <transition><from>{ids[desde]}</from><to>{ids[hacia]}</to>{leido}</transition>")
    lineas += ["  </automaton>", "</structure>", ""]
    return "\n".join(lineas)


def _texto(elemento, etiqueta):
    hijo = elemento.find(etiqueta)
    return None if hijo is None else (hijo.text or "")


def leer_jff(contenido, alfabeto=None, nombre=""):
    """Lee un .jff de JFLAP de tipo autómata finito.

    alfabeto: símbolos del alfabeto. Si no se da, se deduce de los símbolos que leen las
    transiciones, porque el .jff no lo guarda.
    """
    raiz = _parsear_xml(contenido)
    if raiz.tag != "structure":
        raise FormatoInvalido("No es un archivo de JFLAP: falta el elemento <structure>.")
    tipo = (_texto(raiz, "type") or "").strip()
    if tipo != "fa":
        raise FormatoInvalido(f"Solo se leen autómatas finitos (<type>fa</type>); este archivo es de tipo {tipo!r}.")
    automaton = raiz.find("automaton")
    if automaton is None:
        raise FormatoInvalido("Falta el elemento <automaton>.")

    nombres, estados, inicial, aceptacion, posiciones = {}, [], [], [], {}
    for s in automaton.findall("state"):
        ident = s.get("id")
        if ident is None or ident in nombres:
            raise FormatoInvalido(f"Estado sin id o con id repetido: {ident!r}.")
        nombre_estado = (s.get("name") or "").strip() or f"q{ident}"
        nombres[ident] = nombre_estado
        estados.append(nombre_estado)
        if s.find("initial") is not None:
            inicial.append(nombre_estado)
        if s.find("final") is not None:
            aceptacion.append(nombre_estado)
        try:
            posiciones[nombre_estado] = (float(_texto(s, "x")), float(_texto(s, "y")))
        except (TypeError, ValueError):
            pass            # las coordenadas son opcionales y no se interpretan
    if len(inicial) > 1:
        raise FormatoInvalido(f"Hay más de un estado inicial: {', '.join(inicial)}.")

    transiciones = []
    for t in automaton.findall("transition"):
        origen, destino, leido = _texto(t, "from"), _texto(t, "to"), t.find("read")
        if origen not in nombres or destino not in nombres:
            raise FormatoInvalido(f"Una transición usa un estado que no existe (from={origen!r}, to={destino!r}).")
        if leido is None:
            raise FormatoInvalido("Una transición no tiene el elemento <read>.")
        simbolo = _simbolo_leido(leido.text or "")
        if len(simbolo) > 1:
            raise FormatoInvalido(f"Una transición lee {simbolo!r}, que tiene varios símbolos; "
                                  "un autómata finito lee un símbolo por transición.")
        transiciones.append((nombres[origen], simbolo, nombres[destino]))

    if alfabeto is None:
        alfabeto = sorted({lee for _, lee, _ in transiciones if lee})
    a = _construir(alfabeto, estados, inicial[0] if inicial else None, aceptacion, transiciones, nombre=nombre)
    a.posiciones = posiciones if len(posiciones) == len(estados) else {}
    return a


# ---------------------------------------------------------------------------
# .json
# ---------------------------------------------------------------------------

def _agrupar(automata):
    """Transiciones agrupadas por (desde, lee), con la lista de destinos en el orden de Q."""
    grupos = {}
    for desde, lee, hacia in automata.transiciones():
        grupos.setdefault((desde, lee), []).append(hacia)
    return grupos


def escribir_json(automata):
    datos = {
        "tipo": automata.tipo,
        "alfabeto": list(automata.alfabeto),
        "estados": list(automata.estados),
        "inicial": automata.inicial,
        "aceptacion": [q for q in automata.estados if automata.es_aceptacion(q)],
        "transiciones": [{"desde": d, "lee": l, "hacia": h} for (d, l), h in _agrupar(automata).items()],
    }
    return json.dumps(datos, ensure_ascii=False, indent=2) + "\n"


def _lista_de_textos(valor, campo):
    if not isinstance(valor, list) or not all(isinstance(x, str) for x in valor):
        raise FormatoInvalido(f"El campo «{campo}» debe ser una lista de textos.")
    return valor


def leer_json(contenido, nombre=""):
    _exigir_tamano(contenido)
    try:
        datos = json.loads(contenido)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise FormatoInvalido(f"El archivo no es un JSON válido: {error}.") from None
    if not isinstance(datos, dict):
        raise FormatoInvalido("El JSON debe ser un objeto con los campos del autómata.")
    for campo in ("alfabeto", "estados", "aceptacion", "transiciones"):
        if campo not in datos:
            raise FormatoInvalido(f"Falta el campo «{campo}».")
    alfabeto = _lista_de_textos(datos["alfabeto"], "alfabeto")
    estados = _lista_de_textos(datos["estados"], "estados")
    aceptacion = _lista_de_textos(datos["aceptacion"], "aceptacion")
    inicial = datos.get("inicial")
    if inicial is not None and not isinstance(inicial, str):
        raise FormatoInvalido("El campo «inicial» debe ser un texto (o null si aún no se define).")
    if not isinstance(datos["transiciones"], list):
        raise FormatoInvalido("El campo «transiciones» debe ser una lista.")
    transiciones = []
    for i, t in enumerate(datos["transiciones"], start=1):
        if not isinstance(t, dict) or not all(k in t for k in ("desde", "lee", "hacia")):
            raise FormatoInvalido(f"La transición {i} debe tener «desde», «lee» y «hacia».")
        destinos = t["hacia"] if isinstance(t["hacia"], list) else [t["hacia"]]
        if not isinstance(t["desde"], str) or not isinstance(t["lee"], str) \
                or not all(isinstance(h, str) for h in destinos):
            raise FormatoInvalido(f"La transición {i} tiene campos que no son texto.")
        transiciones += [(t["desde"], _simbolo_leido(t["lee"]), h) for h in destinos]
    return _construir(alfabeto, estados, inicial or None, aceptacion, transiciones, datos.get("tipo"), nombre)


# ---------------------------------------------------------------------------
# .xml
# ---------------------------------------------------------------------------

def escribir_xml(automata):
    _exigir_escribible_en_xml(automata)
    lineas = ['<?xml version="1.0" encoding="UTF-8"?>', f"<automata tipo={quoteattr(automata.tipo)}>",
              "  <alfabeto>" + "".join(f"<simbolo>{escape(s)}</simbolo>" for s in automata.alfabeto) + "</alfabeto>",
              "  <estados>"]
    for q in automata.estados:
        marcas = (' inicial="true"' if q == automata.inicial else "") \
                 + (' aceptacion="true"' if automata.es_aceptacion(q) else "")
        lineas.append(f"    <estado nombre={quoteattr(q)}{marcas}/>")
    lineas += ["  </estados>", "  <transiciones>"]
    for desde, lee, hacia in automata.transiciones():
        lineas.append(f"    <transicion desde={quoteattr(desde)} lee={quoteattr(lee)} hacia={quoteattr(hacia)}/>")
    lineas += ["  </transiciones>", "</automata>", ""]
    return "\n".join(lineas)


def leer_xml(contenido, nombre=""):
    raiz = _parsear_xml(contenido)
    if raiz.tag != "automata":
        raise FormatoInvalido("El elemento raíz debe ser <automata>.")
    for hijo in ("alfabeto", "estados", "transiciones"):
        if raiz.find(hijo) is None:
            raise FormatoInvalido(f"Falta el elemento <{hijo}>.")
    alfabeto = [s.text or "" for s in raiz.find("alfabeto").findall("simbolo")]
    estados, inicial, aceptacion = [], [], []
    for e in raiz.find("estados").findall("estado"):
        nombre_estado = e.get("nombre")
        if nombre_estado is None:
            raise FormatoInvalido("Un <estado> no tiene el atributo «nombre».")
        estados.append(nombre_estado)
        if _booleano(e.get("inicial"), f"el estado {nombre_estado!r}"):
            inicial.append(nombre_estado)
        if _booleano(e.get("aceptacion"), f"el estado {nombre_estado!r}"):
            aceptacion.append(nombre_estado)
    if len(inicial) > 1:
        raise FormatoInvalido(f"Hay más de un estado inicial: {', '.join(inicial)}.")
    transiciones = []
    for t in raiz.find("transiciones").findall("transicion"):
        if any(t.get(k) is None for k in ("desde", "lee", "hacia")):
            raise FormatoInvalido("Una <transicion> debe tener los atributos «desde», «lee» y «hacia».")
        transiciones.append((t.get("desde"), _simbolo_leido(t.get("lee")), t.get("hacia")))
    return _construir(alfabeto, estados, inicial[0] if inicial else None, aceptacion, transiciones,
                      raiz.get("tipo"), nombre)


# ---------------------------------------------------------------------------
# Por formato y por archivo
# ---------------------------------------------------------------------------

_ESCRITORES = {"jff": escribir_jff, "json": escribir_json, "xml": escribir_xml}
_LECTORES = {"jff": leer_jff, "json": leer_json, "xml": leer_xml}


def _formato_de(ruta):
    extension = Path(ruta).suffix.lower().lstrip(".")
    if extension not in FORMATOS:
        raise FormatoInvalido(f"Extensión no admitida: {Path(ruta).suffix!r}. Se admiten .jff, .json y .xml.")
    return extension


def escribir(automata, formato):
    """Texto del autómata en el formato indicado ("jff", "json" o "xml")."""
    if formato not in _ESCRITORES:
        raise FormatoInvalido(f"Formato desconocido: {formato!r}.")
    return _ESCRITORES[formato](automata)


def leer(contenido, formato, **opciones):
    """Autómata a partir del contenido de un archivo en el formato indicado."""
    if formato not in _LECTORES:
        raise FormatoInvalido(f"Formato desconocido: {formato!r}.")
    return _LECTORES[formato](contenido, **opciones)


def guardar_archivo(automata, ruta):
    """Guarda el autómata; el formato lo da la extensión (.jff, .json o .xml)."""
    texto = escribir(automata, _formato_de(ruta))
    Path(ruta).write_text(texto, encoding="utf-8", newline="\n")


def leer_archivo(ruta, **opciones):
    """Lee un autómata; el formato lo da la extensión (.jff, .json o .xml)."""
    formato = _formato_de(ruta)
    ruta = Path(ruta)
    try:
        if ruta.stat().st_size > LIMITE_BYTES:
            raise FormatoInvalido(f"El archivo pesa más de {LIMITE_BYTES // 1_000_000} MB y no se lee.")
        contenido = ruta.read_bytes()
    except OSError as error:
        raise FormatoInvalido(f"No se pudo leer el archivo: {error.strerror or error}.") from None
    if formato == "json":
        try:
            contenido = contenido.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise FormatoInvalido("El archivo JSON no está en UTF-8.") from None
    return leer(contenido, formato, nombre=opciones.pop("nombre", ruta.stem), **opciones)
