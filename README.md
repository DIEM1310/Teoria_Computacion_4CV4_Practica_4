# Práctica 4: uso de las expresiones regulares y extensión del software para convertirlas (teorema de Kleene)

Instituto Politécnico Nacional · Escuela Superior de Cómputo

| Dato | Valor |
|---|---|
| Alumno | Diego Polo Santoscoy |
| Boleta | 2025630828 |
| Grupo | 4CV4 |
| Carrera | Ingeniería en Sistemas Computacionales |
| Unidad de aprendizaje | Teoría de la Computación |
| Profesor | Gabriel Hurtado Avilés |
| Fecha límite de entrega | 6 de noviembre de 2026 |
| Etiqueta de Git | `practica4` |

## Objetivo

Estudiar las expresiones regulares y sus aplicaciones, e incorporar al software interactivo las dos direcciones del teorema de Kleene: de una expresión regular a un autómata (construcción de Thompson) y de un autómata a una expresión regular (eliminación de estados, ya de la Práctica 3).

## Índice de la práctica

| Ejercicio | Documento |
|---|---|
| 1. Investigación sobre expresiones regulares | [docs/practica4/01-investigacion.md](docs/practica4/01-investigacion.md) |
| 2. De expresión regular a autómata (construcción de Thompson; ejercicios 272, 273 y 278 de la Lista 4) | [docs/practica4/02-regex-a-automata.md](docs/practica4/02-regex-a-automata.md) |
| 3. De autómata a expresión regular (eliminación de estados; ejercicios 254 a 258 de la Lista 3 y 276, 277 y 278 de la Lista 4) | [docs/practica4/03-automata-a-regex.md](docs/practica4/03-automata-a-regex.md) |
| 4. Aplicaciones: validadores (fecha, teléfono, contraseña) | [docs/practica4/04-validadores.md](docs/practica4/04-validadores.md) |
| Bibliografía | [docs/bibliografia.md](docs/bibliografia.md) |

Los autómatas nuevos de esta práctica están en [automatas/practica4/](automatas/practica4/) (los ejercicios 276 y 277 de la Lista 4); los cinco AFD de 254 a 258 ya estaban en [automatas/practica3/afd-a-er/](automatas/practica3/afd-a-er/) y se reutilizan tal cual (sección 3.4 del Ejercicio 3). Los ejercicios 241 a 253 de la Lista 3, que el enunciado también pide como casos de prueba, son opcionales y no están en la entrega de la Lista 3 de este repositorio; la sección 2.6 de `docs/practica4/02-regex-a-automata.md` explica cómo se cubrió esa parte sin inventar el enunciado.

## Repositorio anterior

El entorno de contenedores, el núcleo del autómata, los formatos de archivo y la interfaz de la Práctica 3 se continúan aquí sin cambios; lo nuevo son `src/validadores.py` y las extensiones de `src/expresiones.py`, `src/automata.py`, `src/controlador.py`, `src/ejercicios.py` y `src/app.py` que describen los documentos de esta práctica. Repositorio de la Práctica 3: <https://github.com/DIEM1310/Teoria_Computacion_4CV4_Practica_3>

## Cómo levantar el entorno y ejecutar las pruebas

Hace falta **Docker Desktop** encendido. La interfaz usa **Flet 0.86.5** (versión fijada en [requirements.txt](requirements.txt)). Hay tres contenedores, uno por versión de Python (3.11, 3.12 y 3.13). Los comandos se ejecutan desde la carpeta `entorno/`:

| Para... | Comando |
|---|---|
| Construir las tres imágenes | `docker compose build` |
| Ejecutar las pruebas en cada contenedor | `docker compose run --rm py311 pytest -q`, y lo mismo con `py312` y `py313` |
| Abrir el simulador | `docker compose up py312` y abrir http://localhost:8550 en el navegador |
| Apagar y limpiar | `docker compose down` |

Las mismas pruebas se ejecutan en GitHub Actions con las tres versiones de Python en cada confirmación y en cada Pull Request ([.github/workflows/pruebas.yml](.github/workflows/pruebas.yml)).

## Notación aceptada por el analizador

La misma de toda la práctica (`expresiones.parsear` y `expresiones.parsear_sin_simplificar`, en `src/expresiones.py`): `+` para la unión, la yuxtaposición para la concatenación, `*` para la cerradura de Kleene, `λ` para la palabra vacía, `∅` para el lenguaje vacío y paréntesis para agrupar. La cerradura liga más fuerte que la concatenación, y la concatenación más fuerte que la unión. Los espacios se ignoran; cualquier otro carácter se trata como un símbolo del alfabeto. Para alfabetos grandes, la documentación de esta práctica abrevia con clases declaradas por escrito (como `D = 0+1+...+9`); el analizador no entiende esa abreviatura como sintaxis, así que las expresiones que las usan (los validadores del Ejercicio 4) se construyen expandidas, símbolo por símbolo. Una expresión mal formada se rechaza con `expresiones.ErrorDeSintaxis` indicando la posición del error dentro del texto (ejemplos en `docs/practica4/02-regex-a-automata.md`, sección 2.1).

## Uso de las funciones nuevas de la Práctica 4

En el simulador, pestañas *Expresión → autómata*, *Autómata → expresión* y *Validadores*.

| Función | Cómo se usa |
|---|---|
| Construir el AFN-λ de una expresión (Ejercicio 2) | *Expresión → autómata* → escribir la expresión y el alfabeto → «Construir AFN-λ»; recorrer las piezas con las flechas |
| Usar ese AFN-λ como autómata actual | *Expresión → autómata* → «Usar el AFN-λ final como autómata actual»; de ahí, *Conversiones* (quitar λ, convertir a AFD, minimizar), *Archivos* (exportar a `.jff`) y *Simulación* (validar cadenas) siguen el resto del Ejercicio 2 con los algoritmos de la Práctica 3 |
| Verificar que un autómata importado sea un AFD (Ejercicio 3) | *Archivos* → cargar el `.jff` → *Autómata → expresión* → «Verificar que sea un AFD» (si no lo es, indica el estado y el símbolo) |
| Eliminar estados paso a paso | *Autómata → expresión* → «Eliminar estados (paso a paso)»; recorrer el autómata generalizado con las flechas, desde antes de eliminar nada hasta el final |
| Comprobar la expresión obtenida contra el Ejercicio 2 | *Autómata → expresión* → «Reconstruir y comparar» (reconstruye el AFN-λ de la expresión y compara su AFD mínimo con el del autómata actual) |
| Validadores (fecha, teléfono, contraseña) | *Validadores* → elegir uno en la lista → escribir un texto → «Validar»; muestra la notación, la traducción a `re`, los estados del AFD antes y después de minimizar, la justificación de qué queda fuera y el diagrama del AFD mínimo |

Los algoritmos también se pueden usar sin la interfaz, desde Python (con `src/` en la ruta):

```python
import expresiones as X
import validadores as V

# Ejercicio 2: de expresión a AFN-λ, y de ahí al AFD mínimo con la Práctica 3
e = X.parsear_sin_simplificar("(a+b)*abb")
afn, pasos = X.desde_expresion(e, "ab")           # Parte I del teorema de Kleene
minimo = afn.quitar_lambda().a_afd(completo=True).afd.minimizar()

# Ejercicio 3: de autómata a expresión, paso a paso
er, orden, pasos = X.desde_automata(minimo)       # Parte II del teorema de Kleene
print(str(er))

# Ejercicio 4: validadores
v = V.POR_CLAVE["fecha"]
etapas = V.construir_automata(v)
print(etapas.minimo.acepta("31/12/2026"), v.python_re)
```

## Estructura del repositorio

| Carpeta o archivo | Contenido |
|---|---|
| `src/automata.py` | Núcleo del autómata, ya de la Práctica 3, más `motivo_no_determinista` (Ejercicio 3) |
| `src/expresiones.py` | Árbol de expresiones y eliminación de estados (Práctica 3), más `desde_expresion` (construcción de Thompson, Ejercicio 2) y `parsear_sin_simplificar` |
| `src/validadores.py` | Los tres validadores del Ejercicio 4: expresión, traducción a `re`, autómata y generación de casos de prueba (no depende de Flet) |
| `src/formatos.py` | Lectura y escritura de `.jff`, `.json` y `.xml` (sin cambios desde la Práctica 3) |
| `src/controlador.py`, `src/dibujo.py`, `src/construcciones.py` | Lógica de la interfaz, diagramas SVG y constructores de patrones (no dependen de Flet) |
| `src/ejercicios.py` | Autómatas de la Lista 3 (Práctica 3) y de la Lista 4 (`EXPRESIONES_LISTA4`, `AUTOMATAS_LISTA4`) |
| `src/lenguajes.py` | Operaciones sobre cadenas y lenguajes (Práctica 1) |
| `src/app.py` | Interfaz gráfica con Flet, con las pestañas *Expresión → autómata*, *Autómata → expresión* y *Validadores* nuevas |
| `tests/test_practica4.py` | Pruebas de integración de las dos direcciones del teorema de Kleene (orden de eliminación igual al de la Práctica 3, ida y vuelta expresión-autómata-expresión) |
| `tests/test_validadores.py` | Congruencia de cada validador con `re.fullmatch` sobre quinientas cadenas |
| `tests/` | El resto de las pruebas con pytest, incluidas las de la Práctica 3 sin cambios |
| `automatas/practica4/` | Los autómatas nuevos de la Lista 4 (276 y 277) |
| `docs/practica4/` | Documentos de esta práctica, en Markdown |
| `evidencias/practica4/` | Capturas y salidas de pytest |
| `herramientas/generar_practica4.py` | Genera los `.jff`, `.json` y `.xml` de `automatas/practica4/` a partir de `ejercicios.AUTOMATAS_LISTA4` |

## Formatos de archivo y convención para λ

Sin cambios desde la Práctica 3: el simulador lee y escribe `.jff` (formato de JFLAP), `.json` y `.xml`. La transición λ se escribe con la cadena vacía como símbolo leído en los tres formatos (`<read/>`, `"lee": ""` y `lee=""`); en pantalla se muestra `λ`, por lo que `λ` no puede ser símbolo del alfabeto. El campo `tipo` toma los valores `AFD`, `AFND` o `AFND-lambda`.

## Entrega

La entrega se identifica con la etiqueta de Git `practica4`.
