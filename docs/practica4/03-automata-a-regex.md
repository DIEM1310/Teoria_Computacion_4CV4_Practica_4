# Ejercicio 3. De autómata a expresión regular

## 3.1 Verificar que el autómata importado sea un AFD

Antes de eliminar estados, `Automata.motivo_no_determinista()` (nuevo en esta práctica) recorre el autómata y devuelve `None` si ya es un AFD o, si no, el primer estado y símbolo que lo impiden: una transición λ (`"El estado «q» tiene una transición λ (hacia «r»): un AFD no tiene transiciones λ."`) o un `(estado, símbolo)` con más de un destino (`"El estado «q» tiene 2 transiciones con el símbolo «a» (hacia r1, r2): un AFD tiene a lo más una por estado y símbolo."`). La pestaña *Autómata → expresión* llama a esta función antes de permitir "Eliminar estados": si el autómata actual (importado en la pestaña *Archivos*, en `.jff`, `.json` o `.xml`) no es un AFD, se niega a continuar y muestra el motivo. `tests/test_automata.py` lo prueba con un AFD (sin motivo), con el AFND-λ del Anexo 3 del enunciado de la Práctica 2 (motivo: la transición λ de `q0`) y con un AFND del ejercicio 263 (motivo: `q0` tiene dos transiciones con `0`).

## 3.2 Eliminación de estados, paso a paso

El método es el mismo de la Práctica 3 (`expresiones.eliminar_en_orden` y `expresiones.desde_automata`, sección 1.3 de `docs/practica4/01-investigacion.md`): se arma el autómata generalizado agregando `inicio` (con una λ al estado inicial) y `fin` (con una λ desde cada estado de aceptación) y se elimina un estado a la vez, acumulando en cada arista la expresión de los caminos que pasaban por él. Lo nuevo de esta práctica es la interfaz: la pestaña *Autómata → expresión* muestra, para cada paso k (desde 0, antes de eliminar nada, hasta el número de estados), una tabla (origen, destino, expresión) con **todas** las aristas que quedan en ese momento —no solo las que cambiaron—, con botones para avanzar, retroceder, ir al principio o ir al final, igual que el paso a paso de la pestaña *Simulación*. `controlador.filas_del_automata_generalizado_inicial` arma la foto del paso 0 (con `expresiones.aristas_iniciales`, que antes era una función interna y ahora es pública porque la interfaz la necesita) y `controlador.filas_de_un_paso_de_eliminacion` arma la de los pasos siguientes.

Cuando no se da un orden, `desde_automata` prueba todas las permutaciones de los estados (hasta 6) y se queda con la expresión más corta; es el comportamiento que ya traía la Práctica 3 y que esta práctica reutiliza sin cambios.

## 3.3 Comprobar con el Ejercicio 2: reconstruir y comparar

El botón "Reconstruir y comparar" cierra el ciclo del teorema de Kleene sobre el autómata actual: toma la expresión que se acaba de obtener, le aplica la Parte I (`desde_expresion`, Ejercicio 2) y las tres etapas de la Práctica 3 (quitar λ, subconjuntos, minimizar), y compara el AFD mínimo resultante con el del autómata original usando `automata.comparar_por_minimo` —la misma prueba de equivalencia de la pestaña *Conversiones*, con el mismo texto (`controlador.lineas_de_equivalencia`)—. `controlador.reconstruir_y_comparar` hace esto desde el código; `tests/test_controlador.py::test_reconstruir_y_comparar_cierra_el_ciclo_del_teorema_de_kleene` y, para 276 y 277, `tests/test_expresiones.py::test_ejercicios_276_y_277_de_la_lista_4` lo comprueban automáticamente para cada caso de prueba de esta sección.

## 3.4 Comparación con JFLAP (Práctica 3): los cinco autómatas del Ejercicio 1

Los ejercicios 254 a 258 de la Lista 3 —los cinco autómatas del Ejercicio 1 de la Práctica 3, en `automatas/practica3/afd-a-er/`— ya se resolvieron con JFLAP y con el software en `docs/practica3/01-afd-a-er-jflap.md`. Esta práctica no repite ese trabajo: lo **reutiliza y lo extiende** por dos lados.

1. **El mismo orden de eliminación da la misma expresión.** `tests/test_practica4.py::test_el_orden_de_la_practica_3_da_la_misma_expresion_del_documento` llama a `eliminar_en_orden` con el orden exacto que usa ese documento para cada autómata (B, A para 254 y 255; A, B para 256; B, C, A para 257; B, A, C para 258) y compara el texto de la expresión contra el que aparece ahí, letra por letra:

   | Ejercicio | Orden | Expresión (Práctica 3 y esta práctica) |
   |---|---|---|
   | 254 | B, A | `(0+11*0)*11*` |
   | 255 | B, A | `((0+1)1*0)*` |
   | 256 | A, B | `(1+2)*0(0+1+2(1+2)*0)*` |
   | 257 | B, C, A | `((1+01*0)(0+1))*(01*+1+01*0)` |
   | 258 | B, A, C | `(0+1)(01+(1+00)(0+1))*` |

Captura de la pestaña *Autómata → expresión* con el ejercicio 254 (autómata generalizado antes de eliminar y expresión obtenida): `evidencias/practica4/ejercicio3_eliminacion_254.jpg`.

2. **La expresión, reconstruida, equivale al autómata original.** `tests/test_expresiones.py::test_los_cinco_autómatas_254_a_258_se_recuperan_con_desde_expresion` toma cada una de esas cinco expresiones, les aplica el Ejercicio 2 completo (Thompson, quitar λ, subconjuntos, minimizar) y compara el resultado con el AFD mínimo del autómata original por `comparar_por_minimo`: los cinco coinciden. Esta es la comprobación que pide el enunciado ("conviertiendo ambas en AFD mínimos con el Ejercicio 2 y comparándolos con la prueba de equivalencia de la Práctica 3"), aplicada a la expresión de JFLAP indirectamente: como `docs/practica3/01-afd-a-er-jflap.md` ya estableció que la expresión de JFLAP es equivalente a la de este software para cada uno de los cinco, y ahora la expresión de este software se comprueba equivalente al autómata reconstruido, las tres puntas de la comparación (JFLAP, este software, el autómata reconstruido) quedan conectadas.

## 3.5 Ejercicio 276: Lema de Arden

AFD sobre Σ = {a, b} (A inicial y de aceptación): A --a→ B, A --b→ A; B --a→ C, B --b→ B; C --a→ A, C --b→ C. Reconoce las cadenas cuyo número de letras «a» es múltiplo de 3 (incluido cero). Las ecuaciones de lenguajes (una por estado, con «+λ» en los de aceptación) son:

```
X_A = a X_B + b X_A + λ        (A es de aceptación)
X_B = a X_C + b X_B
X_C = a X_A + b X_C
```

De X_B, por el Lema de Arden (si λ ∉ L(S), la ecuación X = SX + T tiene como solución X = S\*T): X_B = b X_B + a X_C ⟹ X_B = b\*a X_C. De X_C, igual: X_C = b X_C + a X_A ⟹ X_C = b\*a X_A. Sustituyendo, X_B = b\*a(b\*a X_A) = b\*ab\*a X_A. Sustituyendo en la primera ecuación:

X_A = a(b\*ab\*a X_A) + b X_A + λ = ab\*ab\*a X_A + b X_A + λ = (ab\*ab\*a + b) X_A + λ

y, por Arden otra vez, **X_A = (b + ab\*ab\*a)\***. Es la misma expresión que da `desde_automata` con el orden de eliminación [B, C, A] (la de menor longitud entre las 6 permutaciones; con otros órdenes se obtienen formas distintas pero equivalentes, como `b*+b*ab*a(b+ab*ab*a)*ab*`). `tests/test_expresiones.py::test_ejercicios_276_y_277_de_la_lista_4` comprueba la equivalencia por software.

## 3.6 Ejercicio 277: método R_ij^(k) y Lema de Arden

La tabla de este ejercicio —A inicial, B de aceptación, A --0→ A, A --1→ B, B --0→ A, B --1→ B— es **la misma tabla** del ejercicio 254 de la Lista 3, ya resuelta por los tres métodos (eliminación, R_ij^(k) y Arden) en `docs/practica3/01-afd-a-er-jflap.md`, sección "Comparación de métodos". Se reutiliza ese cálculo en vez de repetirlo:

- **R_ij^(k)** (numerando A = 1, B = 2): R_12^(2) = R_12^(1)(R_22^(1))\* = **0\*1(1+00\*1)\***.
- **Arden**: de X_A = 0X_A + 1X_B y X_B = 0X_A + 1X_B + λ se obtiene X_B = 1\*0X_A + 1\*, y sustituyendo, X_A = (0+11\*0)X_A + 11\*, de donde **X_A = (0+11\*0)\*11\***.

Las dos expresiones se ven distintas pero son equivalentes (lo mismo que concluyó la Práctica 3 para el 254): la de R_ij^(k) sale de acumular caminos que pasan por cada estado intermedio, uno a la vez; la de Arden, de resolver el sistema de ecuaciones de una vez. `expresiones.desde_automata` sobre este autómata da, con el orden [A, B], exactamente `0*1(1+00*1)*`, y con [B, A], `(0+11*0)*11*`: las mismas dos formas.

**Cinco cadenas de prueba** (aceptadas y rechazadas), comprobadas contra el autómata y contra las dos expresiones:

| Cadena | Autómata | R_ij^(k) y Arden |
|---|---|---|
| `1` | acepta | acepta |
| `011` | acepta | acepta |
| `0101` | rechaza | rechaza |
| `00` | rechaza | rechaza |
| `1001` | rechaza | rechaza |

(Los ejemplos por sí solos no demuestran la equivalencia general, como advierte el enunciado; la demostración es la sustitución algebraica de arriba, y `tests/test_expresiones.py` la comprueba además para todas las cadenas hasta longitud 10.)

## 3.7 Ejercicio 278(d): Arden sobre el AFD mínimo de (a+b)\*b

El AFD mínimo de `(a+b)*b` que obtuvo el Ejercicio 2 (sección 2.5 de `docs/practica4/02-regex-a-automata.md`) tiene 2 estados —A inicial, sin aceptación; B de aceptación— con A --a→ A, A --b→ B, B --a→ A, B --b→ B: es la misma forma que el ejercicio 277 (sección 3.6), cambiando 0 por a y 1 por b. Las ecuaciones son X_A = aX_A + bX_B (A no es de aceptación) y X_B = aX_A + bX_B + λ (B sí lo es). De la segunda, por Arden, X_B = b\*(aX_A+λ) = b\*aX_A + b\*; sustituyendo en la primera, X_A = aX_A + b(b\*aX_A+b\*) = (a+bb\*a)X_A + bb\*, y por Arden otra vez: **X_A = (a + bb\*a)\*bb\***.

Esta expresión es distinta, letra por letra, de la original `(a+b)*b` y de la que da la eliminación de estados (`a*b(b+aa*b)*`, sección 2.5), pero las tres son equivalentes: `tests/test_practica4.py::test_ida_y_vuelta_expresion_automata_expresion` prueba precisamente este caso (entre otros) convirtiendo cada una a su AFD mínimo y comparando por `comparar_por_minimo`, y una verificación aparte confirmó que `(a+bb*a)*bb*`, `a*b(b+aa*b)*` y `(a+b)*b` coinciden en todas las cadenas de longitud hasta 10. El ciclo completo del ejercicio 278 queda así: expresión → AFN-λ (Thompson) → AFN sin λ → AFD (subconjuntos) → AFD mínimo → expresión (Arden) → de vuelta a un AFN-λ equivalente a la expresión original.
