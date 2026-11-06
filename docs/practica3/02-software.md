# Ejercicio 2. Extensión del software interactivo

La aplicación de la Práctica 2 (Flet 0.86.5) se amplió con los algoritmos de esta práctica. Cada uno se muestra paso a paso en la interfaz y se aplica a los autómatas importados desde archivos `.jff`. El núcleo (`src/automata.py`) y la lógica de la pantalla (`src/controlador.py`) no dependen de Flet, así que cada algoritmo se ejecuta y se prueba sin abrir la ventana. Los algoritmos están escritos en Python puro, sin bibliotecas de autómatas.

## Cómo abrir la aplicación

Desde la carpeta `entorno/` (requiere Docker Desktop):

```bash
docker compose up py312
```

y abrir <http://localhost:8550>. Las instrucciones completas del entorno están en el [README](../../README.md).

## Qué hace cada apartado y dónde está

| Apartado | Dónde en la interfaz | Función del núcleo | Prueba |
|---|---|---|---|
| 2.1 λ-clausura de cada estado | *Conversiones* → «λ-clausuras» | `Automata.clausuras()` | `test_clausuras_de_196_a_200` |
| 2.1 λ-clausura de un estado elegido | *Conversiones* → campo «Estado» y «λ-clausura de este estado» | `controlador.clausura_de_estado()` | `test_clausura_de_un_estado_elegido` |
| 2.1 Simulación directa, con estados antes y después de la clausura | *Simulación* → «Paso a paso» | `Automata.simular()` (`Paso.antes`, `Paso.conjunto`) | `test_cada_paso_guarda_los_estados_antes_y_despues_de_la_clausura` |
| 2.2 Eliminación de transiciones λ | *Conversiones* → «Quitar transiciones λ» | `Automata.quitar_lambda_detalle()` | `test_el_detalle_de_quitar_lambda_es_coherente_con_el_resultado` |
| 2.3 Construcción de subconjuntos | *Conversiones* → «Convertir a AFD» → «Siguiente renglón» | `Automata.pasos_subconjuntos()`, `a_afd()` | `test_la_tabla_paso_a_paso_reproduce_el_afd` |
| 2.3 Aceptación de los subconjuntos | al final de la tabla | `Automata.razon_de_aceptacion()` | `test_la_razon_de_aceptacion_dice_que_estado_la_causa` |
| 2.4 Inaccesibles y AFD mínimo, con las particiones | *Conversiones* → «Quitar inaccesibles» y «Minimizar AFD» | `quitar_inaccesibles()`, `particiones()`, `minimizar()` | `test_el_minimo_no_tiene_mas_estados_que_el_afd_del_que_procede` |
| 2.4 Equivalencia de dos AFD | *Conversiones* → ruta del segundo AFD y «¿Son equivalentes?» | `comparar_por_minimo()`, `isomorfismo()` | `test_dos_afd_distintos_pero_del_mismo_lenguaje_son_equivalentes` |
| 2.5 Validación de varias cadenas | pestaña *Varias cadenas* | `controlador.validar_lote()`, `guardar_informe()` | `test_validar_lote_da_un_resultado_por_cadena_y_no_se_detiene_en_los_errores` |
| 2.6 Pruebas automatizadas | — | — | `tests/test_practica3.py` |

La descripción de cada algoritmo, con pseudocódigo y complejidad, está en [03-algoritmos.md](03-algoritmos.md).

## Decisiones de diseño

**Simulación directa.** En la Práctica 2 se eligió simular siguiendo todos los caminos a la vez, sin convertir a AFD. Es exactamente lo que pide el apartado 2.1, de modo que no hizo falta implementar una segunda simulación; lo que faltaba era mostrar el conjunto de estados activos *antes* de aplicar la clausura. `Paso` tiene ahora el campo `antes` (resultado de aplicar δ al conjunto anterior) además de `conjunto` (después de la clausura). La descripción de cada paso en pantalla dice «Antes de la λ-clausura: … Después de la λ-clausura: …».

**Minimización.** Se eligió el refinamiento de particiones (método de Moore), una de las dos opciones que permite el enunciado. La pantalla muestra la partición de cada ronda. No se implementó la tabla de pares distinguibles.

**Equivalencia de dos AFD.** `comparar_por_minimo` minimiza los dos autómatas y busca una correspondencia entre estados (`isomorfismo`) que respete el estado inicial, los estados de aceptación y las transiciones. Esto sigue la definición del enunciado («sus autómatas mínimos coinciden salvo el nombre de los estados»). El decisor por recorrido del producto (`lenguajes_iguales`, de la Práctica 2) se conserva y se usa en las pruebas como segundo decisor.

**AFD parciales.** Un AFD sin transición para algún símbolo se acepta. Para minimizarlo se le agrega temporalmente un estado trampa, que se descarta al final, de modo que el mínimo de un AFD parcial también es parcial. Dos AFD parciales se comparan con esa misma convención.

**Eliminación de λ.** Se muestra el detalle (transiciones que se añaden, λ que desaparecen, estados que pasan a aceptación) y se puede usar el resultado como autómata actual para seguir con la construcción de subconjuntos.

## Formato del archivo de cadenas (apartado 2.5)

Un archivo de texto UTF-8 con una cadena por línea.

- Las líneas en blanco se ignoran.
- La cadena vacía se escribe `λ`.
- Una cadena con un símbolo que no es del alfabeto aparece como `ERROR` en el informe; no detiene la validación de las demás.
- El informe se guarda en `salidas/<nombre>.txt` e incluye: autómata, origen de las cadenas, fecha, una línea por cadena (número, cadena, resultado y explicación) y el total de aceptadas, rechazadas y con error.

Ejemplo de archivo para el ejercicio 263 (termina en 01), guardado como [automatas/practica3/casos-de-prueba/cadenas_263.txt](../../automatas/practica3/casos-de-prueba/cadenas_263.txt):

```
01
101
10
λ
```

## Pruebas (apartado 2.6)

`tests/test_practica3.py` comprueba, para cada uno de los 19 casos de prueba, que:

1. el autómata original, el AFN sin λ, el AFD de subconjuntos y el AFD mínimo aceptan **exactamente las mismas cadenas** del alfabeto hasta una longitud N que se calcula por caso (la justificación está al final de [03-algoritmos.md](03-algoritmos.md): N = max(p + q − 2, 6), con p y q los estados del AFD y del mínimo, ambos completados, por el teorema de Moore);
2. los cuatro son equivalentes según el decisor exacto `lenguajes_iguales`;
3. el AFD mínimo **no tiene más estados** que el AFD del que procede;
4. cada `.jff` entregado en `automatas/practica3/` reconoce el lenguaje del ejercicio al que corresponde.

Los casos son los ejercicios 151 a 157 (AFD), 192 a 194 y 260 a 263 (AFN) y 196 a 200 (AFN-λ) de la Lista 3. Se ejecutan con las tres versiones de Python en la integración continua (`.github/workflows/pruebas.yml`: 3.11, 3.12 y 3.13) y en los contenedores:

```bash
docker compose run --rm py311 pytest -q
docker compose run --rm py312 pytest -q
docker compose run --rm py313 pytest -q
```

El ejercicio 191 de la Lista 3 no tiene autómata propio: es el enunciado común de los ejercicios 192 a 195 («encuentre un AFD equivalente y calcule δ̂ y δ̂_D»), cuyas tablas están en cada uno de ellos. Por eso no está en el registro de ejercicios (`src/ejercicios.py`). Del intervalo 191 a 194 que pide el apartado 2.3, los autómatas son los de los ejercicios 192, 193 y 194, que sí son casos de prueba.

## Capturas

Las capturas van en [evidencias/practica3/](../../evidencias/practica3/). Falta tomarlas (la aplicación se debe abrir en el navegador). Las que respaldan este documento:

| Archivo sugerido | Qué mostrar |
|---|---|
| `evidencias/practica3/clausuras_196.png` | Ejercicio 196 cargado; *Conversiones* → «λ-clausuras» (clausura de cada estado) |
| `evidencias/practica3/clausura_estado_196.png` | Clausura de un estado elegido por el usuario (A) |
| `evidencias/practica3/simulacion_196.png` | *Simulación* con 001 en un paso intermedio (se ven «antes» y «después» de la clausura) |
| `evidencias/practica3/quitar_lambda_196.png` | «Quitar transiciones λ» con las transiciones añadidas |
| `evidencias/practica3/subconjuntos_196.png` | «Convertir a AFD» con la tabla completa y las razones de aceptación |
| `evidencias/practica3/minimizacion_156.png` | «Minimizar AFD» con las dos particiones |
| `evidencias/practica3/equivalencia_156_157.png` | Comparación de dos AFD no equivalentes (156 y 157) |
| `evidencias/practica3/equivalencia_156_minimo.png` | Comparación de un AFD con su propio mínimo (equivalentes) |
| `evidencias/practica3/lote_263.png` | Pestaña *Varias cadenas*: archivo cargado, resultados e informe guardado |
| `evidencias/practica3/pytest_py311.txt`, `pytest_py312.txt`, `pytest_py313.txt` | Salida de `pytest -q` en cada contenedor |
| `evidencias/practica3/ci_verde.png` | Pestaña *Actions* de GitHub con las tres versiones en verde |
