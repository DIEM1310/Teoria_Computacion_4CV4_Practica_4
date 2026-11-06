"""Simulador de autómatas finitos con interfaz gráfica (Flet).

Solo arma la pantalla y llama a las funciones de controlador.py, automata.py, formatos.py,
dibujo.py y lenguajes.py; no calcula nada por su cuenta.
"""

import base64
from datetime import datetime

import flet as ft

import controlador as K
import dibujo as D
import formatos as F
import lenguajes as L
from automata import LIMITE_ESTADOS_AFD, comparar_por_minimo

GRIS = ft.Colors.BLUE_GREY_700
ROJO = ft.Colors.RED_700
VERDE = ft.Colors.GREEN_800
AZUL = ft.Colors.BLUE_800
LINEAS_VISIBLES = 500       # líneas que se muestran de una lista larga; el archivo guardado lleva todas

DECISION_NO_DETERMINISMO = (
    "Decisión de diseño para el no determinismo: la simulación sigue todos los caminos a la vez, con el "
    "conjunto de estados activos, sin construir el AFD. Cuesta O(|w|·|δ|) en tiempo y O(|Q|) en espacio. "
    "Convertir antes a AFD puede crear hasta 2ⁿ estados, aunque luego cada cadena se simula con un solo "
    "estado activo; esa conversión está en la pestaña Conversiones.")


def imagen_del_automata(svg, ancho=700, alto=380):
    """Recuadro con el SVG, que se puede arrastrar y ampliar. Un diagrama más ancho que el recuadro
    se reduce hasta la mitad para que se vea casi completo; con la rueda se amplía para leerlo."""
    w, h = D.dimensiones_svg(svg)
    escala = max(0.5, min(1.0, (ancho - 24) / w))
    w, h = w * escala, h * escala
    imagen = ft.Image(src="data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii"),
                      width=w, height=h)
    return ft.Container(
        width=ancho, height=alto, border=ft.Border.all(1, ft.Colors.BLUE_GREY_200),
        border_radius=ft.BorderRadius.all(8), clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.InteractiveViewer(content=imagen, constrained=False, min_scale=0.2, max_scale=5,
                                     boundary_margin=ft.Margin.all(300)))


def tarjeta(titulo, cadenas, ancho):
    """Recuadro con un título y la lista desplazable de las primeras cadenas."""
    visibles = cadenas[:LINEAS_VISIBLES]
    controles = [ft.Text(f"{titulo} ({len(cadenas):,})", weight=ft.FontWeight.BOLD)]
    if not cadenas:
        controles.append(ft.Text("Conjunto vacío (∅)", color=GRIS))
    else:
        if len(cadenas) > LINEAS_VISIBLES:
            controles.append(ft.Text(f"Se muestran las primeras {LINEAS_VISIBLES:,}; el archivo guardado las incluye todas.",
                                     size=12, color=GRIS))
        controles.append(ft.ListView(height=min(260, 24 * len(visibles)), spacing=2,
                                     controls=[ft.Text(L.formatear_cadena(c), selectable=True) for c in visibles]))
    return ft.Card(content=ft.Container(width=ancho, padding=12, content=ft.Column(spacing=8, controls=controles)))


def tabla_de_datos(columnas, filas):
    return ft.DataTable(
        columns=[ft.DataColumn(ft.Text(c, weight=ft.FontWeight.BOLD)) for c in columnas],
        rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(x), selectable=True)) for x in fila]) for fila in filas],
        column_spacing=28, data_row_min_height=34, data_row_max_height=34, heading_row_height=38)


class Aplicacion:
    def __init__(self, page: ft.Page):
        self.page = page
        self.a = K.automata_nuevo()
        self.recorrido = None           # recorrido de la cadena que se está simulando
        self.paso = 0                   # paso que se muestra
        self.resultado = None           # autómata que produjo la última conversión
        self.mostrar_lambda = False
        page.title = "Simulador de autómatas finitos"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 16
        self._armar()
        self.refrescar(editor=True)

    # ------------------------------------------------------------------ utilidades

    def avisar(self, control, texto, color=GRIS):
        control.value = texto
        control.color = color
        control.visible = bool(texto)

    def intentar(self, control, accion):
        """Ejecuta la acción; si falla por una entrada incorrecta, muestra el motivo en `control`."""
        try:
            accion()
            return True
        except (ValueError, OSError) as error:
            self.avisar(control, str(error), ROJO)
            self.page.update()
            return False

    def cambio(self, editor=False):
        """El autómata cambió: lo que dependía de él (simulación y conversión) ya no vale."""
        self.recorrido = None
        self.refrescar(editor=editor)

    # ------------------------------------------------------------------ armado

    def _armar(self):
        self.titulo = ft.Text("Simulador de autómatas finitos", size=24, weight=ft.FontWeight.BOLD)
        self.resumen = ft.Text(weight=ft.FontWeight.BOLD, color=AZUL)
        self.problemas = ft.Text(visible=False, color=ROJO)
        self._armar_definicion()
        self._armar_archivos()
        self._armar_simulacion()
        self._armar_conversiones()
        self._armar_lotes()
        self._armar_lenguajes()
        pestanas = ["Definición", "Archivos", "Simulación", "Conversiones", "Varias cadenas", "Cadenas y lenguajes"]
        vistas = [self.vista_definicion, self.vista_archivos, self.vista_simulacion, self.vista_conversiones,
                  self.vista_lotes, self.vista_lenguajes]
        self.page.add(self.titulo, self.resumen, self.problemas,
                      ft.Tabs(length=len(pestanas), expand=True, content=ft.Column(expand=True, controls=[
                          ft.TabBar(tabs=[ft.Tab(label=p) for p in pestanas]),
                          ft.TabBarView(expand=True, controls=vistas)])))

    # ------------------------------------------------------------------ refresco

    def refrescar(self, editor=False):
        a = self.a
        tipo = {"AFD": "AFD", "AFND": "AFND", "AFND-lambda": "AFND-λ"}[a.tipo]
        self.resumen.value = (f"{a.nombre or 'sin nombre'} · {tipo} · {len(a.estados)} estados · "
                              f"{len(a.transiciones())} transiciones" + (" · completo" if a.es_completo() else ""))
        problemas = a.validar()
        self.avisar(self.problemas, "Falta completar la definición: " + " ".join(problemas) if problemas else "", ROJO)
        if a.tiene_lambda:
            self.mostrar_lambda = True
        self.interruptor_lambda.value = self.mostrar_lambda
        self.campo_alfabeto.value = ", ".join(a.alfabeto)
        if editor:
            self._armar_estados()
            self._armar_celdas()
        self._dibujar_definicion()
        self._dibujar_tabla()
        self._refrescar_archivos()
        self._refrescar_simulacion()
        self.page.update()

    # ================================================================== Definición

    def _armar_definicion(self):
        self.mensaje_def = ft.Text(visible=False)
        self.campo_alfabeto = ft.TextField(label="Alfabeto Σ", hint_text="Ejemplo: a, b", width=240,
                                           on_submit=self.aplicar_alfabeto)
        self.campo_estado = ft.TextField(label="Nuevo estado", hint_text="Ejemplo: q1", width=200,
                                         on_submit=self.agregar_estado)
        self.interruptor_lambda = ft.Switch(label="Columna λ", value=False, on_change=self.cambiar_lambda)
        self.lista_estados = ft.Column(spacing=4)
        self.tabla_editable = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
        self.dibujo_def = ft.Container()
        self.tabla_completa = ft.Container()
        self.vista_definicion = ft.Column(spacing=14, scroll=ft.ScrollMode.AUTO, expand=True, controls=[
            ft.Text("Define el alfabeto, los estados, el estado inicial, los de aceptación y la función de transición. "
                    "En cada celda de la tabla escribe los estados destino separados por comas; vacío o ∅ es ninguno.",
                    color=GRIS),
            ft.Row(wrap=True, controls=[
                self.campo_alfabeto,
                ft.Button(content="Aplicar alfabeto", icon=ft.Icons.CHECK, on_click=self.aplicar_alfabeto),
                self.campo_estado,
                ft.Button(content="Agregar estado", icon=ft.Icons.ADD, on_click=self.agregar_estado),
                ft.OutlinedButton(content="Nuevo autómata", icon=ft.Icons.RESTART_ALT, on_click=self.nuevo_automata)]),
            self.mensaje_def,
            ft.Row(wrap=True, spacing=24, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                ft.Column(spacing=6, controls=[
                    ft.Text("Estados", weight=ft.FontWeight.BOLD),
                    ft.Text("Cambia el nombre y pulsa Enter; la bandera marca el estado inicial.", size=12, color=GRIS),
                    self.lista_estados]),
                ft.Column(spacing=6, controls=[
                    ft.Row(controls=[ft.Text("Función de transición δ", weight=ft.FontWeight.BOLD), self.interruptor_lambda]),
                    self.tabla_editable])]),
            ft.Text("Diagrama (arrastra para moverte, rueda o pellizco para ampliar)", weight=ft.FontWeight.BOLD),
            self.dibujo_def,
            ft.Text("Tabla de transiciones", weight=ft.FontWeight.BOLD),
            self.tabla_completa,
        ])

    def aplicar_alfabeto(self, e=None):
        def accion():
            agregados, quitados, perdidas = K.aplicar_alfabeto(self.a, self.campo_alfabeto.value or "")
            texto = "Alfabeto actualizado."
            if quitados:
                texto += f" Se quitaron {', '.join(quitados)} y {perdidas} transiciones que los leían."
            self.avisar(self.mensaje_def, texto, VERDE)
            self.cambio(editor=True)
        self.intentar(self.mensaje_def, accion)

    def agregar_estado(self, e=None):
        def accion():
            nombre = (self.campo_estado.value or "").strip() or K.nombre_de_estado_libre(self.a)
            self.a.agregar_estado(nombre, inicial=self.a.inicial is None)
            self.campo_estado.value = ""
            self.avisar(self.mensaje_def, f"Estado {nombre} agregado.", VERDE)
            self.cambio(editor=True)
        self.intentar(self.mensaje_def, accion)

    def nuevo_automata(self, e=None):
        self.a = K.automata_nuevo()
        self.mostrar_lambda = False
        self.resultado = None
        self.avisar(self.mensaje_def, "Autómata nuevo: Σ = {a, b} y un estado inicial q0.", VERDE)
        self.cambio(editor=True)
        self._mostrar_resultado_vacio()

    def cambiar_lambda(self, e):
        self.mostrar_lambda = bool(e.control.value)
        self._armar_celdas()
        self.page.update()

    def _armar_estados(self):
        filas = []
        for q in self.a.estados:
            campo = ft.TextField(value=q, width=140, dense=True, text_size=14, tooltip="Nombre del estado")
            campo.on_submit = lambda e, q=q, campo=campo: self.renombrar(q, campo)
            filas.append(ft.Row(spacing=2, controls=[
                campo,
                ft.IconButton(icon=ft.Icons.FLAG, tooltip="Estado inicial",
                              icon_color=VERDE if q == self.a.inicial else ft.Colors.BLUE_GREY_200,
                              on_click=lambda e, q=q: self.marcar_inicial(q)),
                ft.Checkbox(label="Acepta", value=self.a.es_aceptacion(q),
                            on_change=lambda e, q=q: self.marcar_aceptacion(q, e.control.value)),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip="Quitar estado", icon_color=ROJO,
                              on_click=lambda e, q=q: self.quitar_estado(q))]))
        self.lista_estados.controls = filas or [ft.Text("Sin estados", color=GRIS)]

    def renombrar(self, q, campo):
        def accion():
            nuevo = (campo.value or "").strip()
            self.a.renombrar_estado(q, nuevo)
            self.avisar(self.mensaje_def, f"{q} ahora se llama {nuevo}.", VERDE)
            self.cambio(editor=True)
        if not self.intentar(self.mensaje_def, accion):
            campo.value = q
            self.page.update()

    def marcar_inicial(self, q):
        self.a.establecer_inicial(q)
        self.cambio(editor=True)

    def marcar_aceptacion(self, q, valor):
        self.a.marcar_aceptacion(q, bool(valor))
        self.cambio(editor=False)

    def quitar_estado(self, q):
        self.a.quitar_estado(q)
        self.avisar(self.mensaje_def, f"Estado {q} quitado, con sus transiciones.", VERDE)
        self.cambio(editor=True)

    def _armar_celdas(self):
        columnas = ([""] if self.mostrar_lambda else []) + list(self.a.alfabeto)
        if not self.a.estados or not columnas:
            self.tabla_editable.controls = [ft.Text("Define un alfabeto y al menos un estado.", color=GRIS)]
            return
        encabezado = ft.Row(spacing=4, controls=[ft.Container(width=110, content=ft.Text("Estado", weight=ft.FontWeight.BOLD))]
                            + [ft.Container(width=120, content=ft.Text(c or L.LAMBDA, weight=ft.FontWeight.BOLD))
                               for c in columnas])
        filas = [encabezado]
        for q in self.a.estados:
            marca = ("→" if q == self.a.inicial else "") + ("*" if self.a.es_aceptacion(q) else "")
            celdas = [ft.Container(width=110, content=ft.Text(f"{marca} {q}".strip(), selectable=True))]
            for lee in columnas:
                campo = ft.TextField(value=K.texto_de_destinos(self.a, q, lee), width=120, dense=True, text_size=13,
                                     hint_text="∅")
                campo.on_submit = campo.on_blur = (lambda e, q=q, lee=lee, campo=campo: self.aplicar_celda(q, lee, campo))
                celdas.append(campo)
            filas.append(ft.Row(spacing=4, controls=celdas))
        self.tabla_editable.controls = filas

    def aplicar_celda(self, q, lee, campo):
        if (campo.value or "").strip() == K.texto_de_destinos(self.a, q, lee):
            return

        def accion():
            K.fijar_transicion(self.a, q, lee, campo.value or "")
            campo.error_text = None
            self.avisar(self.mensaje_def, "", GRIS)
            self.cambio(editor=False)
        if not self.intentar(self.mensaje_def, accion):
            campo.error_text = "Estado inexistente"
            self.page.update()

    def _dibujar_definicion(self):
        self.dibujo_def.content = imagen_del_automata(D.svg_automata(self.a))

    def _dibujar_tabla(self):
        columnas, filas = self.a.tabla()
        if not self.a.estados:
            self.tabla_completa.content = ft.Text("Sin estados", color=GRIS)
            return
        encabezado = ["Estado"] + [c or L.LAMBDA for c in columnas]
        datos = []
        for q, fila in filas:
            marca = ("→" if q == self.a.inicial else "") + ("*" if self.a.es_aceptacion(q) else "")
            datos.append([f"{marca} {q}".strip()] + [", ".join(fila[c]) or "∅" for c in columnas])
        self.tabla_completa.content = ft.Row(scroll=ft.ScrollMode.AUTO, controls=[tabla_de_datos(encabezado, datos)])

    # ================================================================== Archivos

    def _armar_archivos(self):
        self.mensaje_arch = ft.Text(visible=False)
        self.lista_archivos = ft.Dropdown(label="Autómatas disponibles", width=520, options=[], enable_filter=True)
        self.campo_ruta = ft.TextField(label="O escribe una ruta", hint_text="automatas/lista2-afd/Ej_097_longitud_multiplo_de_3.jff",
                                       width=620, on_submit=self.cargar)
        self.campo_nombre = ft.TextField(label="Nombre del archivo", width=320, value="automata")
        self.aviso_jff = ft.Text(visible=False, size=12, color=GRIS)
        self.vista_archivos = ft.Column(spacing=14, scroll=ft.ScrollMode.AUTO, expand=True, controls=[
            ft.Text("Cargar", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Se leen archivos .jff (JFLAP), .json y .xml. La transición λ se escribe con la cadena vacía como "
                    "símbolo leído. El .jff no guarda el alfabeto: se deduce de las transiciones.", color=GRIS),
            ft.Row(wrap=True, controls=[self.lista_archivos,
                                         ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Actualizar la lista",
                                                       on_click=lambda e: self._refrescar_archivos(True)),
                                         ft.Button(content="Cargar el elegido", icon=ft.Icons.FOLDER_OPEN,
                                                   on_click=self.cargar_elegido)]),
            ft.Row(wrap=True, controls=[self.campo_ruta, ft.Button(content="Cargar la ruta", icon=ft.Icons.FILE_OPEN,
                                                                    on_click=self.cargar)]),
            ft.Divider(),
            ft.Text("Guardar", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Los archivos se guardan en la carpeta salidas/ del proyecto.", color=GRIS),
            ft.Row(wrap=True, controls=[
                self.campo_nombre,
                ft.Button(content="Guardar .jff", icon=ft.Icons.SAVE, on_click=lambda e: self.guardar(("jff",))),
                ft.Button(content="Guardar .json", icon=ft.Icons.SAVE, on_click=lambda e: self.guardar(("json",))),
                ft.Button(content="Guardar .xml", icon=ft.Icons.SAVE, on_click=lambda e: self.guardar(("xml",))),
                ft.Button(content="Guardar los tres", icon=ft.Icons.SAVE_ALT, on_click=lambda e: self.guardar(F.FORMATOS)),
                ft.OutlinedButton(content="Guardar diagrama (.svg)", icon=ft.Icons.IMAGE, on_click=self.guardar_svg)]),
            self.aviso_jff,
            self.mensaje_arch,
        ])

    def _refrescar_archivos(self, avisar=False):
        opciones = [ft.DropdownOption(key=ruta, text=ruta) for ruta, _ in K.archivos_disponibles()]
        self.lista_archivos.options = opciones
        if self.lista_archivos.value not in {o.key for o in opciones}:
            self.lista_archivos.value = None
        perdidos = F.simbolos_que_el_jff_no_conserva(self.a)
        self.avisar(self.aviso_jff, f"Aviso: el .jff no conservará {', '.join(perdidos)}, porque ninguna transición "
                                    "lo lee; el .json y el .xml sí lo conservan." if perdidos else "", GRIS)
        if avisar:
            self.page.update()

    def _poner_cargado(self, automata, origen):
        self.a = automata
        self.mostrar_lambda = automata.tiene_lambda
        self.resultado = None
        self.campo_nombre.value = automata.nombre or "automata"
        self.avisar(self.mensaje_arch, f"Cargado {origen}: {automata.tipo}, {len(automata.estados)} estados.", VERDE)
        self.avisar(self.mensaje_def, "", GRIS)
        self.cambio(editor=True)
        self._mostrar_resultado_vacio()

    def cargar_elegido(self, e=None):
        ruta = self.lista_archivos.value
        if not ruta:
            self.avisar(self.mensaje_arch, "Elige un archivo de la lista.", ROJO)
            self.page.update()
            return
        self.intentar(self.mensaje_arch, lambda: self._poner_cargado(K.cargar(ruta), ruta))

    def cargar(self, e=None):
        texto = self.campo_ruta.value or ""
        self.intentar(self.mensaje_arch, lambda: self._poner_cargado(K.cargar(texto), texto.strip()))

    def guardar(self, formatos):
        def accion():
            rutas = K.guardar_en_salidas(self.a, self.campo_nombre.value, formatos)
            self.avisar(self.mensaje_arch, "Guardado en " + ", ".join(rutas), VERDE)
            self._refrescar_archivos()
            self.page.update()
        self.intentar(self.mensaje_arch, accion)

    def guardar_svg(self, e=None):
        def accion():
            k = self.recorrido.pasos[self.paso] if self.recorrido else None
            ruta = K.guardar_diagrama(self.a, self.campo_nombre.value, k.conjunto if k else (), k.tomadas if k else ())
            self.avisar(self.mensaje_arch, f"Diagrama guardado en {ruta}", VERDE)
            self.page.update()
        self.intentar(self.mensaje_arch, accion)

    # ================================================================== Simulación

    def _armar_simulacion(self):
        self.campo_cadena = ft.TextField(label="Cadena", hint_text="Ejemplo: 0101 (vacío o λ = cadena vacía)", width=360,
                                         on_submit=self.validar)
        self.mensaje_sim = ft.Text(visible=False)
        self.etiqueta_paso = ft.Text(weight=ft.FontWeight.BOLD)
        self.boton_inicio = ft.IconButton(icon=ft.Icons.FIRST_PAGE, tooltip="Al inicio", on_click=lambda e: self.ir_a(0))
        self.boton_anterior = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, tooltip="Paso anterior",
                                            on_click=lambda e: self.ir_a(self.paso - 1))
        self.boton_siguiente = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, tooltip="Paso siguiente",
                                             on_click=lambda e: self.ir_a(self.paso + 1))
        self.boton_final = ft.IconButton(icon=ft.Icons.LAST_PAGE, tooltip="Al final",
                                         on_click=lambda e: self.ir_a(len(self.recorrido.pasos) - 1))
        self.banner = ft.Container(visible=False, padding=12, border_radius=ft.BorderRadius.all(8))
        self.texto_banner = ft.Text(weight=ft.FontWeight.BOLD)
        self.banner.content = self.texto_banner
        self.descripcion = ft.Text(selectable=True)
        self.dibujo_sim = ft.Container()
        self.traza = ft.Column(spacing=2)
        self.caminos = ft.Column(spacing=2)
        self.boton_caminos = ft.OutlinedButton(content="Ver los caminos de cómputo", icon=ft.Icons.ACCOUNT_TREE,
                                               on_click=self.ver_caminos)
        self.vista_simulacion = ft.Column(spacing=14, scroll=ft.ScrollMode.AUTO, expand=True, controls=[
            ft.Text("Escribe una cadena para ver si el autómata la acepta, o recórrela paso a paso.", color=GRIS),
            ft.Row(wrap=True, controls=[
                self.campo_cadena,
                ft.Button(content="Validar", icon=ft.Icons.PLAY_ARROW, on_click=self.validar),
                ft.OutlinedButton(content="Paso a paso", icon=ft.Icons.SKIP_NEXT, on_click=self.empezar_paso_a_paso)]),
            self.mensaje_sim,
            ft.Row(wrap=True, controls=[self.boton_inicio, self.boton_anterior,
                                         ft.Container(width=240, alignment=ft.Alignment.CENTER, content=self.etiqueta_paso),
                                         self.boton_siguiente, self.boton_final]),
            self.banner, self.descripcion,
            ft.Row(wrap=True, spacing=24, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                self.dibujo_sim,
                ft.Column(spacing=6, controls=[ft.Text("Traza completa", weight=ft.FontWeight.BOLD), self.traza])]),
            ft.Divider(),
            ft.Text(DECISION_NO_DETERMINISMO, size=12, color=GRIS),
            self.boton_caminos, self.caminos,
        ])

    def _cadena(self):
        return K.texto_de_cadena(self.campo_cadena.value)

    def empezar_paso_a_paso(self, e=None, al_final=False):
        def accion():
            self.recorrido = self.a.simular(self._cadena())
            self.paso = len(self.recorrido.pasos) - 1 if al_final else 0
            self.avisar(self.mensaje_sim, "", GRIS)
            self.caminos.controls = []
            self._refrescar_simulacion()
            self.page.update()
        self.intentar(self.mensaje_sim, accion)

    def validar(self, e=None):
        self.empezar_paso_a_paso(al_final=True)

    def ir_a(self, k):
        if self.recorrido and 0 <= k < len(self.recorrido.pasos):
            self.paso = k
            self._refrescar_simulacion()
            self.page.update()

    def ver_caminos(self, e=None):
        def accion():
            lineas, aviso = K.caminos_en_texto(self.a, self._cadena())
            self.caminos.controls = ([ft.Text(f"Caminos de cómputo para {L.formatear_cadena(self._cadena())}",
                                              weight=ft.FontWeight.BOLD)]
                                     + [ft.Text(x, selectable=True, size=13) for x in lineas]
                                     + ([ft.Text(aviso, color=ROJO)] if aviso else []))
            self.page.update()
        self.intentar(self.mensaje_sim, accion)

    def _refrescar_simulacion(self):
        a, r = self.a, self.recorrido
        self.boton_caminos.visible = a.tipo != "AFD" and not a.validar()
        hay = r is not None
        for b in (self.boton_inicio, self.boton_anterior, self.boton_siguiente, self.boton_final):
            b.disabled = not hay
        if not hay:
            self.etiqueta_paso.value = "Sin simulación"
            self.banner.visible = False
            self.descripcion.value = ""
            self.traza.controls = []
            self.dibujo_sim.content = imagen_del_automata(D.svg_automata(a), 620, 360)
            return
        k, ultimo = self.paso, len(r.pasos) - 1
        self.boton_inicio.disabled = self.boton_anterior.disabled = k == 0
        self.boton_siguiente.disabled = self.boton_final.disabled = k == ultimo
        self.etiqueta_paso.value = f"{K.titulo_de_paso(r, k)}  (de {ultimo})"
        self.descripcion.value = K.descripcion_de_paso(a, r, k)
        if k == ultimo:
            corto, motivo = K.veredicto(a, r)
            self.texto_banner.value = f"{corto}: {motivo}"
            self.banner.bgcolor = ft.Colors.GREEN_100 if r.aceptada else ft.Colors.RED_100
            self.texto_banner.color = ft.Colors.GREEN_900 if r.aceptada else ft.Colors.RED_900
            self.banner.visible = True
        else:
            self.banner.visible = False
        paso = r.pasos[k]
        self.dibujo_sim.content = imagen_del_automata(D.svg_automata(a, paso.conjunto, paso.tomadas), 620, 360)
        self.traza.controls = [
            ft.Text(linea, selectable=True, size=13, weight=ft.FontWeight.BOLD if i == k else ft.FontWeight.NORMAL,
                    color=AZUL if i == k else None)
            for i, linea in enumerate(K.lineas_de_traza(a, r))]

    # ================================================================== Conversiones

    def _armar_conversiones(self):
        self.mensaje_conv = ft.Text(visible=False)
        self.titulo_conv = ft.Text(weight=ft.FontWeight.BOLD, size=16)
        self.detalle_conv = ft.Column(spacing=6)
        self.dibujo_conv = ft.Container()
        self.campo_nombre_conv = ft.TextField(label="Nombre para guardarlo", width=300, value="resultado")
        self.acciones_conv = ft.Row(wrap=True, visible=False, controls=[
            ft.Button(content="Usar como autómata actual", icon=ft.Icons.SWAP_HORIZ, on_click=self.usar_resultado),
            self.campo_nombre_conv,
            ft.OutlinedButton(content="Guardar el resultado (.jff, .json, .xml)", icon=ft.Icons.SAVE_ALT,
                              on_click=self.guardar_resultado)])
        self.campo_estado_clausura = ft.TextField(label="Estado", width=140, hint_text="q0",
                                                  on_submit=self.ver_clausura_de_estado)
        self.campo_ruta_b = ft.TextField(label="Segundo AFD (ruta .jff, .json o .xml)", width=520,
                                         hint_text="automatas/lista3-afd/Ej_153_minimo.jff",
                                         on_submit=self.comparar_con_otro)
        self.subconjuntos = None        # (conversión, renglones de la tabla) de la última construcción de subconjuntos
        self.vista_conversiones = ft.Column(spacing=14, scroll=ft.ScrollMode.AUTO, expand=True, controls=[
            ft.Text("Operan sobre el autómata actual. Un AFND-λ se convierte primero a AFND (quitando las λ) y "
                    "después a AFD: usa el resultado como autómata actual entre un paso y otro.", color=GRIS),
            ft.Row(wrap=True, controls=[
                ft.Button(content="λ-clausuras", icon=ft.Icons.TABLE_ROWS, on_click=self.ver_clausuras),
                ft.Button(content="Quitar transiciones λ", icon=ft.Icons.LINK_OFF, on_click=self.quitar_lambda),
                ft.Button(content="Convertir a AFD", icon=ft.Icons.ACCOUNT_TREE, on_click=lambda e: self.convertir(False)),
                ft.OutlinedButton(content="AFD completo (con ∅)", on_click=lambda e: self.convertir(True)),
                ft.Button(content="Minimizar AFD", icon=ft.Icons.COMPRESS, on_click=self.minimizar),
                ft.OutlinedButton(content="Quitar inaccesibles", on_click=self.quitar_inaccesibles)]),
            ft.Row(wrap=True, controls=[
                self.campo_estado_clausura,
                ft.OutlinedButton(content="λ-clausura de este estado", icon=ft.Icons.SEARCH,
                                  on_click=self.ver_clausura_de_estado)]),
            ft.Row(wrap=True, controls=[
                self.campo_ruta_b,
                ft.OutlinedButton(content="¿Son equivalentes? (AFD mínimos)", icon=ft.Icons.COMPARE_ARROWS,
                                  on_click=self.comparar_con_otro)]),
            self.mensaje_conv, self.titulo_conv, self.detalle_conv, self.acciones_conv, self.dibujo_conv,
        ])

    def _mostrar_resultado_vacio(self):
        self.titulo_conv.value = ""
        self.detalle_conv.controls = []
        self.dibujo_conv.content = None
        self.acciones_conv.visible = False
        self.avisar(self.mensaje_conv, "", GRIS)
        self.page.update()

    def _mostrar_conversion(self, titulo, resultado, detalle):
        self.resultado = resultado
        self.titulo_conv.value = titulo
        self.detalle_conv.controls = detalle
        self.dibujo_conv.content = imagen_del_automata(D.svg_automata(resultado), 700, 380) if resultado else None
        self.acciones_conv.visible = resultado is not None
        if resultado is not None:
            self.campo_nombre_conv.value = (self.a.nombre or "automata") + "_" + {"AFD": "afd"}.get(resultado.tipo, "res")
        self.avisar(self.mensaje_conv, "", GRIS)
        self.page.update()

    def ver_clausuras(self, e=None):
        def accion():
            self.a._exigir_valido()
            self._mostrar_conversion("λ-clausura de cada estado", None,
                                     [ft.Text("Cl(q) son los estados a los que se llega desde q usando solo transiciones λ, "
                                              "incluido q. En un autómata sin λ cada estado es su propia clausura.", color=GRIS),
                                      tabla_de_datos(["Estado", "Cl(estado)"], K.filas_de_clausuras(self.a))])
        self.intentar(self.mensaje_conv, accion)

    def ver_clausura_de_estado(self, e=None):
        def accion():
            q = (self.campo_estado_clausura.value or "").strip() or self.a.inicial
            self._mostrar_conversion(f"λ-clausura de {q}", None,
                                     [ft.Text(K.clausura_de_estado(self.a, q), selectable=True)])
        self.intentar(self.mensaje_conv, accion)

    def quitar_lambda(self, e=None):
        def accion():
            res = self.a.quitar_lambda_detalle()
            self._mostrar_conversion(
                "AFND sin transiciones λ", res.afn,
                [ft.Text(f"Mismos {len(res.afn.estados)} estados, {len(res.afn.transiciones())} transiciones.", color=GRIS)]
                + [ft.Text(x, selectable=True, size=13) for x in K.lineas_de_quitar_lambda(self.a, res)])
        self.intentar(self.mensaje_conv, accion)

    def convertir(self, completo):
        def accion():
            conv = self.a.a_afd(completo=completo)
            pasos = self.a.pasos_subconjuntos(completo=completo)
            self.subconjuntos = (conv, pasos)
            self._mostrar_conversion("AFD equivalente (construcción de subconjuntos)", conv.afd, [])
            self._dibujar_subconjuntos(1)
        self.intentar(self.mensaje_conv, accion)

    def _dibujar_subconjuntos(self, k):
        """Muestra los primeros k renglones de la tabla de la construcción; con todos, explica la aceptación."""
        conv, pasos = self.subconjuntos
        k = max(0, min(k, len(pasos)))
        n, m = len(self.a.estados), len(conv.afd.estados)
        controles = [
            ft.Text(f"El autómata original tiene {n} estados y el AFD {m}; la cota es 2^{n} = {2 ** n:,}. Se rechaza una "
                    f"conversión de más de {LIMITE_ESTADOS_AFD:,} estados. El estado inicial del AFD es la λ-clausura del "
                    "inicial del original. Cada renglón es δ'(S, a) = Cl(δ(S, a)).", color=GRIS),
            ft.Row(wrap=True, controls=[
                ft.OutlinedButton(content="Renglón anterior", icon=ft.Icons.CHEVRON_LEFT, disabled=k <= 0,
                                  on_click=lambda e: self._dibujar_subconjuntos(k - 1)),
                ft.Button(content="Siguiente renglón", icon=ft.Icons.CHEVRON_RIGHT, disabled=k >= len(pasos),
                          on_click=lambda e: self._dibujar_subconjuntos(k + 1)),
                ft.OutlinedButton(content="Mostrar todos", disabled=k >= len(pasos),
                                  on_click=lambda e: self._dibujar_subconjuntos(len(pasos))),
                ft.Text(f"Renglón {k} de {len(pasos)}", weight=ft.FontWeight.BOLD)]),
            ft.Row(scroll=ft.ScrollMode.AUTO, controls=[tabla_de_datos(
                ["Estado del AFD S", "Símbolo", "δ(S, a)", "Cl(δ(S, a))", "Destino", "¿Subconjunto nuevo?"],
                K.filas_de_pasos_de_subconjuntos(pasos[:k]))])]
        if k == len(pasos):
            controles.append(ft.Text("Estados de aceptación", weight=ft.FontWeight.BOLD))
            controles += [ft.Text(x, selectable=True, size=13) for x in K.lineas_de_aceptacion(self.a, conv)]
        self.detalle_conv.controls = controles
        self.page.update()

    def comparar_con_otro(self, e=None):
        def accion():
            otro = K.cargar(self.campo_ruta_b.value or "")
            res = comparar_por_minimo(self.a, otro)
            self._mostrar_conversion(
                "Equivalencia de dos AFD por sus AFD mínimos", res.minimo_a,
                [ft.Text(x, selectable=True, size=13) for x in K.lineas_de_equivalencia(res)])
        self.intentar(self.mensaje_conv, accion)

    def minimizar(self, e=None):
        def accion():
            particion = self.a.particiones()
            minimo = self.a.minimizar()
            self._mostrar_conversion(
                "AFD mínimo", minimo,
                [ft.Text(f"{len(self.a.estados)} estados → {len(minimo.estados)}. Se parte de {{aceptación}} y {{no aceptación}} y "
                         "se separan los estados que, con algún símbolo, van a clases distintas.", color=GRIS)]
                + [ft.Text(x, selectable=True, size=13) for x in K.lineas_de_particiones(particion)])
        self.intentar(self.mensaje_conv, accion)

    def quitar_inaccesibles(self, e=None):
        def accion():
            res = self.a.quitar_inaccesibles()
            quitados = [q for q in self.a.estados if q not in res.estados]
            self._mostrar_conversion(
                "Sin estados inaccesibles", res,
                [ft.Text("Estados que se quitaron: " + (", ".join(quitados) if quitados else "ninguno (todos son accesibles)"),
                         color=GRIS)])
        self.intentar(self.mensaje_conv, accion)

    def usar_resultado(self, e=None):
        if self.resultado is not None:
            self.a = self.resultado
            self.mostrar_lambda = self.a.tiene_lambda
            self.resultado = None
            self.cambio(editor=True)
            self._mostrar_resultado_vacio()

    def guardar_resultado(self, e=None):
        def accion():
            rutas = K.guardar_en_salidas(self.resultado, self.campo_nombre_conv.value)
            self.avisar(self.mensaje_conv, "Guardado en " + ", ".join(rutas), VERDE)
            self._refrescar_archivos()
            self.page.update()
        self.intentar(self.mensaje_conv, accion)

    # ================================================================== Varias cadenas

    def _armar_lotes(self):
        self.lote = None                # (cadenas, resultados, origen) de la última validación
        self.origen_cadenas = ""
        self.mensaje_lote = ft.Text(visible=False)
        self.campo_ruta_cadenas = ft.TextField(label="Archivo de texto (una cadena por línea)", width=520,
                                               hint_text="cadenas.txt", on_submit=self.cargar_archivo_de_cadenas)
        self.campo_cadenas = ft.TextField(label="Cadenas (una por línea; λ es la cadena vacía)", multiline=True,
                                          min_lines=6, max_lines=12, width=520)
        self.campo_nombre_informe = ft.TextField(label="Nombre del informe", width=300, value="informe")
        self.resumen_lote = ft.Text(weight=ft.FontWeight.BOLD, visible=False)
        self.tabla_lote = ft.Column()
        self.boton_informe = ft.Button(content="Guardar informe (.txt)", icon=ft.Icons.SAVE, disabled=True,
                                       on_click=self.guardar_informe_de_lote)
        self.vista_lotes = ft.Column(spacing=14, scroll=ft.ScrollMode.AUTO, expand=True, controls=[
            ft.Text("Valida muchas cadenas contra el autómata actual. Carga un archivo de texto con una cadena por "
                    "línea o escríbelas aquí; las líneas en blanco se ignoran y la cadena vacía se escribe «λ».",
                    color=GRIS),
            ft.Row(wrap=True, controls=[self.campo_ruta_cadenas,
                                         ft.Button(content="Cargar archivo", icon=ft.Icons.FILE_OPEN,
                                                   on_click=self.cargar_archivo_de_cadenas)]),
            self.campo_cadenas,
            ft.Row(wrap=True, controls=[ft.Button(content="Validar todas", icon=ft.Icons.PLAYLIST_PLAY,
                                                   on_click=self.validar_cadenas),
                                         self.campo_nombre_informe, self.boton_informe]),
            self.mensaje_lote, self.resumen_lote, self.tabla_lote,
        ])

    def cargar_archivo_de_cadenas(self, e=None):
        def accion():
            texto = self.campo_ruta_cadenas.value or ""
            cadenas = K.cargar_cadenas(texto)
            self.campo_cadenas.value = "\n".join(c if c else L.LAMBDA for c in cadenas)
            self.origen_cadenas = texto.strip()
            self.avisar(self.mensaje_lote, f"Se cargaron {len(cadenas):,} cadenas de {texto.strip()}.", VERDE)
            self.page.update()
        self.intentar(self.mensaje_lote, accion)

    def validar_cadenas(self, e=None):
        def accion():
            cadenas = K.leer_cadenas(self.campo_cadenas.value)
            if not cadenas:
                raise ValueError("Escribe o carga al menos una cadena.")
            resultados = K.validar_lote(self.a, cadenas)
            self.lote = (cadenas, resultados, self.origen_cadenas)
            n = len(resultados)
            cuenta = {v: sum(1 for _, x, _ in resultados if x == v) for v in ("ACEPTADA", "RECHAZADA", "ERROR")}
            self.avisar(self.mensaje_lote, "", GRIS)
            self.avisar(self.resumen_lote, f"{n:,} cadenas · aceptadas {cuenta['ACEPTADA']:,} · rechazadas "
                                           f"{cuenta['RECHAZADA']:,} · con error {cuenta['ERROR']:,}", AZUL)
            filas = [(i, w if w else L.LAMBDA, v, x) for i, (w, v, x) in enumerate(resultados[:LINEAS_VISIBLES], start=1)]
            controles = [ft.Row(scroll=ft.ScrollMode.AUTO,
                                controls=[tabla_de_datos(["#", "Cadena", "Resultado", "Explicación"], filas)])]
            if n > LINEAS_VISIBLES:
                controles.append(ft.Text(f"Se muestran las primeras {LINEAS_VISIBLES:,}; el informe guardado las incluye todas.",
                                         size=12, color=GRIS))
            self.tabla_lote.controls = controles
            self.boton_informe.disabled = False
            self.page.update()
        self.intentar(self.mensaje_lote, accion)

    def guardar_informe_de_lote(self, e=None):
        def accion():
            _, resultados, origen = self.lote
            ruta = K.guardar_informe(self.a, resultados, self.campo_nombre_informe.value, origen)
            self.avisar(self.mensaje_lote, f"Informe guardado en {ruta}", VERDE)
            self.page.update()
        self.intentar(self.mensaje_lote, accion)

    # ================================================================== Cadenas y lenguajes (Práctica 1)

    def _armar_lenguajes(self):
        self.ultimo = {}
        # Operación 1
        self.entrada1 = ft.TextField(label="Cadena", hint_text="Ejemplo: abc (vacío = λ)", width=360, on_submit=self.calcular1)
        self.mensaje1 = ft.Text(visible=False)
        self.resumen1 = ft.Text(visible=False, weight=ft.FontWeight.BOLD)
        self.resultados1 = ft.Row(wrap=True, spacing=12, vertical_alignment=ft.CrossAxisAlignment.START)
        self.guardar1 = ft.Button(content="Guardar en archivo", icon=ft.Icons.SAVE, disabled=True, on_click=self.guardar_op1)
        vista1 = ft.Column(spacing=14, scroll=ft.ScrollMode.AUTO, expand=True, controls=[
            ft.Text("Escribe una cadena para ver todos sus prefijos, sufijos y subcadenas distintas. "
                    f"{L.LAMBDA} es la cadena vacía.", color=GRIS),
            ft.Row(wrap=True, controls=[self.entrada1, ft.Button(content="Calcular", icon=ft.Icons.PLAY_ARROW,
                                                                on_click=self.calcular1), self.guardar1]),
            self.mensaje1, self.resumen1, self.resultados1])
        # Operación 2
        self.alfabeto2 = ft.TextField(label="Alfabeto", hint_text="Ejemplo: a, b", width=260)
        self.longitud2 = ft.TextField(label="Longitud máxima", hint_text="Ejemplo: 3", width=180,
                                      keyboard_type=ft.KeyboardType.NUMBER)
        self.mensaje2 = ft.Text(visible=False)
        self.resumen2 = ft.Text(visible=False, weight=ft.FontWeight.BOLD)
        self.resultados2 = ft.Row(wrap=True, spacing=12, vertical_alignment=ft.CrossAxisAlignment.START)
        self.guardar2 = ft.Button(content="Guardar en archivo", icon=ft.Icons.SAVE, disabled=True, on_click=self.guardar_op2)
        vista2 = ft.Column(spacing=14, scroll=ft.ScrollMode.AUTO, expand=True, controls=[
            ft.Text("Calcula Σ* (cerradura de Kleene, con λ) o Σ⁺ (cerradura positiva, sin λ) hasta la longitud que elijas. "
                    f"Se rechaza lo que pase de {L.LIMITE_CADENAS:,} cadenas o de longitud {L.LONGITUD_MAXIMA:,}.", color=GRIS),
            ft.Row(wrap=True, controls=[self.alfabeto2, self.longitud2]),
            ft.Row(wrap=True, controls=[
                ft.Button(content="Calcular Σ*", icon=ft.Icons.PLAY_ARROW, on_click=self.calcular2(False)),
                ft.Button(content="Calcular Σ⁺", icon=ft.Icons.PLAY_ARROW, on_click=self.calcular2(True)),
                self.guardar2]),
            self.mensaje2, self.resumen2, self.resultados2])
        self.vista_lenguajes = ft.Tabs(length=2, expand=True, content=ft.Column(expand=True, controls=[
            ft.TabBar(tabs=[ft.Tab(label="Prefijos, sufijos y subcadenas"), ft.Tab(label="Cerraduras Σ* y Σ⁺")]),
            ft.TabBarView(expand=True, controls=[vista1, vista2])]))

    def guardar_texto(self, nombre, texto):
        """Guarda el texto en salidas/ y devuelve la ruta relativa al proyecto."""
        K.CARPETA_SALIDAS.mkdir(exist_ok=True)
        ruta = K.CARPETA_SALIDAS / f"{nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        ruta.write_text(texto, encoding="utf-8", newline="\n")
        return ruta.relative_to(K.RAIZ).as_posix()

    def calcular1(self, e=None):
        w = (self.entrada1.value or "").strip()
        try:
            pre, suf, sub = L.prefijos(w), L.sufijos(w), L.subcadenas(w)
        except ValueError as error:
            self.ultimo.pop("op1", None)
            self.guardar1.disabled = True
            self.resumen1.visible = False
            self.resultados1.controls = []
            self.avisar(self.mensaje1, str(error), ROJO)
        else:
            self.ultimo["op1"] = w
            self.guardar1.disabled = False
            self.mensaje1.visible = False
            self.avisar(self.resumen1, f"Longitud {len(w)}  ·  Prefijos: {len(pre)}  ·  Sufijos: {len(suf)}  ·  "
                                       f"Subcadenas distintas: {len(sub):,} (máximo posible: {L.cantidad_maxima_subcadenas(len(w)):,})",
                        None)
            self.resultados1.controls = [tarjeta("Prefijos", pre, 200), tarjeta("Sufijos", suf, 200),
                                         tarjeta("Subcadenas distintas", sub, 260)]
        self.page.update()

    def guardar_op1(self, e=None):
        ruta = self.guardar_texto("prefijos_sufijos_subcadenas", L.texto_operacion1(self.ultimo["op1"]))
        self.avisar(self.mensaje1, f"Guardado en {ruta}", VERDE)
        self.page.update()

    def calcular2(self, positiva):
        def manejador(e):
            try:
                simbolos = L.parsear_alfabeto(self.alfabeto2.value or "")
                try:
                    n = int((self.longitud2.value or "").strip())
                except ValueError:
                    raise ValueError("La longitud máxima debe ser un número entero.") from None
                cadenas = (L.cerradura_positiva if positiva else L.cerradura_kleene)(simbolos, n)
            except ValueError as error:
                self.ultimo.pop("op2", None)
                self.guardar2.disabled = True
                self.resumen2.visible = False
                self.resultados2.controls = []
                self.avisar(self.mensaje2, str(error), ROJO)
            else:
                self.ultimo["op2"] = (simbolos, n, cadenas, positiva)
                self.guardar2.disabled = False
                self.mensaje2.visible = False
                nombre = "Σ⁺" if positiva else "Σ*"
                self.avisar(self.resumen2, f"{nombre} con Σ = {{{', '.join(simbolos)}}} y longitud máxima {n}: "
                                           f"{len(cadenas):,} cadenas", None)
                self.resultados2.controls = [tarjeta(nombre, cadenas, 360)]
            self.page.update()
        return manejador

    def guardar_op2(self, e=None):
        simbolos, n, cadenas, positiva = self.ultimo["op2"]
        ruta = self.guardar_texto("cerradura_positiva" if positiva else "cerradura_kleene",
                                  L.texto_cerradura(simbolos, n, cadenas, positiva))
        self.avisar(self.mensaje2, f"Guardado en {ruta}", VERDE)
        self.page.update()


def main(page: ft.Page):
    Aplicacion(page)


if __name__ == "__main__":
    ft.run(main)
