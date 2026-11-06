"""Genera los autómatas de la Lista 4 que usa la Práctica 4 (Ejercicio 3: 276 y 277).

Uso, desde la raíz del repositorio:

    python herramientas/generar_practica4.py

Como en herramientas/generar_lista3.py, un .jff que ya exista no se vuelve a escribir (para no
perder uno dibujado a mano); su .json y su .xml siempre se generan a partir del .jff que haya.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import ejercicios as E   # noqa: E402
import formatos as F     # noqa: E402

AUT = RAIZ / "automatas"


def escribir_archivos(sobrescribir=False):
    nuevos = existentes = 0
    for e in E.AUTOMATAS_LISTA4:
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
    print(f"{nuevos} .jff escritos, {existentes} ya existían y se respetaron; "
          f".json y .xml de los {len(E.AUTOMATAS_LISTA4)}.")


if __name__ == "__main__":
    escribir_archivos(sobrescribir="--sobrescribir" in sys.argv)
