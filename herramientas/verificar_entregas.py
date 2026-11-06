"""Comprueba los autómatas de la Lista 3 (y las conversiones) que haya en automatas/.

Uso, desde la raíz del repositorio:

    python herramientas/verificar_entregas.py              # solo comprueba
    python herramientas/verificar_entregas.py --formatos   # además escribe el .json y el .xml de cada .jff

Para cada .jff compara el lenguaje que reconoce con el de su definición (src/ejercicios.py) y avisa de
cualquier diferencia con la cadena más corta que los distingue, de que el tipo no es el esperado (por ejemplo, un AFD
con una transición no determinista) y de nombres de archivo que no corresponden a ningún ejercicio.
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import ejercicios as E                          # noqa: E402
import formatos as F                            # noqa: E402
from automata import cadena_distintiva          # noqa: E402

CARPETAS = ["lista3-afd", "lista3-afnd", "lista3-afnd-lambda", "conversiones"]


def revisar(ruta, escribir_formatos):
    """Devuelve (estado, mensaje) para un .jff: «OK», «AVISO» o «MAL»."""
    entrega = E.POR_NOMBRE.get(ruta.stem)
    try:
        tuyo = F.leer_archivo(ruta)
    except (F.FormatoInvalido, ValueError) as error:
        return "MAL", f"no se pudo leer: {error}"
    if tuyo.validar():
        return "MAL", "definición incompleta: " + " ".join(tuyo.validar())
    if entrega is None:
        return "AVISO", "el nombre no corresponde a ningún ejercicio (revisa que sea exactamente el de la guía)"
    esperado = entrega.fabrica()
    esperado.nombre = entrega.nombre
    avisos = []
    distintiva = cadena_distintiva(tuyo, esperado)
    if distintiva is not None:
        quien = "tu autómata la acepta y el esperado no" if tuyo.acepta(distintiva) else "el esperado la acepta y el tuyo no"
        return "MAL", f"no reconoce el mismo lenguaje: con {distintiva or 'la cadena vacía'!r} {quien}"
    if (TIPOS_ORDEN.index(tuyo.tipo) > TIPOS_ORDEN.index(esperado.tipo)):
        avisos.append(f"es un {tuyo.tipo} y se esperaba un {esperado.tipo}")
    if len(tuyo.estados) != len(esperado.estados):
        avisos.append(f"tiene {len(tuyo.estados)} estados y el de referencia {len(esperado.estados)}")
    if escribir_formatos:
        for extension in (".json", ".xml"):
            F.guardar_archivo(tuyo, ruta.with_suffix(extension))
    return ("AVISO", "; ".join(avisos)) if avisos else ("OK", f"{tuyo.tipo}, {len(tuyo.estados)} estados")


TIPOS_ORDEN = ["AFD", "AFND", "AFND-lambda"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--formatos", action="store_true", help="escribe el .json y el .xml de cada .jff correcto")
    args = parser.parse_args()
    cuentas = {"OK": 0, "AVISO": 0, "MAL": 0}
    for carpeta in CARPETAS:
        rutas = sorted((RAIZ / "automatas" / carpeta).glob("*.jff"))
        if not rutas:
            continue
        print(f"\n{carpeta}/")
        for ruta in rutas:
            estado, mensaje = revisar(ruta, args.formatos and True)
            cuentas[estado] += 1
            print(f"  {estado:5} {ruta.name:50} {mensaje}")
    print(f"\n{cuentas['OK']} bien, {cuentas['AVISO']} con aviso, {cuentas['MAL']} mal.")
    return 1 if cuentas["MAL"] else 0


if __name__ == "__main__":
    sys.exit(main())
