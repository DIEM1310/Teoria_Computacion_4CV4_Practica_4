"""Genera los autómatas de la Lista 3 y las guías para hacerlos en JFLAP.

Uso, desde la raíz del repositorio:

    python herramientas/generar_lista3.py                 # archivos y guías
    python herramientas/generar_lista3.py --solo-guias    # solo las guías (docs/guia-jflap/)
    python herramientas/generar_lista3.py --sobrescribir  # reescribe también los .jff que ya existan

Los .jff que ya existan (por ejemplo, los que se dibujaron en JFLAP) NO se reescriben, salvo con
--sobrescribir; su .json y su .xml siempre se generan a partir del .jff que haya en la carpeta.
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import construcciones as C                                    # noqa: E402
import controlador as K                                       # noqa: E402
import ejercicios as E                                        # noqa: E402
import expresiones as X                                       # noqa: E402
import formatos as F                                          # noqa: E402
from automata import cadena_distintiva, formatear_conjunto    # noqa: E402
from lenguajes import LAMBDA                                  # noqa: E402

AUT = RAIZ / "automatas"
GUIA = RAIZ / "docs" / "guia-jflap"


# ---------------------------------------------------------------------------
# Archivos
# ---------------------------------------------------------------------------

def escribir_archivos(sobrescribir=False):
    nuevos = existentes = 0
    for e in E.ENTREGAS:
        a = e.fabrica()
        a.nombre = e.nombre
        ruta = AUT / e.carpeta / f"{e.nombre}.jff"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        if ruta.exists() and not sobrescribir:
            existentes += 1
        else:
            F.guardar_archivo(a, ruta)
            nuevos += 1
        leido = F.leer_archivo(ruta)
        for extension in (".json", ".xml"):
            F.guardar_archivo(leido, ruta.with_suffix(extension))
    print(f"{nuevos} .jff escritos, {existentes} ya existían y se respetaron; .json y .xml de los {len(E.ENTREGAS)}.")


# ---------------------------------------------------------------------------
# Piezas de Markdown
# ---------------------------------------------------------------------------

def tabla(encabezados, filas):
    lineas = ["| " + " | ".join(encabezados) + " |", "|" + "---|" * len(encabezados)]
    lineas += ["| " + " | ".join(str(c) for c in fila) + " |" for fila in filas]
    return lineas


def cadena_md(w):
    return f"`{w if w else LAMBDA}`"


def etiqueta(a, q):
    marca = ("→" if q == a.inicial else "") + ("*" if a.es_aceptacion(q) else "")
    return f"`{marca} {q}`".replace("` ", "`") if marca else f"`{q}`"


def tabla_de_transiciones(a):
    columnas, filas = a.tabla()
    cuerpo = [[etiqueta(a, q)] + [", ".join(f[c]) or "∅" for c in columnas] for q, f in filas]
    return tabla(["Estado"] + [c or LAMBDA for c in columnas], cuerpo) + \
        ["", "`→` estado inicial, `*` estado de aceptación, `∅` ninguna transición."]


def tabla_de_casos(a, validas=5, invalidas=5, mostrar_caminos=None):
    """Casos de prueba con el resultado esperado y el recorrido (conjunto de estados activos tras cada símbolo)."""
    buenas, malas = K.casos_de_prueba(a, validas, invalidas)
    con_caminos = a.tipo != "AFD" if mostrar_caminos is None else mostrar_caminos
    filas = []
    for etiqueta_tipo, grupo in (("válida", buenas), ("inválida", malas)):
        for w in grupo:
            r = a.simular(w)
            fila = [etiqueta_tipo, cadena_md(w), "acepta" if r.aceptada else "rechaza", K.traza_compacta(a, r)]
            if con_caminos:
                c = a.caminos(w, limite=500)
                fila.append(f"{len(c.caminos)}{'+' if c.truncado else ''} (aceptan: {sum(x.aceptado for x in c.caminos)})")
            filas.append(fila)
    encabezado = ["Tipo", "Cadena", "Esperado", "Recorrido (estados activos tras cada símbolo)"] + (["Caminos"] if con_caminos else [])
    lineas = tabla(encabezado, filas)
    if len(buenas) < validas:
        lineas += ["", f"*El lenguaje solo tiene {len(buenas)} cadena(s) válida(s); no se pueden dar {validas}.*"]
    return lineas


def archivos(e, extra=()):
    nombres = [f"`automatas/{e.carpeta}/{e.nombre}.jff`"] + [f"`automatas/{x.carpeta}/{x.nombre}.jff`" for x in extra]
    return "Archivo(s): " + ", ".join(nombres)


def datos(a):
    return f"{a.tipo} · {len(a.estados)} estados · {len(a.transiciones())} transiciones"


def con_nombre(e):
    a = e.fabrica()
    a.nombre = e.nombre
    return a


def lista_de_caminos(a, w, maximo=40):
    r = a.caminos(w, limite=2000)
    lineas = []
    for i, c in enumerate(r.caminos[:maximo], start=1):
        ruta = c.estados[0] + "".join(f" –{lee if lee else LAMBDA}→ {h}" for (_, lee, h) in c.transiciones)
        lineas.append(f"{i}. `{ruta}` — {'**acepta**' if c.aceptado else 'rechaza'} ({c.motivo})")
    if len(r.caminos) > maximo:
        lineas.append(f"… y {len(r.caminos) - maximo} caminos más ({sum(x.aceptado for x in r.caminos)} aceptan en total).")
    return lineas, r


def automata_lista2(numero):
    """AFD de la Lista 2 con ese número de ejercicio (de automatas/lista2-afd)."""
    ruta = next((AUT / "lista2-afd").glob(f"Ej_{numero}_*.jff"))
    return F.leer_archivo(ruta), ruta


# ---------------------------------------------------------------------------
# 151 a 161
# ---------------------------------------------------------------------------

LENGUAJE_DE_LA_FIGURA = {
    "158": "{01}: solo la cadena `01`.",
    "159": "`1*01`: cualquier cantidad de unos, luego `01`.",
    "160": "`01(0+1)*`: las cadenas que empiezan con `01`.",
    "161": "`(010)*(λ+01)`: repeticiones de `010`, y a lo más un `01` al final.",
}


def guia_simplificacion():
    L = ["# Guía 1: simplificar AFD (151 a 157) y describir AFN (158 a 161)", "",
         "Los ejercicios 151 a 155 piden dibujar el autómata de la tabla y **quitar los estados inaccesibles**; los 156 y 157, "
         "simplificarlo con una **partición** y/o quitando los inaccesibles. Para todos se da también el AFD mínimo (opcional en 151 a 155).", ""]
    for n in range(151, 158):
        orig = E.POR_NOMBRE[f"Ej_{n}_original"]
        a = con_nombre(orig)
        inaccesibles = [q for q in a.estados if q not in a.accesibles()]
        minimo = E.POR_NOMBRE[f"Ej_{n}_minimo"]
        extra = [E.POR_NOMBRE[f"Ej_{n}_sin_inaccesibles"]] if f"Ej_{n}_sin_inaccesibles" in E.POR_NOMBRE else []
        L += [f"## Ejercicio {n}", "", archivos(orig, extra + [minimo]), "", f"**Autómata del enunciado** — {datos(a)}", ""]
        L += tabla_de_transiciones(a) + [""]
        if inaccesibles:
            L += [f"**Estados inaccesibles:** {', '.join(inaccesibles)} (ningún camino desde {a.inicial} llega a ellos).", ""]
            L += [f"**Sin inaccesibles** — {datos(extra[0].fabrica())}", ""] + tabla_de_transiciones(extra[0].fabrica()) + [""]
        else:
            L += ["**Estados inaccesibles:** ninguno; todos se alcanzan desde el inicial. Quitarlos no cambia el autómata.", ""]
        part = a.particiones()
        L += ["**Partición (método de refinamiento).** La primera ronda separa aceptación de no aceptación; cada ronda separa los "
              "estados que, con algún símbolo, van a clases distintas; termina cuando ya no cambia.", ""]
        L += [f"- {x}" for x in K.lineas_de_particiones(part)] + [""]
        m = minimo.fabrica()
        L += [f"**AFD mínimo** — {datos(m)}. Los estados de una misma clase son equivalentes.", ""] + tabla_de_transiciones(m) + [""]
        L += ["**Cadenas de prueba** (valen para el original y para el simplificado: reconocen el mismo lenguaje).", ""] + tabla_de_casos(a) + [""]
    L += ["# Ejercicios 158 a 161: qué hace cada autómata", "",
          "Aunque el enunciado los llama AFN, **ninguno tiene dos transiciones con el mismo símbolo desde un estado**: "
          "son AFD parciales (si falta la transición, la cadena se rechaza).", ""]
    for n in range(158, 162):
        e = E.POR_NOMBRE[f"Ej_{n}_figura"]
        a = con_nombre(e)
        L += [f"## Ejercicio {n}", "", archivos(e), "", f"{datos(a)}. **Lenguaje:** {LENGUAJE_DE_LA_FIGURA[str(n)]}", ""]
        L += tabla_de_transiciones(a) + [""] + tabla_de_casos(a) + [""]
    return L


# ---------------------------------------------------------------------------
# 162 a 190
# ---------------------------------------------------------------------------

PISTA = {
    "99": "se adivina en qué posición empieza el sufijo `001001`; hasta ahí el estado inicial lee cualquier símbolo",
    "102": "se adivina dónde empieza `abbbab`; antes y después se lee cualquier símbolo",
    "103": "se adivina dónde empieza `aabbba`; antes y después se lee cualquier símbolo",
    "106": "se adivina dónde empieza `1101001`; antes y después se lee cualquier símbolo",
    "118": "se adivina dónde empieza `ab` y dónde está la `a` final; `x` e `y` son lazos",
    "120": "al leer el primer símbolo se recuerda cuál fue; se adivina cuál es el último y se comprueba que es otro",
    "123": "se recuerda `w` (4 posibilidades) y se adivina dónde empieza la segunda `w`; `x` es un lazo",
}


def guia_afn_lista2():
    L = ["# Guía 2: AFN de los ejercicios de la Lista 2 (162 a 188) y ejercicios 189 y 190", "",
         "El enunciado numera 162 a 188 para los problemas 94 a 123 de la Lista 2 pero no dice cuáles; se hacen los obligatorios "
         "(con asterisco). «Cuando sea posible, busque que el diagrama del AFN sea más simple que el del AFD»: donde no lo es, "
         "se reutiliza el AFD (todo AFD es un AFN) y aquí se explica por qué.", "",
         "## Qué ejercicios de la Lista 2 tienen AFN nuevo", ""]
    filas = []
    for numero, clave in (("99", "Ej_099_afn_termina_en_001001"), ("102", "Ej_102_afn_contiene_abbbab"),
                          ("103", "Ej_103_afn_contiene_aabbba"), ("106", "Ej_106_afn_contiene_1101001"),
                          ("118", "Ej_118_afn_forma_axabya"), ("120", "Ej_120_afn_primer_y_ultimo_distintos"),
                          ("123", "Ej_123_afn_forma_wxw")):
        afn = con_nombre(E.POR_NOMBRE[clave])
        afd, _ = automata_lista2(f"{int(numero):03d}")
        mas_simple = len(afn.estados) < len(afd.estados) or len(afn.transiciones()) < len(afd.transiciones())
        filas.append([numero, f"{len(afn.estados)} / {len(afd.estados)}", f"{len(afn.transiciones())} / {len(afd.transiciones())}",
                      "sí" if mas_simple else "no"])
    L += tabla(["Ejercicio (Lista 2)", "Estados AFN / AFD", "Transiciones AFN / AFD", "AFN más simple"], filas) + [""]
    L += ["## Ejercicios en los que se reutiliza el AFD", ""]
    filas = []
    for numero, motivo in E.AFD_COMO_AFN.items():
        _, ruta = automata_lista2(f"{int(numero):03d}")
        filas.append([numero, motivo, f"`automatas/lista2-afd/{ruta.name}`"])
    L += tabla(["Ejercicio (Lista 2)", "Por qué el AFN no mejora al AFD", "Archivo que se reutiliza"], filas) + [""]
    for numero, clave in (("99", "Ej_099_afn_termina_en_001001"), ("102", "Ej_102_afn_contiene_abbbab"),
                          ("103", "Ej_103_afn_contiene_aabbba"), ("106", "Ej_106_afn_contiene_1101001"),
                          ("118", "Ej_118_afn_forma_axabya"), ("120", "Ej_120_afn_primer_y_ultimo_distintos"),
                          ("123", "Ej_123_afn_forma_wxw")):
        e = E.POR_NOMBRE[clave]
        a = con_nombre(e)
        afd, _ = automata_lista2(f"{int(numero):03d}")
        L += [f"## Ejercicio {numero} de la Lista 2 — AFN", "", archivos(e), "",
              f"{datos(a)} (el AFD de la Lista 2 tiene {len(afd.estados)} estados y {len(afd.transiciones())} transiciones).", "",
              f"**Idea de diseño:** {PISTA[numero]}.", ""] + tabla_de_transiciones(a) + [""] + tabla_de_casos(a) + [""]
    for numero, clave, w in (("189", "Ej_189_afn_00101_o_00110", "1001011"), ("190", "Ej_190_afn_11010_y_10100", "01101010100")):
        e = E.POR_NOMBRE[clave]
        a = con_nombre(e)
        L += [f"## Ejercicio {numero}", "", archivos(e), "", datos(a) + ".", ""]
        if numero == "189":
            L += ["**Idea de diseño:** los dos patrones comparten el prefijo `001`; después se bifurca: `01` o `10`. El estado inicial "
                  "tiene un lazo y adivina dónde empieza `001`.", ""]
        else:
            afd = C.afd_contiene_todos(["11010", "10100"], "01")
            L += ["**Idea de diseño:** se adivina cuál patrón aparece primero (dos ramas desde el inicial). Los patrones se traslapan: "
                  "`10100` puede empezar en el segundo símbolo de `11010` (comparten `1010`) o en el cuarto (comparten `10`); eso se "
                  "resuelve con dos transiciones desde la rama de `11010` hacia la cadena de `10100`. `10100` no puede terminar y "
                  "dejar a `11010` empezando dentro de él.",
                  f"Para comparar: el AFD mínimo tiene {len(afd.estados)} estados.", ""]
        L += tabla_de_transiciones(a) + [""]
        lineas, r = lista_de_caminos(a, w)
        L += [f"**Diagrama de transiciones de la palabra `{w}`** (todos los caminos de cómputo; {len(r.caminos)} en total, "
              f"{sum(x.aceptado for x in r.caminos)} aceptan). El árbol de ejecución se dibuja con una rama por cada camino:", ""] + lineas
        L += ["", "Conjuntos de estados activos: `" + K.traza_compacta(a, a.simular(w)) + "`", "",
              f"**Resultado:** {'ACEPTA' if a.acepta(w) else 'RECHAZA'} `{w}`.", ""]
        L += ["**Más cadenas de prueba**", ""] + tabla_de_casos(a) + [""]
    return L


# ---------------------------------------------------------------------------
# 192 a 195 y 260 a 263
# ---------------------------------------------------------------------------

def _consulta_en_texto(consulta):
    tipo = consulta[0]
    if tipo == "delta_hat":
        return f"δ̂({{{', '.join(consulta[1])}}}, {consulta[2]})"
    if tipo == "clausura":
        return f"Cl({{{', '.join(consulta[1])}}})"
    return f"δ({consulta[1]}, {consulta[2]})"


def bloque_de_conversion(num, nombre_afn, con_consultas=True):
    afn = con_nombre(E.POR_NOMBRE[nombre_afn])
    conv = afn.a_afd()
    afd = conv.afd
    afd.nombre = f"Ej_{num}_afd"
    minimo = afd.minimizar()
    L = [f"## Ejercicio {num}", "", archivos(E.POR_NOMBRE[nombre_afn], [E.POR_NOMBRE[f"Ej_{num}_afd"]]), "",
         f"**AFN** — {datos(afn)}", ""] + tabla_de_transiciones(afn) + [""]
    L += ["**Construcción de subconjuntos, paso a paso** (δ' es la función del AFD; el estado inicial es la λ-clausura del inicial)", ""]
    L += [f"- {x}" for x in K.detalle_de_subconjuntos(afn, conv)] + [""]
    L += [f"**AFD equivalente** — {datos(afd)}. Cada estado es un conjunto de estados del AFN.", ""] + tabla_de_transiciones(afd) + [""]
    L += [f"**Tamaños:** AFN {len(afn.estados)} estados → AFD {len(afd.estados)} estados (cota 2^{len(afn.estados)} = "
          f"{2 ** len(afn.estados):,}); el AFD mínimo tiene {len(minimo.estados)}.", ""]
    if con_consultas and num in E.CONSULTAS:
        L += ["**Preguntas del ejercicio.** δ̂ es la función extendida del AFN; δ̂_D la del AFD, cuyos estados son conjuntos: "
              "δ̂_D(Z, ω) es el conjunto al que llega el AFD empezando en el estado Z. Coinciden, porque δ_D(S, a) = ∪ δ(q, a).", ""]
        filas = []
        for inciso, consulta in E.CONSULTAS[num]:
            res = E.responder(afn, consulta)
            if consulta[0] == "delta_hat":
                camino = " → ".join(K.trazas_de_subconjuntos(afn, set(consulta[1]), consulta[2]))
                res_d = formatear_conjunto(afn._ordenar(res))
                filas.append([inciso, _consulta_en_texto(consulta), formatear_conjunto(afn._ordenar(res)), f"{res_d} (`{camino}`)"])
            else:
                filas.append([inciso, _consulta_en_texto(consulta), formatear_conjunto(afn._ordenar(res)), "—"])
        L += tabla(["Inciso", "Pregunta", "δ̂ en el AFN", "δ̂_D en el AFD (y el camino de conjuntos)"], filas) + [""]
    L += ["**Cadenas de prueba**", ""] + tabla_de_casos(afn) + [""]
    return L


def guia_conversiones():
    L = ["# Guía 3: de AFN a AFD (191 a 195 y 260 a 263)", "",
         "El ejercicio 191 es el enunciado de los 192 a 195 (hallar el AFD equivalente y calcular δ̂ y δ̂_D). En JFLAP: "
         "*Convert → Convert to DFA*, *Complete* para ver cada paso y *Done?* al terminar. JFLAP nombra los estados del AFD "
         "con los conjuntos y no agrega el estado ∅ (el AFD resultante puede quedar incompleto).", ""]
    for num in ("192", "193", "194", "195"):
        L += bloque_de_conversion(num, f"Ej_{num}_tabla")
    L += ["# Ejercicios 260 a 263", ""]
    L += bloque_de_conversion("260", "Ej_260_tabla", False)
    L += ["> En el 260 se pide describir a detalle cómo se obtuvo: la lista de «Construcción de subconjuntos» de arriba es esa descripción.", ""]
    L += bloque_de_conversion("261", "Ej_261_figura", False)
    L += ["> Los estados `q3` y `q4` no llevan a ningún estado de aceptación: son una rama muerta del AFN. Aparecen en los conjuntos "
          "del AFD pero no cambian el lenguaje, que son las cadenas que terminan en `00`.", ""]
    L += bloque_de_conversion("262", "Ej_262_ab_ba", False)
    L += ["> El AFN de {ab, ba} resulta determinista (un solo destino por símbolo); la conversión solo agrega el estado `∅` al "
          "completarlo (se pidió con `completo=True`). JFLAP dará el mismo autómata sin ese estado.", ""]
    L += bloque_de_conversion("263", "Ej_263_figura", False)
    return L


# ---------------------------------------------------------------------------
# 196 a 200
# ---------------------------------------------------------------------------

def guia_lambda():
    L = ["# Guía 4: AFND-λ (196 a 200)", "",
         "Estos ejercicios no tienen asterisco, pero el apartado 2.3 de la práctica pide la λ-clausura de cada estado de cada "
         "AFND-λ y la conversión AFND-λ → AFND → AFD, y sin ellos esa parte quedaría vacía. En JFLAP, la transición λ se escribe "
         "dejando vacío el campo de la etiqueta (JFLAP muestra λ).", ""]
    for num in ("196", "197", "198", "199", "200"):
        e = E.POR_NOMBRE[f"Ej_{num}_tabla"]
        a = con_nombre(e)
        sin = E.POR_NOMBRE[f"Ej_{num}_afnd"].fabrica()
        sin.nombre = f"Ej_{num}_afnd"
        conv = sin.a_afd()
        afd = conv.afd
        L += [f"## Ejercicio {num}", "", archivos(e, [E.POR_NOMBRE[f"Ej_{num}_afnd"], E.POR_NOMBRE[f"Ej_{num}_afd"]]), "",
              f"**AFND-λ** — {datos(a)}", ""] + tabla_de_transiciones(a) + [""]
        L += ["**λ-clausura de cada estado**", ""] + tabla(["Estado", "Cl(estado)"], [[f"`{q}`", c] for q, c in K.filas_de_clausuras(a)]) + [""]
        filas = []
        for inciso, consulta in E.CONSULTAS[num]:
            filas.append([inciso, _consulta_en_texto(consulta), formatear_conjunto(a._ordenar(E.responder(a, consulta)))])
        L += ["**Preguntas del ejercicio**", ""] + tabla(["Inciso", "Pregunta", "Respuesta"], filas) + [""]
        L += [f"**Paso 1: de AFND-λ a AFND** — δ'(q, a) = Cl(δ(Cl({{q}}), a)); q es de aceptación si su clausura contiene un estado de "
              f"aceptación. {datos(sin)}.", ""] + tabla_de_transiciones(sin) + [""]
        L += ["**Paso 2: de AFND a AFD** (subconjuntos)", ""] + [f"- {x}" for x in K.detalle_de_subconjuntos(sin, conv)] + [""]
        L += [f"**AFD** — {datos(afd)}. Tamaños: AFND-λ {len(a.estados)} → AFND {len(sin.estados)} → AFD {len(afd.estados)} "
              f"(cota 2^{len(sin.estados)} = {2 ** len(sin.estados)}).", ""] + tabla_de_transiciones(afd) + [""]
        L += ["**Cadenas de prueba** (en el AFND-λ)", ""] + tabla_de_casos(a) + [""]
    return L


# ---------------------------------------------------------------------------
# 254 a 258
# ---------------------------------------------------------------------------

def guia_expresiones():
    L = ["# Guía 5: expresión regular de un autómata (254 a 258)", "",
         "Método de **eliminación de estados**: se agregan un estado `inicio` y un estado `fin`, y se van eliminando los estados del "
         "autómata; al quitar `k`, cada camino `p → k → q` se reemplaza por `R(p,k) R(k,k)* R(k,q)`, que se une a lo que ya hubiera en `p → q`. "
         "JFLAP lo hace con *Convert → Convert FA to RE*. Las expresiones se comprobaron contra el autómata con todas las cadenas hasta longitud 9 o más.", ""]
    for n in range(254, 259):
        e = E.POR_NOMBRE[f"Ej_{n}_tabla"]
        a = con_nombre(e)
        er, orden, pasos = X.desde_automata(a)
        L += [f"## Ejercicio {n}", "", archivos(e), "", datos(a), ""] + tabla_de_transiciones(a) + [""]
        L += [f"**Orden de eliminación:** {', '.join(orden)}. Aristas que quedan tras cada paso:", ""]
        for p in pasos:
            aristas = "; ".join(f"{o} → {d}: `{t}`" for o, d, t in p.aristas)
            L += [f"- quitar `{p.eliminado}`: {aristas}"]
        L += ["", f"**Expresión regular:** `{er}`", ""]
        buenas, malas = K.casos_de_prueba(a)
        filas = [[tipo, cadena_md(w), "acepta" if a.acepta(w) else "rechaza", "sí" if X.acepta(er, w) else "no"]
                 for tipo, grupo in (("válida", buenas), ("inválida", malas)) for w in grupo]
        L += tabla(["Tipo", "Cadena", "Autómata", "La expresión la genera"], filas) + [""]
    return L


# ---------------------------------------------------------------------------
# Índice
# ---------------------------------------------------------------------------

NOMBRE_CORTO = {"099": "termina en 001001 (Lista 2)", "102": "contiene abbbab (Lista 2)", "103": "contiene aabbba (Lista 2)",
                "106": "contiene 1101001 (Lista 2)", "118": "forma axabya (Lista 2)", "120": "primer y último símbolo distintos (Lista 2)",
                "123": "forma wxw (Lista 2)", "189": "contiene 00101 o 00110", "190": "contiene 11010 y 10100",
                "192": "tabla del enunciado", "193": "tabla del enunciado", "194": "tabla del enunciado", "195": "tabla del enunciado",
                "260": "tabla del enunciado", "261": "figura: termina en 00", "262": "{ab, ba}", "263": "figura: termina en 01"}


def guia_indice():
    L = ["# Guía para hacer en JFLAP los autómatas de la Lista 3", "",
         "Cada guía da, por autómata: la tabla de transiciones, cadenas de prueba válidas e inválidas con el resultado esperado "
         "y el recorrido (los estados activos tras cada símbolo, para comparar con la simulación paso a paso de JFLAP), y, en las "
         "conversiones, los pasos y los tamaños.", "",
         "| Guía | Ejercicios |", "|---|---|",
         "| [01-simplificacion.md](01-simplificacion.md) | 151 a 157 (simplificar AFD), 158 a 161 (qué hace cada autómata) |",
         "| [02-afn-lista2-y-189-190.md](02-afn-lista2-y-189-190.md) | 162 a 188 (AFN de la Lista 2), 189 y 190 |",
         "| [03-afn-a-afd.md](03-afn-a-afd.md) | 191 a 195 y 260 a 263 (AFN a AFD) |",
         "| [04-afnd-lambda.md](04-afnd-lambda.md) | 196 a 200 (AFND-λ, opcionales) |",
         "| [05-expresiones-regulares.md](05-expresiones-regulares.md) | 254 a 258 (autómata a expresión regular) |", "",
         "## Cómo trabajar cada autómata", "",
         "1. En JFLAP: *File → New → Finite Automaton*. Crea los estados con la herramienta de estados; marca el inicial y los de "
         "aceptación con clic derecho. Usa **el mismo nombre de estado** que la tabla (clic derecho → *Set Name*).",
         "2. Prueba las cadenas: *Input → Step…* (paso a paso, muestra las ramas del no determinismo) y *Input → Multiple Run* "
         "(todas las cadenas de la tabla de una vez).",
         "3. Guarda como `automatas/<carpeta>/<nombre>.jff` con el nombre exacto que dice la guía.",
         "4. Para generar su `.json` y `.xml`, y comprobar que tu dibujo reconoce el lenguaje correcto, ejecuta "
         "`python herramientas/verificar_entregas.py --formatos`.", "",
         "Los `.jff` de esas carpetas **ya existen**, generados desde las tablas: puedes abrirlos en JFLAP para simular y hacer las "
         "capturas, o dibujar los tuyos y guardarlos con el mismo nombre (no se pisan).", "",
         "## Resumen de conversiones (para la tabla del apartado 2.4)", "",
         "Estados del AFN, del AFD que produce la construcción de subconjuntos, del AFD mínimo, y la cota 2ⁿ.", ""]
    filas = []
    for nombre in E.CONVERSIONES_AFN:
        num = nombre.split("_")[1]
        afn = E.POR_NOMBRE[nombre].fabrica()
        afd = E.POR_NOMBRE[f"Ej_{num}_afd"].fabrica()
        filas.append([num, NOMBRE_CORTO[num], len(afn.estados), len(afd.estados),
                      len(afd.minimizar().estados), f"{2 ** len(afn.estados):,}"])
    for nombre in E.CONVERSIONES_LAMBDA:
        num = nombre.split("_")[1]
        lam = E.POR_NOMBRE[nombre].fabrica()
        sin = E.POR_NOMBRE[f"Ej_{num}_afnd"].fabrica()
        afd = E.POR_NOMBRE[f"Ej_{num}_afd"].fabrica()
        filas.append([f"{num} (λ)", f"AFND-λ de {len(lam.estados)} estados", len(sin.estados), len(afd.estados),
                      len(afd.minimizar().estados), f"{2 ** len(sin.estados):,}"])
    L += tabla(["Ejercicio", "Autómata", "Estados AFN", "Estados AFD", "AFD mínimo", "Cota 2ⁿ"], filas) + [""]
    L += ["En ningún caso la cota se alcanza. La familia de la bibliografía en la que sí se alcanza (el n-ésimo símbolo desde el final "
          "es 1) está comprobada en `tests/test_automata.py` para n = 1 a 6.", ""]
    return L


GUIAS = {"README.md": guia_indice, "01-simplificacion.md": guia_simplificacion, "02-afn-lista2-y-189-190.md": guia_afn_lista2,
         "03-afn-a-afd.md": guia_conversiones, "04-afnd-lambda.md": guia_lambda, "05-expresiones-regulares.md": guia_expresiones}


def escribir_guias():
    GUIA.mkdir(parents=True, exist_ok=True)
    for nombre, construir in GUIAS.items():
        texto = "\n".join(construir()) + "\n"
        (GUIA / nombre).write_text(texto, encoding="utf-8", newline="\n")
        print(f"{(GUIA / nombre).relative_to(RAIZ)}  ({len(texto.splitlines())} líneas)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--solo-guias", action="store_true", help="no escribe autómatas, solo las guías")
    parser.add_argument("--sobrescribir", action="store_true", help="reescribe también los .jff que ya existan")
    args = parser.parse_args()
    if not args.solo_guias:
        escribir_archivos(args.sobrescribir)
    escribir_guias()


if __name__ == "__main__":
    main()
