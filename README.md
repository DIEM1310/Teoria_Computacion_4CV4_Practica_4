# Práctica 3: JFLAP, AFD a expresiones regulares y extensión del software (AFN-λ, subconjuntos y minimización)

Instituto Politécnico Nacional · Escuela Superior de Cómputo

| Dato | Valor |
|---|---|
| Alumno | Diego Polo Santoscoy |
| Boleta | 2025630828 |
| Grupo | 4CV4 |
| Carrera | Ingeniería en Sistemas Computacionales |
| Unidad de aprendizaje | Teoría de la Computación |
| Profesor | Gabriel Hurtado Avilés |
| Fecha límite de entrega | 4 de noviembre de 2026 |
| Etiqueta de Git | `practica3` |

## Objetivo

Relacionar los autómatas finitos con las expresiones regulares mediante JFLAP, e incorporar al software interactivo, programados en Python, los algoritmos que transforman un AFN con transiciones λ en un AFD mínimo.

## Índice de la práctica

| Ejercicio | Documento |
|---|---|
| 1. Conversión de AFD a expresiones regulares (JFLAP y a mano) | [docs/practica3/01-afd-a-er-jflap.md](docs/practica3/01-afd-a-er-jflap.md) |
| 2. Extensión del software interactivo (con capturas) | [docs/practica3/02-software.md](docs/practica3/02-software.md) |
| 3. Documentación de los algoritmos | [docs/practica3/03-algoritmos.md](docs/practica3/03-algoritmos.md) |
| Bibliografía | [docs/bibliografia.md](docs/bibliografia.md) |

Los autómatas de esta práctica están en [automatas/practica3/](automatas/practica3/): `afd-a-er/` (los cinco AFD del Ejercicio 1, ejercicios 254 a 258 de la Lista 3) y `casos-de-prueba/` (los 19 autómatas de la Lista 3 que usan las pruebas). Las capturas y salidas de pytest van en [evidencias/practica3/](evidencias/practica3/).

## Repositorio anterior

El entorno de contenedores, el núcleo del autómata y la interfaz proceden de la Práctica 2 y se continúan aquí. Las carpetas `automatas/lista2-afd/`, `lista3-afd/`, `lista3-afnd/`, `lista3-afnd-lambda/`, `conversiones/` y `aplicacion/` son las de esa práctica. Repositorio de la Práctica 2: <https://github.com/DIEM1310/Teoria_Computacion_4CV4_Practica_2>

## Cómo levantar el entorno y ejecutar las pruebas

Hace falta **Docker Desktop** encendido. La interfaz usa **Flet 0.86.5** (versión fijada en [requirements.txt](requirements.txt)). Hay tres contenedores, uno por versión de Python (3.11, 3.12 y 3.13). Los comandos se ejecutan desde la carpeta `entorno/`:

| Para... | Comando |
|---|---|
| Construir las tres imágenes | `docker compose build` |
| Ejecutar las pruebas en cada contenedor | `docker compose run --rm py311 pytest -q`, y lo mismo con `py312` y `py313` |
| Abrir el simulador | `docker compose up py312` y abrir http://localhost:8550 en el navegador |
| Apagar y limpiar | `docker compose down` |

Las mismas pruebas se ejecutan en GitHub Actions con las tres versiones de Python en cada confirmación y en cada Pull Request ([.github/workflows/pruebas.yml](.github/workflows/pruebas.yml)).

## Uso de las funciones nuevas de la Práctica 3

Todas están en el simulador (pestañas *Simulación*, *Conversiones* y *Varias cadenas*). Primero se carga un autómata en la pestaña *Archivos* (por ejemplo `automatas/practica3/casos-de-prueba/Ej_196_tabla.jff`).

| Función | Cómo se usa |
|---|---|
| λ-clausura de cada estado | *Conversiones* → «λ-clausuras» |
| λ-clausura de un estado elegido | *Conversiones* → escribir el estado en «Estado» → «λ-clausura de este estado» |
| Simulación directa del AFN-λ, con los estados antes y después de la clausura | *Simulación* → escribir la cadena → «Paso a paso» y avanzar con las flechas |
| Eliminar transiciones λ | *Conversiones* → «Quitar transiciones λ» (muestra las transiciones añadidas y los estados que pasan a aceptación) |
| Construcción de subconjuntos | *Conversiones* → «Convertir a AFD» → «Siguiente renglón» (o «Mostrar todos»); al final explica qué subconjuntos son de aceptación y por qué |
| Quitar inaccesibles y minimizar un AFD | *Conversiones* → «Quitar inaccesibles» y «Minimizar AFD» (muestra la partición de cada ronda) |
| Decidir si dos AFD son equivalentes | *Conversiones* → escribir la ruta del segundo AFD → «¿Son equivalentes? (AFD mínimos)» |
| Validar varias cadenas | *Varias cadenas* → cargar un `.txt` con una cadena por línea (la cadena vacía se escribe `λ`) → «Validar todas» → «Guardar informe (.txt)» (se guarda en `salidas/`) |

Los resultados de las conversiones se pueden usar como autómata actual («Usar como autómata actual») para encadenar los pasos: AFN-λ → AFN → AFD → AFD mínimo, y se pueden guardar en `.jff`, `.json` y `.xml`.

Los algoritmos también se pueden usar sin la interfaz, desde Python (con `src/` en la ruta):

```python
import formatos as F
from automata import comparar_por_minimo

a = F.leer_archivo("automatas/practica3/casos-de-prueba/Ej_196_tabla.jff")
print(a.clausuras())                                  # λ-clausura de cada estado
print(a.simular("001").texto(a.estados))              # simulación directa
sin_lambda = a.quitar_lambda_detalle().afn            # AFN sin transiciones λ
afd = sin_lambda.a_afd().afd                          # construcción de subconjuntos
minimo = afd.minimizar()                              # AFD mínimo
print(comparar_por_minimo(afd, minimo).equivalentes)  # equivalencia por AFD mínimos
```

## Estructura del repositorio

| Carpeta o archivo | Contenido |
|---|---|
| `src/automata.py` | Núcleo del autómata: definición, λ-clausura, simulación, eliminación de λ, subconjuntos, minimización y equivalencia (no depende de Flet) |
| `src/formatos.py` | Lectura y escritura de `.jff`, `.json` y `.xml` (no depende de Flet) |
| `src/controlador.py`, `src/dibujo.py`, `src/construcciones.py` | Lógica de la interfaz, diagramas SVG y constructores de patrones (no dependen de Flet) |
| `src/ejercicios.py`, `src/expresiones.py` | Autómatas de la Lista 3 y expresiones regulares (no dependen de Flet) |
| `src/lenguajes.py` | Operaciones sobre cadenas y lenguajes (Práctica 1) |
| `src/app.py` | Interfaz gráfica con Flet (el único módulo que importa Flet) |
| `tests/test_practica3.py` | Pruebas de la Práctica 3 (equivalencia de las cuatro versiones, eliminación de λ, subconjuntos, minimización, equivalencia, lotes) |
| `tests/` | El resto de las pruebas con pytest |
| `automatas/` | Autómatas en `.jff`, `.json` y `.xml` |
| `docs/practica3/` | Documentos de la práctica, en Markdown |
| `evidencias/practica3/` | Capturas y salidas de pytest |
| `herramientas/` | Scripts de la Práctica 2 que generan y verifican los autómatas, y `jflap_practica3.js`, que repite con las clases de JFLAP 7.1 el Ejercicio 1.1 (expresión, NFA, equivalencia y *Multiple Run*) |

## Formatos de archivo y convención para λ

El simulador lee y escribe `.jff` (formato de JFLAP), `.json` y `.xml`. **La transición λ se escribe con la cadena vacía como símbolo leído** en los tres formatos: `<read/>` en `.jff`, `"lee": ""` en `.json` y `lee=""` en `.xml`. En pantalla y en la documentación se muestra con el símbolo `λ`, por lo que `λ` no puede ser un símbolo del alfabeto. El campo `tipo` toma los valores `AFD`, `AFND` o `AFND-lambda`.

## Entrega

La entrega se identifica con la etiqueta de Git `practica3`.
