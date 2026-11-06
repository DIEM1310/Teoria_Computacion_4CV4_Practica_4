"""Genera el punto de partida de docs/02-jflap.md con las tablas calculadas desde los autómatas entregados.

Uso, desde la raíz del repositorio:

    python herramientas/generar_docs.py            # escribe docs/02-jflap.md (no sobrescribe si ya existe)
    python herramientas/generar_docs.py --forzar   # lo reescribe (se pierde lo que se haya editado a mano)

Las tablas (clasificación, conversiones, λ-clausuras) salen de src/ejercicios.py, así que los números siempre coinciden con los
archivos de automatas/.
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import ejercicios as E           # noqa: E402
import formatos as F             # noqa: E402
from automata import formatear_conjunto   # noqa: E402

DESTINO = RAIZ / "docs" / "02-jflap.md"


def tabla(encabezados, filas):
    lineas = ["| " + " | ".join(encabezados) + " |", "|" + "---|" * len(encabezados)]
    return lineas + ["| " + " | ".join(str(c) for c in f) + " |" for f in filas]


def lista2(numero):
    return F.leer_archivo(next((RAIZ / "automatas" / "lista2-afd").glob(f"Ej_{int(numero):03d}_*.jff")))


def enlace(carpeta, nombre):
    return f"[{nombre}.jff](../automatas/{carpeta}/{nombre}.jff)"


def cuenta(automata):
    return f"{len(automata.estados)} / {len(automata.transiciones())}"


# Clasificación de la Lista 2 (ejercicios con asterisco). (sección, justificación de una línea)
JUSTIFICACION_LISTA2 = {
    "97": ("AFD", "Contador módulo 3; no hay nada que adivinar y el AFN no mejora al AFD."),
    "107": ("AFD", "Conjunción de dos condiciones (producto de autómatas): el AFN, unión de los dos órdenes posibles, tiene 15 estados y el AFD 13."),
    "109": ("AFD", "Con traslape, el AFN necesita además las cadenas fundidas: 40 estados contra 22 del AFD."),
    "111": ("AFD", "«Exactamente tres» exige comprobar que no hay una cuarta aparición: es un contador, y un AFN no puede comprobar ausencias."),
    "112": ("AFD", "«Exactamente dos»: contador de apariciones (sin traslape)."),
    "113": ("AFD", "«Exactamente dos»: contador de apariciones (con traslape)."),
    "116": ("Ninguna", "No es regular (Myhill-Nerode): no existe autómata finito de ningún tipo."),
    "121": ("AFD", "Posición módulo 3 y una bandera; no hay elección que adivinar."),
    "122": ("AFD", "Ventana de memoria acotada de los últimos símbolos."),
    "124": ("AFD", "Mecanismo físico determinista: el estado es la posición de las tres palancas y la última salida."),
    "125": ("AFD", "Teórico sobre un AFD genérico (complemento)."),
    "126": ("AFD", "Teórico sobre un AFD genérico (F = ∅)."),
    "127": ("AFD", "Teórico sobre un AFD genérico (F = Q)."),
    "128": ("AFD", "Se conserva el AFD del diagrama y cambian los estados de aceptación."),
    "131": ("AFD", "AFD dado; el estado depende solo del último símbolo."),
    "133": ("AFD", "AFD dado por tabla de transiciones."),
    "135": ("AFD", "Fases secuenciales sin ambigüedad (bᵐ a bⁿ)."),
    "137": ("AFD", "Prefijo fijo `ab`."),
    "139": ("AFD", "Paridad del número de ceros."),
    "141": ("AFD", "Se recuerda si el símbolo anterior fue un 0 pendiente de su 1."),
    "143": ("AFD", "Dos autómatas dados; el (b) es un AFD parcial."),
    "145": ("AFD", "Aritmética modular (módulo 5, leyendo de derecha a izquierda)."),
    "147": ("AFD", "Residuo módulo 6 (4 estados tras minimizar)."),
    "148": ("AFD", "Proceso determinista: cada evento lleva a un solo estado."),
    "149": ("AFD", "AFD dado por tabla; se piden valores de δ y δ̂."),
    "150": ("AFD", "AFD dado por tabla sobre {0, 1, a}; se piden valores de δ̂."),
}
AFN_DE_LISTA2 = {"99": "Ej_099_afn_termina_en_001001", "102": "Ej_102_afn_contiene_abbbab", "103": "Ej_103_afn_contiene_aabbba",
                 "106": "Ej_106_afn_contiene_1101001", "118": "Ej_118_afn_forma_axabya", "120": "Ej_120_afn_primer_y_ultimo_distintos",
                 "123": "Ej_123_afn_forma_wxw"}
ARCHIVO_LISTA2 = {"143": ["Ej_143a_todas_las_cadenas", "Ej_143b_empieza_y_termina_en_a_sin_bb"]}


def tabla_clasificacion_lista2():
    filas = []
    numeros = sorted(set(JUSTIFICACION_LISTA2) | set(AFN_DE_LISTA2) | {"97"}, key=int)
    for n in numeros:
        if n in AFN_DE_LISTA2:
            afn, afd = E.POR_NOMBRE[AFN_DE_LISTA2[n]].fabrica(), lista2(n)
            texto = (f"El AFN tiene {len(afn.estados)} estados y {len(afn.transiciones())} transiciones; el AFD, {len(afd.estados)} y "
                     f"{len(afd.transiciones())}. La elección que se adivina simplifica el diagrama. El AFD de la Lista 2 es su AFD equivalente.")
            archivos = enlace("lista3-afnd", AFN_DE_LISTA2[n]) + " y " + f"[AFD](../automatas/lista2-afd/{next((RAIZ / 'automatas' / 'lista2-afd').glob(f'Ej_{int(n):03d}_*.jff')).name})"
            filas.append([n, "**AFND**", archivos, texto])
            continue
        seccion, texto = JUSTIFICACION_LISTA2[n]
        if n in ARCHIVO_LISTA2:
            archivos = " y ".join(f"[{x}.jff](../automatas/lista2-afd/{x}.jff)" for x in ARCHIVO_LISTA2[n])
        elif seccion == "Ninguna" or n in ("125", "126", "127"):
            archivos = "—"
        else:
            nombre = next((RAIZ / "automatas" / "lista2-afd").glob(f"Ej_{int(n):03d}_*.jff")).name
            archivos = f"[{nombre}](../automatas/lista2-afd/{nombre})"
        filas.append([n, f"**{seccion}**" if seccion != "Ninguna" else "**Ninguna**", archivos, texto])
    return tabla(["Ej.", "Sección", "Archivo(s)", "Justificación"], filas)


def tabla_clasificacion_lista3():
    def fila(ejercicios, seccion, nombres, texto):
        archivos = ", ".join(enlace(E.POR_NOMBRE[x].carpeta, x) for x in nombres[:2]) + (" …" if len(nombres) > 2 else "")
        return [ejercicios, f"**{seccion}**", archivos, texto]
    filas = [
        fila("151–157", "AFD", [f"Ej_{n}_original" for n in range(151, 158)], "AFD dado por tabla (151–155) o figura (156–157), que se simplifica quitando estados inaccesibles y por partición."),
        fila("158–161", "AFD", [f"Ej_{n}_figura" for n in range(158, 162)],
             "El enunciado los llama AFN, pero ningún estado tiene dos transiciones con el mismo símbolo: son AFD parciales."),
        fila("162–188 (Lista 2)", "AFND", list(AFN_DE_LISTA2.values()), "Los siete AFN nuevos (99, 102, 103, 106, 118, 120, 123); en los demás se reutiliza el AFD, véase la Lista 2."),
        fila("189", "AFND", ["Ej_189_afn_00101_o_00110"], "Dos patrones que comparten el prefijo `001`; se adivina dónde empieza."),
        fila("190", "AFND", ["Ej_190_afn_11010_y_10100"], "Se adivina cuál patrón aparece primero; los patrones se traslapan en `1010` y en `10`."),
        fila("192–195", "AFND", [f"Ej_{n}_tabla" for n in range(192, 196)], "AFN dado por tabla: hay celdas con varios destinos."),
        fila("196–200", "AFND-λ", [f"Ej_{n}_tabla" for n in range(196, 201)], "Tabla con columna λ. Opcionales en la lista, pero necesarios para el apartado 2.3."),
        fila("254–258", "AFD", [f"Ej_{n}_tabla" for n in range(254, 259)], "AFD dado por tabla; se pide su expresión regular."),
        fila("260", "AFND", ["Ej_260_tabla"], "AFN dado por tabla."),
        fila("261", "AFND", ["Ej_261_figura"], "AFN dado por figura: `q0` va a `q0` y a `q1` con 0."),
        fila("262", "AFD", ["Ej_262_ab_ba"], "El enunciado pide un AFN para {ab, ba}; el diseño resulta determinista (AFD parcial), y la conversión solo agrega el estado ∅."),
        fila("263", "AFND", ["Ej_263_figura"], "AFN dado por figura: `q0` va a `q0` y a `q1` con 0."),
    ]
    return tabla(["Ej.", "Sección", "Archivo(s)", "Justificación"], filas)


def tabla_conversiones():
    filas = []
    for nombre in E.CONVERSIONES_AFN + E.CONVERSIONES_LAMBDA:
        num = nombre.split("_")[1]
        lam = nombre in E.CONVERSIONES_LAMBDA
        origen = E.POR_NOMBRE[nombre].fabrica()
        afn = E.POR_NOMBRE[f"Ej_{num}_afnd"].fabrica() if lam else origen
        afd = E.POR_NOMBRE[f"Ej_{num}_afd"].fabrica()
        etiqueta = f"{num} (λ → AFND → AFD)" if lam else num
        filas.append([etiqueta, cuenta(origen) if lam else cuenta(afn), cuenta(afd), len(afd.minimizar().estados),
                      f"{2 ** len(afn.estados):,}", f"{len(afd.estados) / len(afn.estados):.1f}×"])
    return tabla(["Ejercicio", "AFN (o AFND-λ): estados / transiciones", "AFD: estados / transiciones", "AFD mínimo", "Cota 2ⁿ", "AFD / AFN"], filas)


def tabla_lambda():
    filas, clausuras = [], []
    for n in range(196, 201):
        a = E.POR_NOMBRE[f"Ej_{n}_tabla"].fabrica()
        lambdas = [f"{d} –λ→ {h}" for d, l, h in a.transiciones() if l == ""]
        filas.append([n, len(a.estados), len(lambdas), ", ".join(lambdas)])
        for q, cl in a.clausuras().items():
            clausuras.append([n, q, formatear_conjunto(cl)])
    return tabla(["Ej.", "Estados", "Transiciones λ", "Cuáles"], filas), tabla(["Ej.", "Estado", "Cl(estado)"], clausuras)


def tabla_correcciones():
    filas = [["99", "Tenía una transición no determinista (`q5` con `1` iba a `q0` y a `q6`): no era un AFD y rechazaba `00101001001`."],
             ["103", "No cubría el traslape del patrón: rechazaba `aabaabbba`."],
             ["107", "Transición no determinista en `q3` con `1`: rechazaba `020101021`."],
             ["109", "Fallaba desde longitud 9: rechazaba `abbcbaabb` y `abbcbcbaabb`."],
             ["118", "Aceptaba cadenas que no son del lenguaje, como `aab`."],
             ["121", "Tenía como final el estado trampa `q5` en lugar de `q0`."],
             ["133", "Faltaba la transición δ(q2, b) = q3 que da el enunciado."]]
    return tabla(["Ej. (Lista 2)", "Qué fallaba en el `.jff` de la Práctica 1"], filas)


def datos_de_comparacion():
    """Cifras que se citan en el texto de 2.4, calculadas de los autómatas."""
    import statistics
    import controlador as K
    razones, iguales = [], []
    for nombre in E.CONVERSIONES_AFN + E.CONVERSIONES_LAMBDA:
        num = nombre.split("_")[1]
        lam = nombre in E.CONVERSIONES_LAMBDA
        afn = E.POR_NOMBRE[f"Ej_{num}_afnd"].fabrica() if lam else E.POR_NOMBRE[nombre].fabrica()
        afd = E.POR_NOMBRE[f"Ej_{num}_afd"].fabrica()
        razones.append((len(afd.estados) / len(afn.estados), num, len(afn.estados), len(afd.estados)))
        if len(afd.estados) == len(afn.estados):
            iguales.append(num)
    activos_prom, evaluadas_prom = [], []
    for nombre in E.CONVERSIONES_AFN:
        afn = E.POR_NOMBRE[nombre].fabrica()
        afn.nombre = nombre
        buenas, malas = K.casos_de_prueba(afn)
        activos, evaluadas = [], []
        for w in buenas + malas:
            r = afn.simular(w)
            for anterior, paso in zip(r.pasos, r.pasos[1:]):
                activos.append(len(anterior.conjunto))
                evaluadas.append(sum(len(afn.destinos(q, paso.simbolo)) for q in anterior.conjunto))
        activos_prom.append(statistics.mean(activos))
        evaluadas_prom.append(statistics.mean(evaluadas))
    mayor = max(razones)
    return {"total": len(razones), "razon_max": mayor[0], "caso_max": mayor[1:], "iguales": iguales,
            "activos": (min(activos_prom), max(activos_prom)), "evaluadas": (min(evaluadas_prom), max(evaluadas_prom))}


def decimal(x):
    return f"{x:.1f}".replace(".", ",")


def conteo_por_carpeta():
    cuenta_ = {}
    for e in E.ENTREGAS:
        cuenta_[e.carpeta] = cuenta_.get(e.carpeta, 0) + 1
    filas = [["lista2-afd", len(list((RAIZ / "automatas" / "lista2-afd").glob("*.jff"))), "AFD de los ejercicios con asterisco de la Lista 2"],
             ["lista3-afd", cuenta_["lista3-afd"], "AFD de la Lista 3: simplificaciones, AFN deterministas (158–161, 262) y autómatas de 254–258"],
             ["lista3-afnd", cuenta_["lista3-afnd"], "AFN: 7 de la Lista 2, 189, 190, 192–195, 260, 261 y 263"],
             ["lista3-afnd-lambda", cuenta_["lista3-afnd-lambda"], "AFND-λ de 196–200"],
             ["conversiones", cuenta_["conversiones"], "AFD resultantes de cada conversión (y los AFND sin λ intermedios)"]]
    return tabla(["Carpeta de `automatas/`", "Autómatas", "Contenido"], filas)


def construir():
    lam, clausuras = tabla_lambda()
    cmp = datos_de_comparacion()
    return f"""# Ejercicio 2. AFND y AFND-λ en JFLAP


## 2.0. Alcance y organización de los archivos

Se implementan los ejercicios con asterisco de la Lista 2 (94 a 150) y de la Lista 3 (151 a 263), más los ejercicios 196 a 200 de la Lista 3, que no llevan asterisco pero hacen falta para el apartado 2.3. Cada autómata se entrega en `.jff` (formato principal), `.json` y `.xml`; la convención para λ (cadena vacía como símbolo leído) está en el [README](../README.md).

{chr(10).join(conteo_por_carpeta())}

Para cada autómata, sus cadenas de prueba, sus recorridos y su tabla de transiciones están en [guia-jflap/](guia-jflap/README.md). La Lista 3 resuelta, con las figuras de ejecución, está en el documento de LaTeX que se entrega aparte.

## 2.1. Clasificación y cobertura

### Criterio

Todo lenguaje regular tiene un AFD, un AFND y un AFND-λ; por eso la clasificación no dice qué se *puede* construir, sino cuál es el **diseño natural**. Se aplicó el criterio del enunciado de los ejercicios 162 a 188 («busque que el diagrama del AFN sea más simple que el del AFD»):

| Sección | Cuándo se coloca ahí un ejercicio |
|---|---|
| **AFD** | El estado es un resumen determinista de lo leído (contadores, paridades, posición, un patrón que avanza, conjunción de dos condiciones), o el autómata ya viene dado como AFD. El AFN no mejora al AFD. |
| **AFND** | El lenguaje se define con un «existe» (existe una posición o una descomposición) y el AFN que *adivina* esa elección tiene menos estados o menos transiciones que el AFD, o el autómata viene dado con celdas de varios destinos. |
| **AFND-λ** | El autómata tiene transiciones λ. |

Cada resultado se midió: se diseñó el AFN candidato, se verificó contra la definición del lenguaje (todas las cadenas hasta una longitud dada, más cadenas largas al azar, y una comparación exacta con el AFD) y se contaron estados y transiciones.

### Lista 2 (ejercicios con asterisco)

En la Lista 2 todos los problemas piden un AFD, así que el AFD se entrega siempre en `lista2-afd/`. En los siete donde el AFN es más simple, el AFN se entrega además en `lista3-afnd/` (lo pide la Lista 3, ejercicios 162 a 188) y el AFD queda como su AFD equivalente.

{chr(10).join(tabla_clasificacion_lista2())}

### Lista 3 (ejercicios con asterisco, más 196 a 200)

{chr(10).join(tabla_clasificacion_lista3())}


## 2.2. Diseño y validación

### Cómo se diseñó y se probó cada autómata

Para cada autómata se documenta: la idea de diseño, la tabla de transiciones, **cinco cadenas válidas y cinco inválidas** de distinta longitud con el resultado esperado, y el recorrido completo (los estados activos tras cada símbolo y, en los no deterministas, el número de caminos de cómputo y cuántos aceptan). Todo eso está en [guia-jflap/](guia-jflap/README.md). Donde el lenguaje tiene pocas cadenas válidas (el 158 solo acepta `01`; el 262 solo `ab` y `ba`) se dan las que existen.

La validación no depende de unos cuantos ejemplos:

- Cada autómata construido a partir de un enunciado en palabras se compara con un predicado independiente para **todas las cadenas hasta una longitud dada** (de 7 a 15 símbolos según el alfabeto) y con miles de cadenas largas al azar (`tests/test_lista2.py`, `tests/test_lista3.py`).
- Los AFN de la Lista 3 se comparan con el AFD de la Lista 2 con una comparación **exacta** (`cadena_distintiva`, que recorre a la vez los conjuntos de estados de los dos autómatas).
- Cada conversión se comprueba contra su AFN de origen.
- `python herramientas/verificar_entregas.py` revisa cualquier `.jff` dibujado a mano contra su definición y da la cadena más corta que los distingue.

### Corrección de siete autómatas de la Práctica 1

Al cargar con el lector nuevo los `.jff` de la Práctica 1 y probarlos con una longitud mayor a la de entonces (8 símbolos), siete no reconocían el lenguaje del enunciado. Se regeneraron; los otros 14 se conservan tal cual. En el 128, además, la transcripción del diagrama estaba mal (el diagrama tiene δ(D, 1) = E y δ(F, 0) = δ(F, 1) = D).

{chr(10).join(tabla_correcciones())}

### Simulación paso a paso en JFLAP


## 2.3. Transiciones λ

Los cinco AFND-λ del enunciado (196 a 200) tienen las transiciones λ que se muestran; su ubicación viene dada en cada tabla.

{chr(10).join(lam)}

La λ-clausura de un estado `q`, Cl(q), es el conjunto de estados alcanzables desde `q` usando solo transiciones λ, incluido `q`. Para un conjunto, es la unión de las clausuras de sus estados.

{chr(10).join(clausuras)}

**Su papel en el reconocimiento.** El autómata no consume ningún símbolo al seguir una transición λ, así que, al empezar y después de leer cada símbolo, hay que añadir al conjunto de estados activos todo lo que se alcanza por λ. Formalmente, δ̂(Z, ε) = Cl(Z) y δ̂(Z, wa) = Cl(⋃ δ(q, a) para q en δ̂(Z, w)). Una cadena se acepta si δ̂({{q₀}}, w) contiene un estado de aceptación. Por eso la cadena vacía se acepta si y solo si Cl({{q₀}}) contiene uno, y por eso quitar las transiciones λ (δ'(q, a) = Cl(δ(Cl({{q}}), a)), con q de aceptación si Cl({{q}}) contiene un estado de aceptación) no cambia el lenguaje.


## 2.4. Conversiones y análisis comparativo

### Procedimiento

En JFLAP, un AFND estándar se convierte con *Convert → Convert to DFA* (se puede ver paso a paso con *Complete*). Un AFND-λ se convierte **primero a un AFND estándar** (se quitan las transiciones λ) **y después a un AFD**. Los AFD resultantes están en `automatas/conversiones/`; JFLAP nombra los estados del AFD con los conjuntos y no agrega el estado ∅, por lo que su resultado puede quedar incompleto. La construcción de subconjuntos, paso a paso, de cada ejercicio está en [guia-jflap/03-afn-a-afd.md](guia-jflap/03-afn-a-afd.md) y [04-afnd-lambda.md](guia-jflap/04-afnd-lambda.md).


### Tabla de conversiones

{chr(10).join(tabla_conversiones())}

El AFD es el que produce la construcción de subconjuntos (solo los conjuntos alcanzables), no el mínimo; la columna «AFD mínimo» muestra cuánto se podría reducir. La conversión del 262 agrega el estado ∅, porque el AFN ya era determinista.

### Comparación

**Número de estados.** En las {cmp["total"]} conversiones el AFD tiene como máximo {decimal(cmp["razon_max"])} veces los estados del AFN (el {cmp["caso_max"][0]}, de {cmp["caso_max"][1]} a {cmp["caso_max"][2]}), y en ninguna se acerca a la cota 2ⁿ: el caso más grande, el 190, pasa de 21 a 48 estados, contra 2 097 152. En los ejercicios {", ".join(cmp["iguales"])} el AFD tiene tantos estados como el AFN (o AFND).

**Complejidad de las transiciones.** Un AFD completo tiene |Σ| transiciones por estado; un AFN solo dibuja las que existen. Por eso los AFN de patrones tienen menos transiciones aunque no tengan menos estados (el 99: 9 contra 21).

**Facilidad de diseño e interpretación.**


**Eficiencia en el reconocimiento.** Simular un AFN siguiendo todos los caminos cuesta O(|w|·|δ|) en tiempo y O(|Q|) en espacio; con el AFD ya construido, O(|w|) con un solo estado activo. En las cadenas de prueba de los AFN de la Lista 3 hay entre {decimal(cmp["activos"][0])} y {decimal(cmp["activos"][1])} estados activos en promedio y entre {decimal(cmp["evaluadas"][0])} y {decimal(cmp["evaluadas"][1])} transiciones evaluadas por símbolo (frente a una en el AFD); el detalle está en [03-simulador.md](03-simulador.md#medición-del-costo).

### Por qué la cota 2ⁿ rara vez se alcanza

Cada estado del AFD es un subconjunto de estados del AFN que se alcanza desde el inicial por alguna cadena; solo se crean esos. La estructura de un AFN suele limitar qué subconjuntos pueden coincidir. En los AFN de patrones (99, 102, 103 y 106), los estados activos quedan determinados por el prefijo más largo del patrón que coincide con el final de lo leído (los demás prefijos que coinciden son sus bordes), así que el número de subconjuntos crece con la longitud del patrón y no como 2ⁿ: en el 102, 7 estados dan 12 subconjuntos, no 128. Además, estados distintos del AFD pueden ser equivalentes (por eso el AFD mínimo es todavía menor).

### Una familia en la que sí se alcanza

Hopcroft, Motwani y Ullman presentan el lenguaje de las cadenas sobre {{0, 1}} cuyo n-ésimo símbolo desde el final es 1: tiene un AFN de n + 1 estados y todo AFD que lo reconozca necesita al menos 2ⁿ estados (Hopcroft et al., 2007, sección 2.3.6; verifica el número de sección y de página en tu ejemplar). Se comprobó con el simulador: el AFN construido para n = 1 a 6 da, por subconjuntos, un AFD cuyo mínimo tiene exactamente 2ⁿ estados (`tests/test_automata.py`, `test_la_cota_2_a_la_n_se_alcanza_en_el_n_esimo_simbolo_desde_el_final`), y para n = 4, 8 y 12 el AFD mide 16, 256 y 4 096 estados (véase [03-simulador.md](03-simulador.md#medición-del-costo)).


## Referencias

Hopcroft, J. E., Motwani, R. y Ullman, J. D. (2007). *Introducción a la teoría de autómatas, lenguajes y computación* (3.ª ed.). Pearson Addison-Wesley. ISBN: 978-84-7829-088-8.

Rodger, S. H. y Finley, T. W. (2006). *JFLAP: An interactive formal languages and automata package*. Jones & Bartlett.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--forzar", action="store_true", help="reescribe docs/02-jflap.md aunque ya exista")
    args = parser.parse_args()
    if DESTINO.exists() and not args.forzar:
        sys.exit(f"{DESTINO.relative_to(RAIZ)} ya existe; usa --forzar para reescribirlo (se pierde lo editado a mano).")
    DESTINO.parent.mkdir(exist_ok=True)
    texto = construir()
    DESTINO.write_text(texto, encoding="utf-8", newline="\n")
    print(f"{DESTINO.relative_to(RAIZ)}: {len(texto.splitlines())} líneas")


if __name__ == "__main__":
    main()
