"""Mide el costo de las dos formas de reconocer con un autómata no determinista.

Uso, desde la raíz del repositorio:

    python herramientas/medir_costos.py

Imprime dos tablas en Markdown:

1. La familia «el n-ésimo símbolo desde el final es 1» (AFN de n+1 estados, AFD mínimo de 2^n): tamaño del AFD, tiempo para
   construirlo y tiempo para reconocer cadenas largas siguiendo todos los caminos (AFN) y con el AFD ya construido.
2. Para los AFN de las conversiones de la Lista 3: cuántos estados están activos en promedio y cuántas transiciones se evalúan
   por símbolo al recorrer sus cadenas de prueba, frente a una sola transición en el AFD.

Los tiempos dependen de la computadora; lo que se compara es su proporción, no los valores absolutos.
"""

import random
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import controlador as K          # noqa: E402
import ejercicios as E           # noqa: E402
from automata import Automata    # noqa: E402


def n_desde_el_final(n):
    a = Automata("01", [f"q{i}" for i in range(n + 1)], "q0", [f"q{n}"])
    a.agregar_transicion("q0", "0", "q0")
    a.agregar_transicion("q0", "1", "q0")
    a.agregar_transicion("q0", "1", "q1")
    for i in range(1, n):
        a.agregar_transicion(f"q{i}", "0", f"q{i + 1}")
        a.agregar_transicion(f"q{i}", "1", f"q{i + 1}")
    return a


def mejor_tiempo(funcion, repeticiones=3):
    mejores = []
    for _ in range(repeticiones):
        t = time.perf_counter()
        funcion()
        mejores.append(time.perf_counter() - t)
    return min(mejores)


def tabla_familia(ns=(4, 8, 12), cadenas=100, longitud=1000):
    azar = random.Random(1)
    filas = []
    for n in ns:
        afn = n_desde_el_final(n)
        palabras = ["".join(azar.choice("01") for _ in range(longitud)) for _ in range(cadenas)]
        t_conversion = mejor_tiempo(lambda: afn.a_afd(), 1)
        afd = afn.a_afd().afd
        t_afn = mejor_tiempo(lambda: [afn.acepta(w) for w in palabras])
        t_afd = mejor_tiempo(lambda: [afd.acepta(w) for w in palabras])
        assert [afn.acepta(w) for w in palabras] == [afd.acepta(w) for w in palabras]
        filas.append((n, len(afn.estados), len(afd.estados), 2 ** n, t_conversion, t_afn, t_afd))
    lineas = [f"| n | Estados AFN | Estados AFD | 2^n | Construir el AFD (s) | {cadenas} cadenas de {longitud} símbolos con el AFN (s) | las mismas con el AFD (s) |",
              "|---|---|---|---|---|---|---|"]
    lineas += [f"| {n} | {a} | {d} | {c:,} | {tc:.3f} | {ta:.3f} | {td:.3f} |" for n, a, d, c, tc, ta, td in filas]
    return lineas


def tabla_actividad():
    lineas = ["| Ejercicio | Estados AFN | Estados activos (promedio) | Transiciones evaluadas por símbolo (promedio) | Estados AFD |",
              "|---|---|---|---|---|"]
    for nombre in E.CONVERSIONES_AFN:
        num = nombre.split("_")[1]
        afn = E.POR_NOMBRE[nombre].fabrica()
        afn.nombre = nombre
        afd = E.POR_NOMBRE[f"Ej_{num}_afd"].fabrica()
        buenas, malas = K.casos_de_prueba(afn)
        activos, evaluadas = [], []
        for w in buenas + malas:
            r = afn.simular(w)
            for anterior, paso in zip(r.pasos, r.pasos[1:]):
                activos.append(len(anterior.conjunto))
                evaluadas.append(sum(len(afn.destinos(q, paso.simbolo)) for q in anterior.conjunto))
        lineas.append(f"| {num} | {len(afn.estados)} | {statistics.mean(activos):.2f} | {statistics.mean(evaluadas):.2f} | {len(afd.estados)} |")
    return lineas


def main():
    print("## La familia en la que se alcanza 2^n\n")
    print("\n".join(tabla_familia()))
    print("\n## Actividad del AFN en las cadenas de prueba\n")
    print("\n".join(tabla_actividad()))


if __name__ == "__main__":
    main()
