"""Dibujo de un autómata como imagen SVG.

No depende de Flet: devuelve texto SVG, que la interfaz muestra y que también se puede
guardar como archivo. Los estados se colocan con las coordenadas del autómata o, si no las
tiene, con la distribución por capas de formatos.posiciones_de_dibujo.

Convención del diagrama (la de JFLAP y la del curso): una flecha sin origen marca el estado
inicial, un doble círculo marca un estado de aceptación y la transición λ se escribe λ.
"""

import math
import re
from xml.sax.saxutils import escape

from formatos import posiciones_de_dibujo
from lenguajes import LAMBDA

TRAZO = "#37474f"
RELLENO = "#ffffff"
ACTIVO_RELLENO = "#ffe082"
ACTIVO_TRAZO = "#e65100"
RESALTADO = "#d84315"
TEXTO = "#212121"
ETIQUETA = "#0d47a1"


def radio_de(nombre):
    """Radio del círculo de un estado: crece con la longitud del nombre."""
    return min(64.0, max(26.0, 4.4 * len(nombre) + 14.0))


def _tamano_de_letra(nombre):
    return 14 if len(nombre) <= 8 else max(9.0, 14 - 0.6 * (len(nombre) - 8))


def _unitario(dx, dy):
    largo = math.hypot(dx, dy) or 1.0
    return dx / largo, dy / largo


def _numero(x):
    return f"{x:.1f}"


def _agrupar_aristas(automata):
    """(desde, hacia) -> lista de etiquetas (símbolos leídos, con λ para la cadena vacía)."""
    aristas = {}
    for desde, lee, hacia in automata.transiciones():
        aristas.setdefault((desde, hacia), []).append(lee if lee else LAMBDA)
    return aristas


def _etiqueta(x, y, texto, resaltada):
    """Texto con un contorno blanco debajo (dos textos: el contorno y el relleno)."""
    color = RESALTADO if resaltada else ETIQUETA
    peso = "bold" if resaltada else "normal"
    base = (f'x="{_numero(x)}" y="{_numero(y)}" text-anchor="middle" font-size="14" font-weight="{peso}" '
            'font-family="Segoe UI, Arial, sans-serif"')
    return (f'<text {base} fill="{RELLENO}" stroke="{RELLENO}" stroke-width="5">{escape(texto)}</text>'
            f'<text {base} fill="{color}">{escape(texto)}</text>')


def _punta(x, y, tx, ty, color):
    """Triángulo de la punta de una flecha en (x, y), con (tx, ty) la dirección de avance.
    Se dibuja a mano porque algunos visores de SVG (el de Flet) no soportan marker."""
    nx, ny = -ty, tx
    largo, ancho = 11.0, 5.0
    bx, by = x - tx * largo, y - ty * largo
    puntos = f"{_numero(x)},{_numero(y)} {_numero(bx + nx * ancho)},{_numero(by + ny * ancho)} "              f"{_numero(bx - nx * ancho)},{_numero(by - ny * ancho)}"
    return f'<polygon points="{puntos}" fill="{color}"/>'


def _curvatura(p1, p2, hay_inversa):
    """Cuánto se aparta del segmento la flecha entre dos estados: 0 si va recta. Se curvan las
    que tienen otra flecha de vuelta y las largas, para que no crucen los estados intermedios."""
    distancia = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    if distancia > 240:
        return min(120.0, 0.3 * distancia)
    return 34.0 if hay_inversa else 0.0


def _arista_entre(p1, r1, p2, r2, etiqueta, hay_inversa, resaltada):
    """Flecha entre dos estados distintos; se curva si también hay una flecha de vuelta."""
    (x1, y1), (x2, y2) = p1, p2
    ux, uy = _unitario(x2 - x1, y2 - y1)
    nx, ny = -uy, ux                                   # perpendicular a la izquierda del sentido de la flecha
    curva = _curvatura(p1, p2, hay_inversa)
    cx, cy = (x1 + x2) / 2 + nx * curva, (y1 + y2) / 2 + ny * curva
    sx, sy = _unitario(cx - x1, cy - y1)
    ex, ey = _unitario(cx - x2, cy - y2)
    ax, ay = x1 + sx * r1, y1 + sy * r1
    bx, by = x2 + ex * (r2 + 2), y2 + ey * (r2 + 2)    # punta de la flecha, 2 px antes del círculo
    tx, ty = _unitario(bx - cx, by - cy)               # dirección con la que llega
    color = RESALTADO if resaltada else TRAZO
    ancho = 3 if resaltada else 1.6
    fx, fy = bx - tx * 9.0, by - ty * 9.0              # el trazo termina en la base de la punta
    if curva:
        d = f"M {_numero(ax)} {_numero(ay)} Q {_numero(cx)} {_numero(cy)} {_numero(fx)} {_numero(fy)}"
    else:
        d = f"M {_numero(ax)} {_numero(ay)} L {_numero(fx)} {_numero(fy)}"
    mx = 0.25 * ax + 0.5 * cx + 0.25 * bx             # punto medio de la curva
    my = 0.25 * ay + 0.5 * cy + 0.25 * by
    dx, dy = _unitario(bx - ax, by - ay)
    lx, ly = mx - dy * 14.0, my + dx * 14.0            # la etiqueta, a la izquierda de la flecha
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ancho}"/>'
            + _punta(bx, by, tx, ty, color) + _etiqueta(lx, ly + 5, etiqueta, resaltada))


def _bucle(p, r, etiqueta, resaltada):
    """Flecha de un estado hacia sí mismo, por encima del círculo."""
    x, y = p
    sx, sy, ex, ey = x - r * 0.5, y - r * 0.866, x + r * 0.5, y - r * 0.866
    c1x, c1y, c2x, c2y = x - r * 1.15, y - r * 2.7, x + r * 1.15, y - r * 2.7
    tx, ty = _unitario(ex - c2x, ey - c2y)
    fx, fy = ex - tx * 9.0, ey - ty * 9.0
    d = (f"M {_numero(sx)} {_numero(sy)} C {_numero(c1x)} {_numero(c1y)} {_numero(c2x)} {_numero(c2y)} "
         f"{_numero(fx)} {_numero(fy)}")
    color = RESALTADO if resaltada else TRAZO
    ancho = 3 if resaltada else 1.6
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ancho}"/>'
            + _punta(ex, ey, tx, ty, color) + _etiqueta(x, y - r * 2.1 - 6, etiqueta, resaltada))


def _estado(automata, q, p, r, activo):
    x, y = p
    relleno = ACTIVO_RELLENO if activo else RELLENO
    trazo = ACTIVO_TRAZO if activo else TRAZO
    ancho = 3.2 if activo else 1.8
    partes = [f'<circle cx="{_numero(x)}" cy="{_numero(y)}" r="{_numero(r)}" fill="{relleno}" '
              f'stroke="{trazo}" stroke-width="{ancho}"/>']
    if automata.es_aceptacion(q):
        partes.append(f'<circle cx="{_numero(x)}" cy="{_numero(y)}" r="{_numero(r - 5)}" fill="none" '
                      f'stroke="{trazo}" stroke-width="{ancho}"/>')
    partes.append(f'<text x="{_numero(x)}" y="{_numero(y + 5)}" text-anchor="middle" '
                  f'font-size="{_numero(_tamano_de_letra(q))}" fill="{TEXTO}" '
                  f'font-family="Segoe UI, Arial, sans-serif">{escape(q)}</text>')
    if q == automata.inicial:
        partes.append(f'<path d="M {_numero(x - r - 48)} {_numero(y)} L {_numero(x - r - 11)} {_numero(y)}" '
                      f'fill="none" stroke="{TRAZO}" stroke-width="1.8"/>' + _punta(x - r - 2, y, 1.0, 0.0, TRAZO))
    return "".join(partes)


def svg_automata(automata, activos=(), resaltadas=(), titulo=None):
    """Imagen SVG del autómata.

    activos: estados que se pintan como activos (los del paso actual de la simulación).
    resaltadas: transiciones (desde, lee, hacia) que se dibujan en destacado (las del paso actual).
    """
    activos = set(activos)
    resaltadas = {(d, h) for d, _, h in resaltadas}
    titulo = automata.nombre if titulo is None else titulo
    if not automata.estados:
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="360" height="120" viewBox="0 0 360 120">'
                f'<rect width="360" height="120" fill="{RELLENO}"/>'
                f'<text x="180" y="65" text-anchor="middle" font-size="15" fill="{ETIQUETA}" '
                'font-family="Segoe UI, Arial, sans-serif">Aún no hay estados</text></svg>')
    pos = posiciones_de_dibujo(automata)
    radios = {q: radio_de(q) for q in automata.estados}
    aristas = _agrupar_aristas(automata)
    curvas = [_curvatura(pos[d], pos[h], (h, d) in aristas) for (d, h) in aristas if d != h]
    holgura = max(curvas, default=0.0) / 2 + 30
    izquierda = min(pos[q][0] - radios[q] for q in automata.estados) - 70
    derecha = max(pos[q][0] + radios[q] for q in automata.estados) + 40
    arriba = min(pos[q][1] - radios[q] * 2.9 for q in automata.estados) - 10 - holgura
    abajo = max(pos[q][1] + radios[q] for q in automata.estados) + 60 + holgura
    ancho, alto = derecha - izquierda, abajo - arriba
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_numero(ancho)}" height="{_numero(alto)}" '
        f'viewBox="{_numero(izquierda)} {_numero(arriba)} {_numero(ancho)} {_numero(alto)}">',
        f"<title>{escape(titulo or 'Autómata')}</title>",
        f'<rect x="{_numero(izquierda)}" y="{_numero(arriba)}" width="{_numero(ancho)}" height="{_numero(alto)}" '
        f'fill="{RELLENO}"/>',
    ]
    for (desde, hacia), simbolos in aristas.items():
        texto = ",".join(simbolos)
        resaltada = (desde, hacia) in resaltadas
        if desde == hacia:
            partes.append(_bucle(pos[desde], radios[desde], texto, resaltada))
        else:
            partes.append(_arista_entre(pos[desde], radios[desde], pos[hacia], radios[hacia], texto,
                                        (hacia, desde) in aristas, resaltada))
    for q in automata.estados:
        partes.append(_estado(automata, q, pos[q], radios[q], q in activos))
    partes.append("</svg>")
    return "\n".join(partes)


def dimensiones_svg(svg):
    """(ancho, alto) en píxeles de un SVG generado por svg_automata."""
    m = re.search(r'<svg[^>]*\swidth="([\d.]+)"[^>]*\sheight="([\d.]+)"', svg)
    return (float(m.group(1)), float(m.group(2))) if m else (360.0, 120.0)
