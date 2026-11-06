"""Lógica de la interfaz que no depende de Flet.

app.py solo arma la pantalla y llama a estas funciones y a las de automata.py, formatos.py
y lenguajes.py; lo que se puede probar sin abrir una ventana vive aquí.
"""

import random
import re
import zlib
from datetime import datetime
from pathlib import Path

import formatos as F
from automata import LIMITE_CAMINOS, Automata, AutomataInvalido, formatear_conjunto
from construcciones import cadenas_hasta
from dibujo import svg_automata
from lenguajes import LAMBDA, parsear_alfabeto

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_AUTOMATAS = RAIZ / "automatas"
CARPETA_SALIDAS = RAIZ / "salidas"
CAMINOS_VISIBLES = 200          # caminos que se muestran en pantalla (se enumeran hasta LIMITE_CAMINOS)


def automata_nuevo():
    """Punto de partida para definir un autómata: alfabeto {a, b} y un estado inicial q0."""
    return Automata("ab", ["q0"], "q0", nombre="nuevo")


# ---------------------------------------------------------------------------
# Edición
# ---------------------------------------------------------------------------

def nombre_de_estado_libre(a):
    """q0, q1, ... el primero que no está en uso."""
    n = len(a.estados)
    while f"q{n}" in a.estados:
        n += 1
    return f"q{n}"


def aplicar_alfabeto(a, texto):
    """Cambia el alfabeto al que describe el texto ("a, b" o "ab"). Los símbolos que ya no
    están se quitan junto con sus transiciones. Devuelve (agregados, quitados, transiciones perdidas)."""
    nuevos = parsear_alfabeto(texto)          # ValueError si está vacío o tiene un símbolo no válido
    quitados = [s for s in a.alfabeto if s not in nuevos]
    perdidas = sum(1 for _, lee, _ in a.transiciones() if lee in quitados)
    for s in quitados:
        a.quitar_simbolo(s)
    agregados = [s for s in nuevos if s not in a.alfabeto]
    for s in agregados:
        a.agregar_simbolo(s)
    a.alfabeto = list(nuevos)                 # en el orden en que se escribió
    return agregados, quitados, perdidas


def _es_un_solo_grupo(texto):
    """True si la llave de apertura del principio se cierra justo en la última letra: {q0,q1}
    es un grupo, pero {q0}, {q1} son dos nombres."""
    if not (texto.startswith("{") and texto.endswith("}")):
        return False
    profundidad = 0
    for i, c in enumerate(texto):
        profundidad += (c == "{") - (c == "}")
        if profundidad == 0 and i < len(texto) - 1:
            return False
    return profundidad == 0


def destinos_de_texto(a, texto):
    """Estados que nombra el texto de una celda de la tabla ("q0, q1", "{q0,q1}" o "∅").

    Los nombres se separan por comas, punto y coma o espacios, salvo dentro de llaves, para
    que se pueda escribir un estado como {q0,q1} (así se llaman los del AFD de una conversión).
    """
    texto = (texto or "").strip()
    if texto in ("", "∅", "-"):
        return []
    if texto in a.estados:
        return [texto]
    if _es_un_solo_grupo(texto):
        texto = texto[1:-1]
    nombres, actual, profundidad = [], "", 0
    for c in texto:
        profundidad += (c == "{") - (c == "}")
        if profundidad <= 0 and (c in ",; " or c.isspace()):
            if actual:
                nombres.append(actual)
            actual = ""
        else:
            actual += c
    if actual:
        nombres.append(actual)
    for nombre in nombres:
        if nombre not in a.estados:
            raise AutomataInvalido(f"El estado «{nombre}» no existe.")
    return list(dict.fromkeys(nombres))


def texto_de_destinos(a, estado, lee):
    return ", ".join(a.destinos(estado, lee))


def fijar_transicion(a, desde, lee, texto):
    """Reemplaza los destinos de (desde, lee) por los que nombra el texto (vacío o ∅ los quita)."""
    destinos = destinos_de_texto(a, texto)     # se valida todo antes de cambiar nada
    if a.destinos(desde, lee):
        a.quitar_transicion(desde, lee)
    for destino in destinos:
        a.agregar_transicion(desde, lee, destino)
    return destinos


# ---------------------------------------------------------------------------
# Archivos
# ---------------------------------------------------------------------------

def archivos_disponibles():
    """Archivos de autómatas que se pueden cargar: (etiqueta, ruta), los de automatas/ y salidas/."""
    encontrados = []
    for carpeta in (CARPETA_AUTOMATAS, CARPETA_SALIDAS):
        if carpeta.is_dir():
            encontrados += [p for p in carpeta.rglob("*") if p.suffix.lower().lstrip(".") in F.FORMATOS]
    return [(p.relative_to(RAIZ).as_posix(), p) for p in sorted(encontrados, key=lambda p: p.as_posix().lower())]


def resolver_ruta(texto):
    """Ruta absoluta de lo que escribió el usuario (relativa a la carpeta del proyecto o absoluta)."""
    texto = (texto or "").strip().strip('"')
    if not texto:
        raise F.FormatoInvalido("Escribe la ruta de un archivo .jff, .json o .xml.")
    ruta = Path(texto)
    return ruta if ruta.is_absolute() else RAIZ / ruta


def cargar(texto_de_ruta):
    return F.leer_archivo(resolver_ruta(texto_de_ruta))


def nombre_de_archivo_valido(nombre):
    """Nombre seguro para un archivo dentro de salidas/ (sin carpetas ni extensión)."""
    base = Path((nombre or "").strip()).stem if "." in (nombre or "") else (nombre or "").strip()
    base = re.sub(r"[^\w\-]+", "_", base, flags=re.UNICODE).strip("_")
    if not base:
        raise F.FormatoInvalido("Escribe un nombre para el archivo.")
    return base[:80]


def guardar_en_salidas(a, nombre, formatos=F.FORMATOS):
    """Guarda el autómata en salidas/ en los formatos pedidos; devuelve las rutas relativas."""
    base = nombre_de_archivo_valido(nombre)
    CARPETA_SALIDAS.mkdir(exist_ok=True)
    rutas = []
    for formato in formatos:
        ruta = CARPETA_SALIDAS / f"{base}.{formato}"
        F.guardar_archivo(a, ruta)
        rutas.append(ruta.relative_to(RAIZ).as_posix())
    return rutas


def guardar_diagrama(a, nombre, activos=(), resaltadas=()):
    """Guarda el diagrama del autómata como .svg en salidas/."""
    base = nombre_de_archivo_valido(nombre)
    CARPETA_SALIDAS.mkdir(exist_ok=True)
    ruta = CARPETA_SALIDAS / f"{base}.svg"
    ruta.write_text(svg_automata(a, activos, resaltadas), encoding="utf-8", newline="\n")
    return ruta.relative_to(RAIZ).as_posix()


# ---------------------------------------------------------------------------
# Textos de la simulación
# ---------------------------------------------------------------------------

def _flechas(tomadas):
    return ", ".join(f"{d} –{l if l else LAMBDA}→ {h}" for d, l, h in tomadas)


def titulo_de_paso(recorrido, k):
    p = recorrido.pasos[k]
    return "Inicio" if p.simbolo is None else f"Paso {k}: lee «{p.simbolo}»"


def descripcion_de_paso(a, recorrido, k):
    """Texto del paso k: estado actual, transiciones tomadas y estados activos."""
    p = recorrido.pasos[k]
    activos = formatear_conjunto(a._ordenar(p.conjunto))
    if p.simbolo is None:
        partes = [f"Se parte del estado inicial {a.inicial}."]
        if a.tiene_lambda:
            partes.append(f"Antes de la λ-clausura: {formatear_conjunto(a._ordenar(p.antes))}.")
        partes.append(f"λ-clausura: {activos}." if a.tiene_lambda else f"Estado actual: {activos}.")
        if p.tomadas:
            partes.append(f"Transiciones λ: {_flechas(p.tomadas)}.")
        return " ".join(partes)
    partes = [f"Se lee «{p.simbolo}»."]
    partes.append(f"Transiciones tomadas: {_flechas(p.tomadas)}." if p.tomadas else "No hay ninguna transición posible.")
    if a.tiene_lambda:
        partes.append(f"Antes de la λ-clausura: {formatear_conjunto(a._ordenar(p.antes))}. "
                      f"Después de la λ-clausura: {activos}.")
    partes.append(f"Estados activos: {activos}." if len(p.conjunto) != 1 else f"Estado actual: {activos}.")
    if not p.conjunto:
        partes.append("El autómata se bloqueó: la cadena se rechaza.")
    return " ".join(partes)


def lineas_de_traza(a, recorrido):
    """Una línea por paso, para la traza completa del recorrido."""
    return [f"{titulo_de_paso(recorrido, k)}  →  {formatear_conjunto(a._ordenar(p.conjunto))}"
            for k, p in enumerate(recorrido.pasos)]


def veredicto(a, recorrido):
    """(texto corto, explicación) del resultado final."""
    final = recorrido.pasos[-1].conjunto
    if recorrido.aceptada:
        en = ", ".join(a._ordenar(final & a.aceptacion))
        return "ACEPTADA", f"Terminó de leer la cadena en un estado de aceptación ({en})."
    if not recorrido.consumida:
        return "RECHAZADA", "El autómata se bloqueó antes de terminar de leer la cadena."
    if not final:
        return "RECHAZADA", "Al leer el último símbolo no quedó ningún estado activo."
    return "RECHAZADA", f"Terminó de leer la cadena en {formatear_conjunto(a._ordenar(final))}, que no es de aceptación."


def caminos_en_texto(a, w):
    """Los caminos de cómputo de w, uno por línea: (líneas, mensaje sobre el límite o '')."""
    resultado = a.caminos(w)
    lineas = []
    for i, c in enumerate(resultado.caminos[:CAMINOS_VISIBLES], start=1):
        ruta = c.estados[0] + "".join(f" –{l if l else LAMBDA}→ {h}" for (_, l, h) in c.transiciones)
        lineas.append(f"{i}. {ruta}  [{'ACEPTA' if c.aceptado else 'rechaza'}: {c.motivo}]")
    aviso = ""
    if resultado.truncado:
        aviso = f"Hay más de {LIMITE_CAMINOS:,} caminos; se enumeraron solo los primeros."
    elif len(resultado.caminos) > CAMINOS_VISIBLES:
        aviso = f"Hay {len(resultado.caminos):,} caminos; se muestran los primeros {CAMINOS_VISIBLES}."
    return lineas, aviso


def texto_de_cadena(texto):
    """Cadena que escribió el usuario: «λ» o vacío es la cadena vacía."""
    texto = texto or ""
    return "" if texto.strip() == LAMBDA else texto


# ---------------------------------------------------------------------------
# Textos de las conversiones
# ---------------------------------------------------------------------------

def filas_de_clausuras(a):
    """(estado, λ-clausura) para cada estado."""
    return [(q, formatear_conjunto(cl)) for q, cl in a.clausuras().items()]


def filas_de_subconjuntos(a, conversion):
    """(estado del AFD, conjunto de estados del original) en el orden de la construcción."""
    return [(nombre, formatear_conjunto(a._ordenar(s))) for nombre, s in conversion.subconjuntos.items()]


def lineas_de_particiones(resultado):
    """Una línea por ronda de la minimización."""
    lineas = []
    for i, ronda in enumerate(resultado.rondas):
        clases = "  ".join("{" + ", ".join(c) + "}" for c in ronda)
        lineas.append(f"Partición {i}: {clases}")
    if resultado.trampa:
        lineas.append(f"(El AFD es parcial: se agregó temporalmente el estado trampa {resultado.trampa}.)")
    return lineas


# ---------------------------------------------------------------------------
# Cadenas de prueba y detalle de las conversiones (para documentar cada autómata)
# ---------------------------------------------------------------------------

def traza_compacta(a, recorrido):
    """El recorrido en una línea: {q0} –0→ {q0,q1} –1→ ∅ (conjuntos de estados activos tras cada símbolo)."""
    partes = [formatear_conjunto(a._ordenar(recorrido.pasos[0].conjunto))]
    for p in recorrido.pasos[1:]:
        partes.append(f"–{p.simbolo}→ {formatear_conjunto(a._ordenar(p.conjunto))}")
    return " ".join(partes)


def _elegir_por_longitud(grupos, cantidad, azar):
    """Elige `cantidad` cadenas repartidas entre las longitudes disponibles, de la más corta a la más larga."""
    longitudes = sorted(grupos)
    if not longitudes:
        return []
    elegidas = []
    if len(longitudes) >= cantidad:
        objetivos = [longitudes[round(i * (len(longitudes) - 1) / max(1, cantidad - 1))] for i in range(cantidad)]
    else:
        objetivos = [longitudes[i % len(longitudes)] for i in range(cantidad)]
    for n in objetivos:
        candidatas = [w for w in grupos[n] if w not in elegidas]
        if candidatas:
            elegidas.append(azar.choice(candidatas))
    return elegidas


def casos_de_prueba(a, validas=5, invalidas=5, semilla=""):
    """Cadenas válidas e inválidas de distinta longitud para probar un autómata (siempre las mismas para el
    mismo autómata y semilla). Si el lenguaje tiene menos cadenas válidas que las pedidas, devuelve las que hay.
    Entre las inválidas procura incluir una con la que el autómata se bloquea."""
    azar = random.Random(zlib.crc32(f"{semilla}|{a.nombre}".encode("utf-8")))
    limite = {1: 14, 2: 12, 3: 8}.get(len(a.alfabeto), 6)
    aceptadas, rechazadas, bloqueadas = {}, {}, {}
    for w in cadenas_hasta(a.alfabeto, limite):
        if a.acepta(w):
            aceptadas.setdefault(len(w), []).append(w)
        else:
            rechazadas.setdefault(len(w), []).append(w)
            if w and not a.simular(w).pasos[-1].conjunto and len(w) >= 2:
                bloqueadas.setdefault(len(w), []).append(w)
    base = [w for g in aceptadas.values() for w in g]
    for _ in range(800 if base else 0):                       # válidas más largas: se rodea una válida de símbolos al azar
        w = azar.choice(base)
        w = "".join(azar.choice(a.alfabeto) for _ in range(azar.randint(0, 4))) + w \
            + "".join(azar.choice(a.alfabeto) for _ in range(azar.randint(0, 4)))
        if limite < len(w) <= 14 and a.acepta(w) and w not in aceptadas.get(len(w), []):
            aceptadas.setdefault(len(w), []).append(w)
    buenas = _elegir_por_longitud(aceptadas, validas, azar)
    malas = _elegir_por_longitud(rechazadas, invalidas, azar)
    if bloqueadas and malas and not any(w in {x for g in bloqueadas.values() for x in g} for w in malas):
        corta = min(bloqueadas)
        malas[len(malas) // 2] = azar.choice(bloqueadas[corta])
    return sorted(set(buenas), key=lambda w: (len(w), w)), sorted(set(malas), key=lambda w: (len(w), w))


def detalle_de_subconjuntos(a, conversion):
    """Una línea por cada (estado del AFD, símbolo): de qué unión sale su destino. Para explicar paso a paso
    la construcción de subconjuntos."""
    lineas = []
    for nombre, subconjunto in conversion.subconjuntos.items():
        miembros = a._ordenar(subconjunto)
        for simbolo in a.alfabeto:
            partes = [formatear_conjunto(a.destinos(q, simbolo)) for q in miembros]
            union = a.clausura(a.mover(subconjunto, simbolo))
            lineas.append(f"δ'({nombre}, {simbolo}) = " + " ∪ ".join(f"δ({q},{simbolo})" for q in miembros)
                          + " = " + " ∪ ".join(partes) + f" = {formatear_conjunto(a._ordenar(union))}")
    return lineas


def trazas_de_subconjuntos(a, inicio, w):
    """Los conjuntos que recorre el AFD desde el estado `inicio` (un conjunto de estados) leyendo w."""
    actual = a.clausura(inicio)
    camino = [formatear_conjunto(a._ordenar(actual))]
    for simbolo in w:
        actual = a.clausura(a.mover(actual, simbolo))
        camino.append(formatear_conjunto(a._ordenar(actual)))
    return camino


# ---------------------------------------------------------------------------
# Práctica 3: eliminación de λ, subconjuntos y minimización paso a paso
# ---------------------------------------------------------------------------

def clausura_de_estado(a, estado):
    """Línea con la λ-clausura de un estado elegido: Cl(q) = {...} y las λ que se siguen."""
    a._exigir_valido()
    if estado not in a._indice:
        raise AutomataInvalido(f"El estado «{estado}» no existe en el autómata.")
    cl = a._ordenar(a.clausura({estado}))
    if len(cl) == 1:
        return f"Cl({estado}) = {formatear_conjunto(cl)}: {estado} no tiene transiciones λ hacia otros estados."
    aristas = [(q, "", r) for q in cl for r in a.destinos(q, "")]
    return f"Cl({estado}) = {formatear_conjunto(cl)}, por las transiciones {_flechas(aristas)}."


def lineas_de_quitar_lambda(a, resultado):
    """Explicación de la eliminación de λ: qué se añade, qué desaparece y qué estados pasan a aceptación."""
    lineas = ["Regla: δ'(q, a) = Cl(δ(Cl({q}), a)); q es de aceptación si Cl({q}) contiene un estado de aceptación."]
    for q in a.estados:
        lineas.append(f"Cl({q}) = {formatear_conjunto(resultado.clausuras[q])}")
    lineas.append(f"Transiciones λ que desaparecen ({len(resultado.quitadas)}): "
                  + (_flechas(resultado.quitadas) or "ninguna"))
    lineas.append(f"Transiciones que se añaden ({len(resultado.anadidas)}): " + (_flechas(resultado.anadidas) or "ninguna"))
    if resultado.nuevas_aceptacion:
        for q in resultado.nuevas_aceptacion:
            finales = [r for r in resultado.clausuras[q] if a.es_aceptacion(r)]
            lineas.append(f"{q} pasa a ser de aceptación: Cl({q}) contiene {', '.join(finales)}.")
    else:
        lineas.append("Ningún estado pasa a ser de aceptación.")
    return lineas


def filas_de_pasos_de_subconjuntos(pasos):
    """Filas (origen, símbolo, δ sin clausura, δ con clausura, destino, ¿nuevo?) de la tabla de subconjuntos."""
    filas = []
    for p in pasos:
        filas.append((p.origen, p.simbolo, formatear_conjunto(p.movido), formatear_conjunto(p.destino_conjunto),
                      p.destino or "(sin transición)", "sí" if p.nuevo else ""))
    return filas


def lineas_de_aceptacion(a, conversion):
    """Para cada estado del AFD, si es de aceptación y por qué."""
    return [a.razon_de_aceptacion(s) for s in conversion.subconjuntos.values()]


def lineas_de_equivalencia(resultado):
    """Resultado de comparar dos AFD por sus mínimos."""
    ma, mb = resultado.minimo_a, resultado.minimo_b
    lineas = [f"AFD mínimo de A: {len(ma.estados)} estados. AFD mínimo de B: {len(mb.estados)} estados.",
              "SON EQUIVALENTES. " + resultado.motivo if resultado.equivalentes else "NO SON EQUIVALENTES. " + resultado.motivo]
    if resultado.equivalentes:
        lineas.append("Correspondencia de estados (A → B): "
                      + ", ".join(f"{p} → {q}" for p, q in resultado.correspondencia.items()))
    return lineas


# ---------------------------------------------------------------------------
# Práctica 3: validación de varias cadenas
# ---------------------------------------------------------------------------

def leer_cadenas(texto):
    """Cadenas de un texto con una por línea. Las líneas en blanco se ignoran; la cadena vacía se
    escribe «λ». Devuelve la lista de cadenas en el orden del archivo."""
    cadenas = []
    for linea in (texto or "").splitlines():
        linea = linea.strip()
        if linea:
            cadenas.append(texto_de_cadena(linea))
    return cadenas


def cargar_cadenas(texto_de_ruta):
    """Lee un archivo de texto (UTF-8, con o sin BOM) con una cadena por línea."""
    ruta = resolver_ruta(texto_de_ruta)
    if not ruta.is_file():
        raise F.FormatoInvalido(f"No existe el archivo {ruta.name}.")
    return leer_cadenas(ruta.read_text(encoding="utf-8-sig"))


def validar_lote(a, cadenas):
    """Valida todas las cadenas. Devuelve [(cadena, veredicto, explicación)] con veredicto
    ACEPTADA, RECHAZADA o ERROR (símbolo fuera del alfabeto o cadena demasiado larga); un error en una
    cadena no detiene a las demás."""
    a._exigir_valido()
    resultados = []
    for w in cadenas:
        try:
            corto, explicacion = veredicto(a, a.simular(w))
        except ValueError as error:          # SimboloFueraDelAlfabeto y LimiteExcedido son ValueError
            corto, explicacion = "ERROR", str(error)
        resultados.append((w, corto, explicacion))
    return resultados


def informe_de_lote(a, resultados, origen=""):
    """Texto del informe: una línea por cadena y el resumen."""
    n = len(resultados)
    cuenta = {v: sum(1 for _, x, _ in resultados if x == v) for v in ("ACEPTADA", "RECHAZADA", "ERROR")}
    lineas = [f"Informe de validación — autómata «{a.nombre or 'sin nombre'}» ({a.tipo})",
              f"Origen de las cadenas: {origen or 'texto escrito en la aplicación'}",
              f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for i, (w, v, explicacion) in enumerate(resultados, start=1):
        lineas.append(f"{i}. {w if w else LAMBDA}\t{v}\t{explicacion}")
    lineas += ["", f"Total: {n}. Aceptadas: {cuenta['ACEPTADA']}. Rechazadas: {cuenta['RECHAZADA']}. Con error: {cuenta['ERROR']}."]
    return "\n".join(lineas) + "\n"


def guardar_informe(a, resultados, nombre, origen=""):
    """Guarda el informe en salidas/ como .txt; devuelve la ruta relativa."""
    base = nombre_de_archivo_valido(nombre)
    CARPETA_SALIDAS.mkdir(exist_ok=True)
    ruta = CARPETA_SALIDAS / f"{base}.txt"
    ruta.write_text(informe_de_lote(a, resultados, origen), encoding="utf-8", newline="\n")
    return ruta.relative_to(RAIZ).as_posix()
