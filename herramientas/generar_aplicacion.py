"""Genera el autómata del Ejercicio 5: comportamiento de un fantasma de Pac-Man como AFD.

Uso, desde la raíz del repositorio:

    python herramientas/generar_aplicacion.py

Escribe en automatas/aplicacion/ el .jff, el .json y el .xml del autómata.

Base: Gribkoff (2013), sección 4 y Figura 3 (cuatro estados y siete flechas).
Ampliación propia (apartado «Ampliación» de docs/05-del-articulo-al-automata.md):
dos estados nuevos (Parpadear y Regenerar) y dos eventos nuevos (a y r). Ambas
ampliaciones son refinamientos: cada una parte en dos pasos una flecha de la figura.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import formatos as F                            # noqa: E402
from automata import Automata                   # noqa: E402

CARPETA = RAIZ / "automatas" / "aplicacion"
NOMBRE = "Pacman_fantasma"

# Eventos: un carácter cada uno, porque el simulador lee la cadena símbolo por símbolo.
EVENTOS = {
    "v": "el fantasma ve a Pac-Man (Spot Pac-Man)",
    "p": "el fantasma pierde a Pac-Man (Lose Pac-Man)",
    "c": "Pac-Man come una pastilla de poder (Pac-Man Eats Power Pellet)",
    "e": "se acaba el efecto de la pastilla (Power Pellet Expires)",
    "m": "Pac-Man se come al fantasma (Eaten by Pac-Man)",
    "b": "el fantasma llega a la base central (Reach Central Base)",
    "a": "NUEVO: quedan pocos segundos de pastilla (alerta de fin)",
    "r": "NUEVO: el fantasma termina de regenerarse",
}

# Estado -> (nombre en el juego, significado). q0 a q3 vienen de la Figura 3; q4 y q5 son nuevos.
ESTADOS = {
    "q0": ("Vagar", "recorre el laberinto sin objetivo (estado inicial)"),
    "q1": ("Perseguir", "Pac-Man está a la vista y el fantasma lo persigue (único estado de aceptación)"),
    "q2": ("Huir", "Pac-Man comió una pastilla: el fantasma es vulnerable y huye"),
    "q3": ("Regresar", "Pac-Man se comió al fantasma: solo los ojos vuelven a la base"),
    "q4": ("Parpadear", "NUEVO: quedan pocos segundos de pastilla; el fantasma sigue vulnerable"),
    "q5": ("Regenerar", "NUEVO: el fantasma está en la base, regenerándose, y no se puede comer"),
}
INICIAL, ACEPTACION = "q0", ["q1"]

# Solo se escriben las flechas que cambian de estado; el resto de los eventos deja el estado igual
# (el evento ocurre pero no cambia el comportamiento) y se completa abajo con lazos.
CAMBIOS = {
    "q0": {"v": "q1", "c": "q2"},              # Spot Pac-Man; Pac-Man Eats Power Pellet
    "q1": {"p": "q0", "c": "q2"},              # Lose Pac-Man; Pac-Man Eats Power Pellet
    "q2": {"m": "q3", "a": "q4"},              # Eaten by Pac-Man; NUEVO: alerta de fin de pastilla
    "q3": {"b": "q5"},                         # Reach Central Base, ahora pasa por Regenerar
    "q4": {"e": "q0", "m": "q3", "c": "q2"},   # Power Pellet Expires (ahora desde Parpadear); otra pastilla reinicia el tiempo
    "q5": {"r": "q0"},                         # NUEVO: termina la regeneración
}

POSICIONES = {"q0": (120, 100), "q1": (420, 100), "q2": (420, 280),
              "q4": (270, 280), "q3": (270, 460), "q5": (120, 460)}


def construir():
    a = Automata(list(EVENTOS), list(ESTADOS), INICIAL, ACEPTACION, nombre=NOMBRE)
    for q in ESTADOS:
        for simbolo in EVENTOS:
            a.agregar_transicion(q, simbolo, CAMBIOS[q].get(simbolo, q))
    a.posiciones = {q: (float(x), float(y)) for q, (x, y) in POSICIONES.items()}
    return a


def main():
    CARPETA.mkdir(parents=True, exist_ok=True)
    a = construir()
    for extension in (".jff", ".json", ".xml"):
        F.guardar_archivo(a, CARPETA / f"{NOMBRE}{extension}")
    print(f"{NOMBRE}: {a.tipo}, {len(a.estados)} estados, {len(a.alfabeto)} eventos, "
          f"completo={a.es_completo()} -> {CARPETA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
