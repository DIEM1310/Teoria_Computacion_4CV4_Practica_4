# Ejercicio 2. De expresión regular a autómata

## 2.1 El analizador de la notación del curso

`expresiones.parsear` (ya de la Práctica 3) y la nueva `expresiones.parsear_sin_simplificar` son un analizador recursivo descendente para la gramática de la notación del curso:

```
unión          ::= concatenación ('+' concatenación)*
concatenación  ::= estrella+
estrella       ::= átomo '*'*
átomo          ::= '(' unión ')' | 'λ' | '∅' | símbolo
```

que respeta la precedencia del enunciado (cerradura > concatenación > unión) porque cada nivel de la gramática llama al siguiente nivel, más alto en precedencia, antes de mirar su propio operador. Los espacios se ignoran y cualquier otro carácter se trata como símbolo. Una expresión mal formada se rechaza con `expresiones.ErrorDeSintaxis` (subclase de `ValueError`) **indicando la posición del error** dentro del texto ya sin espacios:

| Texto | Mensaje |
|---|---|
| `(a` | Falta cerrar un paréntesis abierto, cerca de la posición 2 de `'(a'`. |
| `a)` | Sobra «)» en la posición 1 de `'a)'`. |
| `*a` | Una estrella sin nada que repetir, en la posición 0 de `'*a'`. |
| `a+` | Falta una expresión cerca de la posición 2 de `'a+'`. |
| `a++b` | Falta una expresión cerca de la posición 2 de `'a++b'`. |

La diferencia entre las dos funciones es que `parsear` arma el árbol con los constructores que **simplifican** (`union`, `concat`, `estrella`, ya de la Práctica 3 y documentados en `docs/practica4/01-investigacion.md`, sección 1.4), mientras que `parsear_sin_simplificar` arma el árbol **literal**, un nodo por cada operador escrito, sin aplanar ni descartar nada. La construcción de Thompson usa la segunda: si se simplificara antes, una pieza como `b+∅` del ejercicio 272(e) se perdería (`union()` descarta ∅) y la construcción ya no mostraría el caso básico de ∅ que pide ese ejercicio.

## 2.2 La construcción de Thompson (Parte I del teorema de Kleene)

`expresiones.desde_expresion(e, alfabeto)` recorre el árbol de `e` en orden de profundidad y arma el AFN-λ de abajo hacia arriba, con los cuatro casos de la sección 1.3 de la investigación:

- **∅**: dos estados nuevos, sin ninguna transición entre ellos.
- **λ**: dos estados nuevos, con una transición λ del primero al segundo.
- **símbolo a**: dos estados nuevos, con una transición «a» del primero al segundo.
- **unión** (n partes): un estado inicial y un estado final nuevos; una λ del inicial a cada pieza y una λ de cada pieza al final.
- **concatenación** (n partes): sin estados nuevos; una λ del final de cada pieza al inicial de la siguiente.
- **cerradura**: un estado inicial y un estado final nuevos; cuatro λ: saltarse la pieza (inicial→final), entrar a ella (inicial→inicial de la pieza), repetirla (final de la pieza→inicial de la pieza) y terminar (final de la pieza→final).

Cada pieza tiene siempre **un solo estado inicial y un solo estado de aceptación**, y nunca se reutiliza el inicial o el final de una pieza como el de la pieza que la contiene: se agregan dos estados nuevos en cada unión y en cada cerradura. Esto no es un detalle de implementación menor: el ejercicio 274 de la Lista 4 pide aplicar el atajo contrario —hacer final el estado inicial de la pieza y agregarle una λ de vuelta desde su final, para ahorrarse los dos estados nuevos— al autómata de `a*b` (q0 con un lazo `a` y q0 --b--> q1, q1 final). Con el atajo, q0 pasaría a ser también de aceptación, así que **λ se aceptaría**, que no pertenece a (a\*b)\*; la construcción correcta no tiene este problema porque el nuevo estado inicial del `*` no hereda ser de aceptación del estado que envuelve, solo le llega una λ si la pieza se repite cero veces. `tests/test_expresiones.py::test_la_estrella_no_reutiliza_el_inicio_ni_el_final_de_la_pieza` comprueba justamente que el autómata de `E*` tiene más estados que el de `E`.

Al terminar, el autómata se renombra q0, q1, ... con un recorrido a lo ancho desde el inicial (`construcciones.renombrar_secuencial`, de la Práctica 3) para que no queden los nombres internos `t0, t1, ...` que usa la construcción mientras arma las piezas.

## 2.3 Ejercicio 272: AFN-λ para cinco expresiones sobre Σ = {a, b}

Para cada expresión, la tabla da el texto de cada pieza, el caso de la Parte I que se aplicó y los estados nuevos; el autómata ya renombrado se exporta a `.jff` (pestaña *Expresión → autómata* → *Usar el AFN-λ final como autómata actual* → pestaña *Archivos* → *Guardar .jff*, exactamente como cualquier otro resultado de una conversión de la Práctica 3).

### 272(a). a + b\*

| Pieza | Caso | Estados nuevos |
|---|---|---|
| `a` | básico «a» | 2 |
| `b` | básico «b» | 2 |
| `b*` | cerradura | 2 (reutiliza los 2 de `b`) |
| `a+b*` | unión (2 partes) | 2 (reutiliza los de `a` y los de `b*`) |

AFN-λ final: **8 estados, 10 transiciones**. Por la Práctica 3: sin λ, 8 estados; AFD (subconjuntos), 4 estados; AFD mínimo, 4 estados.

### 272(b). (ab)\*a

| Pieza | Caso |
|---|---|
| `a` | básico «a» |
| `b` | básico «b» |
| `ab` | concatenación (2 partes, sin estados nuevos) |
| `(ab)*` | cerradura |
| `a` | básico «a» (una segunda pieza, con sus propios estados) |
| `(ab)*a` | concatenación (2 partes, sin estados nuevos) |

AFN-λ final: **8 estados, 9 transiciones**. AFD, 4 estados; AFD mínimo, **3 estados**.

### 272(c). (a+b)\*abb

| # | Pieza | Caso |
|---|---|---|
| 1 | `a` | básico «a» |
| 2 | `b` | básico «b» |
| 3 | `a+b` | unión de 2 partes |
| 4 | `(a+b)*` | cerradura |
| 5 | `a` | básico «a» |
| 6 | `b` | básico «b» |
| 7 | `b` | básico «b» |
| 8 | `(a+b)*abb` | concatenación de **4** partes: `(a+b)*`, `a`, `b`, `b` (sin estados nuevos) |

AFN-λ final: **14 estados, 16 transiciones** (q0 a q13). Sin λ, 14 estados; AFD, 5 estados; AFD mínimo, **4 estados**. Es el ejemplo con más piezas de los cinco porque la concatenación final tiene cuatro factores, no dos.

### 272(d). a(ba)\* + b

| # | Pieza | Caso |
|---|---|---|
| 1 | `a` | básico «a» |
| 2 | `b` | básico «b» |
| 3 | `a` | básico «a» (pieza aparte de la 1, con sus propios estados) |
| 4 | `ba` | concatenación de 2 |
| 5 | `(ba)*` | cerradura |
| 6 | `a(ba)*` | concatenación de 2 |
| 7 | `b` | básico «b» (pieza aparte de la 2) |
| 8 | `a(ba)*+b` | unión de 2 |

AFN-λ final: **12 estados, 14 transiciones**. AFD, 6 estados; AFD mínimo, **5 estados**.

### 272(e). (a + λ)(b + ∅)

| # | Pieza | Caso |
|---|---|---|
| 1 | `a` | básico «a» |
| 2 | `λ` | básico λ |
| 3 | `a+λ` | unión de 2 |
| 4 | `b` | básico «b» |
| 5 | `∅` | básico ∅ (dos estados sin ninguna transición) |
| 6 | `b+∅` | unión de 2 |
| 7 | `(a+λ)(b+∅)` | concatenación de 2 |

AFN-λ final: **12 estados, 12 transiciones**. Son dos estados menos que en 272(d) a pesar de tener el mismo número de piezas, porque el caso ∅ no agrega ninguna transición. AFD, 4 estados; AFD mínimo, **4 estados**. Este ejercicio es el que justifica usar `parsear_sin_simplificar`: con `parsear` (el que simplifica), `b+∅` se reduciría a `b` y el caso básico ∅ nunca se construiría.

## 2.4 Ejercicio 273: verificación por λ-clausuras

Para los autómatas de 272(b) y 272(c), `Automata.acepta` (de la Práctica 3) hace la λ-clausura del estado inicial y, después de cada símbolo, la λ-clausura del conjunto de estados activos; es el mismo procesamiento que usa la pestaña *Simulación* paso a paso.

| Cadena | 272(b) `(ab)*a` | 272(c) `(a+b)*abb` |
|---|---|---|
| `aba` | **acepta** (`ab`¹ más `a`) | rechaza (no termina en `abb`) |
| `ab` | rechaza (termina en `b`, no en `a`) | rechaza (demasiado corta) |
| `babb` | rechaza (no empieza con `a`) | **acepta** (termina en `abb`) |
| `abab` | rechaza (longitud 4; `(ab)*a` tiene longitud impar) | rechaza (termina en `ab`, no en `abb`) |

`tests/test_expresiones.py::test_ejercicio_273_cadenas_contra_272b_y_272c` compara estos cuatro resultados con `re.fullmatch(r"(ab)*a", w)` y `re.fullmatch(r"(?:[ab])*abb", w)`.

## 2.5 Ejercicio 278: el ciclo completo

Para `(a+b)*b`, Thompson da un AFN-λ de **10 estados y 12 transiciones** (5 piezas: `a`, `b`, `a+b`, `(a+b)*`, `b`, más la concatenación final). Al quitar las λ (Práctica 3) se conservan los 10 estados; la construcción de subconjuntos da un AFD de 3 estados y, al minimizar, quedan **2 estados**: uno no aceptación (el último símbolo leído fue `a`, o la cadena está vacía) y uno de aceptación (el último símbolo leído fue `b`), que es exactamente «termina en b». El Ejercicio 3 (sección 3.3 de ese documento) retoma este mismo autómata mínimo para aplicarle el Lema de Arden y comparar.

## 2.6 Casos de prueba de la Lista 3 (241 a 253)

El enunciado pide también los ejercicios 241 a 253 de la Lista 3 como casos de prueba. Esos ejercicios no llevan asterisco (son opcionales) y, por eso, no están en la entrega de la Lista 3 de este repositorio (`Polo_Santoscoy_Diego_2025630828.pdf`, que cubre del 151 al 263 pero salta del 240 al 254); no se tiene el enunciado exacto para transcribirlo aquí sin inventarlo. En su lugar, el motor se comprobó de dos formas que no dependen de ese enunciado puntual:

1. Con las 35 afirmaciones verdadero/falso de los ejercicios 201 a 235 y las cinco expresiones de los ejercicios 236 a 240, ya construidas en `tests/test_expresiones.py` desde la Práctica 3 (siguen la misma sección "Expresiones regulares" de la Lista 3 que continúa en 241): `tests/test_practica4.py::test_el_motor_completo_equivale_a_la_expresion_por_fuerza_bruta` las vuelve a probar, ahora pasándolas por `desde_expresion` y comparando el AFD mínimo contra la definición del lenguaje por fuerza bruta.
2. Con una muestra de 20 expresiones adicionales de distintas formas (uniones, concatenaciones y cerraduras anidadas, sobre alfabetos de uno y dos símbolos), en la misma prueba.

Si se consigue el enunciado de los ejercicios 241 a 253, agregarlos a `EXPRESIONES_LISTA4` (`src/ejercicios.py`) es automático: cada entrada solo necesita el texto en la notación del curso y el alfabeto.
