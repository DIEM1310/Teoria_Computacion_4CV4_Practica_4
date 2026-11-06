# Ejercicio 1. Conversión de AFD a expresiones regulares

Se eligieron cinco AFD de la Lista 3, los ejercicios **254 a 258**, cuyos archivos están en [automatas/practica3/afd-a-er/](../../automatas/practica3/afd-a-er/). Son los AFD de la Lista 3 de los que el enunciado pide la expresión regular, y tienen entre 2 y 3 estados, lo que permite revisar a mano cada paso.

**Cómo leer este documento.** Cada apartado tiene lo que ya está calculado y verificado con el software del repositorio (la expresión, la traza de eliminación de estados y la prueba de 6 cadenas en autómata y expresión), y lo que entrega JFLAP 7.1: la expresión de `Convert FA to RE`, el resultado de `Convert to NFA` con `Compare Equivalence` y la prueba de las cadenas con `Multiple Run`. JFLAP elige su propio orden de eliminación, así que su expresión puede ser distinta de la de este documento aunque sea equivalente; en cada ejercicio se indica si coinciden.

**Cómo se obtuvieron los resultados de JFLAP.** El ejercicio 254 se hizo en la interfaz de JFLAP 7.1 (con capturas). Los ejercicios 255 a 258 se obtuvieron ejecutando las mismas clases de `JFLAP7.1.jar` desde la línea de comandos, sin abrir la ventana: `FSAToRegularExpressionConverter` (*Convert FA to RE*), la conversión de expresión a NFA (*Convert to NFA*), `FSAEqualityChecker` (*Compare Equivalence*) y el simulador de entradas (*Multiple Run*). El script está en [herramientas/jflap_practica3.js](../../herramientas/jflap_practica3.js) y se ejecuta con `jjs -cp JFLAP7.1.jar herramientas/jflap_practica3.js` desde la raíz del repositorio. El 254 se hizo por las dos vías y coinciden en todo: la expresión `(0*11*0)*0*11*`, el NFA de 28 estados, la equivalencia y las seis respuestas de *Multiple Run*. Para los otros cuatro no hay capturas de JFLAP; el orden en que la interfaz elimina los estados puede variar si se eligen a mano, y con él la forma de la expresión.

La verificación con el software usa `expresiones.desde_automata` y `expresiones.acepta` ([src/expresiones.py](../../src/expresiones.py)): la expresión de cada autómata se probó con **todas** las cadenas de longitud hasta 9 sobre su alfabeto.

## 1.1 Conversión con JFLAP

Procedimiento en JFLAP 7.1 (Anexo 1 del enunciado), igual para los cinco:

1. *File → Open* y abrir el `.jff` de la carpeta `afd-a-er/`.
2. *Convert → Convert FA to RE*. Se agregan primero un estado inicial y un estado final nuevos (autómata generalizado); se eliminan los estados uno por uno con la herramienta de colapsar estados y se anota la expresión de cada arista tras cada eliminación.
3. Con la expresión final: *Convert → Convert to NFA* (en la ventana de la expresión) y guardar el autómata resultante.
4. *Test → Compare Equivalence* entre el original y el NFA obtenido.
5. *Input → Multiple Run* con las seis cadenas de la tabla de cada autómata.

### Resumen

| Ej. | Estados | Inicial | Aceptación | Expresión regular (eliminación de estados) | Forma simplificada |
|---|---|---|---|---|---|
| 254 | A, B | A | B | `(0+11*0)*11*` | `(0+1)*1` |
| 255 | A, B | A | A | `((0+1)1*0)*` | no se simplifica |
| 256 | A, B | A | B | `(1+2)*0(0+1+2(1+2)*0)*` | no se simplifica |
| 257 | A, B, C | A | B, C | `((1+01*0)(0+1))*(01*+1+01*0)` | `((1+01*0)(0+1))*(01*(λ+0)+1)` |
| 258 | A, B, C | A | C | `(0+1)(01+(1+00)(0+1))*` | no se simplifica |

### Ejercicio 254

**Análisis previo.** Σ = {0, 1}. Cada estado va a B con 1 y a A con 0, sea cual sea el estado de origen, así que el estado en que se está es siempre el último símbolo leído. Hay un lazo con 0 en A, un lazo con 1 en B y el ciclo A → B → A. Por eso se anticipa que la expresión empieza con `0*1` (llegar a B por primera vez) seguida de una repetición de ciclos que regresan a B; el lenguaje debería ser «cadenas que terminan en 1».

**Eliminación de estados** (orden B, A; autómata generalizado con estados `inicio` y `fin`):

| Estado eliminado | Aristas que quedan |
|---|---|
| B (lazo `1`, entrada A→B `1`, salida B→A `0`, B→fin `λ`) | A→A: `0+11*0`; A→fin: `11*`; inicio→A: `λ` |
| A (lazo `0+11*0`) | inicio→fin: `(0+11*0)*11*` |

Con el orden A, B se obtiene `0*1(1+00*1)*`, también equivalente.

**Resultado de JFLAP 7.1** (*Convert FA to RE*): `(0*11*0)*0*11*`. No coincide letra por letra con la de este documento, pero es equivalente: se comparó con el autómata y con `(0+11*0)*11*` sobre todas las cadenas de longitud 0 a 12 y no hubo ninguna discrepancia. Los tres describen «cadenas que terminan en 1». JFLAP elige su propio orden de eliminación, que puede diferir del de este documento.

**Verificación** (autómata contra expresión y contra JFLAP, con *Input → Multiple Run* sobre el AFD):

| Cadena | Autómata | Expresión | JFLAP (Multiple Run) |
|---|---|---|---|
| λ | rechaza | rechaza | Reject |
| 1 | acepta | acepta | Accept |
| 01 | acepta | acepta | Accept |
| 110 | rechaza | rechaza | Reject |
| 0101 | acepta | acepta | Accept |
| 10 | rechaza | rechaza | Reject |

Captura: `evidencias/practica3/jflap_254_multiplerun.png`.

`Convert to NFA` + `Compare Equivalence`: se escribió `(0*11*0)*0*11*` en una expresión regular de JFLAP, se convirtió a NFA (autómata de 28 estados con transiciones λ, construcción de Thompson) y se comparó con el AFD original. JFLAP respondió «They ARE equivalent!». Captura: `evidencias/practica3/jflap_254_equivalencia.png`.

**Simplificación.** Leyes de Hopcroft, Motwani y Ullman (2007), sección 3.4 (leyes algebraicas de las expresiones regulares):

1. `(0+11*0)*11*`
2. `= ((λ+11*)0)*11*` — identidad de la concatenación (`0 = λ0`) y ley distributiva derecha.
3. `= (1*0)*11*` — ley de la clausura `λ + RR* = R*`, con R = 1.
4. `= (1*0)*1*1` — ley de la clausura `RR* = R*R`, con R = 1.
5. `= (0+1)*1` — identidad `(R*S)*R* = (R+S)*` con R = 1 y S = 0, que se demuestra así: toda cadena de (R*S)*R* es una cadena de (R+S)*; y a la inversa, una cadena de (R+S)* se parte después de cada aparición de un símbolo de S en bloques «R*S» y un resto «R*».

El resultado confirma el pronóstico del análisis previo: las cadenas que terminan en 1. Equivalencia comprobada con el software para todas las cadenas hasta longitud 9.

### Ejercicio 255

**Análisis previo.** A es inicial y de aceptación; por lo tanto, λ ∈ L. De A se va a B con cualquier símbolo, en B se queda con 1 y se regresa a A con 0. El único ciclo que pasa por A es A → B → A con la forma «cualquier símbolo, 1*, un 0». Se anticipa `((0+1)1*0)*`.

**Eliminación de estados** (orden B, A):

| Estado eliminado | Aristas que quedan |
|---|---|
| B (lazo `1`, A→B `0+1`, B→A `0`) | A→A: `(0+1)1*0`; A→fin: `λ`; inicio→A: `λ` |
| A (lazo `(0+1)1*0`) | inicio→fin: `((0+1)1*0)*` |

**Resultado de JFLAP 7.1** (*Convert FA to RE*): `((0+1)1*0)*`, la misma expresión de este documento. Como A es inicial y de aceptación, JFLAP primero crea un estado final nuevo («Make Single Noninitial Final State»).

**Verificación:**

| Cadena | Autómata | Expresión | JFLAP (Multiple Run) |
|---|---|---|---|
| λ | acepta | acepta | Accept |
| 1 | rechaza | rechaza | Reject |
| 01 | rechaza | rechaza | Reject |
| 110 | acepta | acepta | Accept |
| 0101 | rechaza | rechaza | Reject |
| 10 | acepta | acepta | Accept |

`Convert to NFA` + `Compare Equivalence`: la expresión de JFLAP `((0+1)1*0)*` se convirtió a un NFA de 16 estados y el comprobador de equivalencia de JFLAP (el de *Compare Equivalence*) lo da **equivalente** al AFD original.

**Simplificación.** No se simplifica: el bloque `(0+1)1*0` no tiene factor común ni alternativas repetidas. Se intentó `λ+(0+1)(0+1)*0`, pero no es equivalente (acepta 000, que el autómata rechaza).

### Ejercicio 256

**Análisis previo.** Σ = {0, 1, 2}. En A hay un lazo con 1 y 2; en B, un lazo con 0 y 1. Desde A se pasa a B con 0 y desde B se vuelve a A con 2. Hay dos ciclos grandes: el lazo de B y el ciclo B → A → B (2, luego (1+2)*, luego 0). Se anticipa una expresión de la forma `(1+2)*0 ( 0+1 + 2(1+2)*0 )*`.

**Eliminación de estados** (orden A, B):

| Estado eliminado | Aristas que quedan |
|---|---|
| A (lazo `1+2`, inicio→A `λ`, A→B `0`, B→A `2`) | inicio→B: `(1+2)*0`; B→B: `0+1+2(1+2)*0`; B→fin: `λ` |
| B (lazo `0+1+2(1+2)*0`) | inicio→fin: `(1+2)*0(0+1+2(1+2)*0)*` |

**Resultado de JFLAP 7.1** (*Convert FA to RE*): `((1+2)*0(0+1)*2)*(1+2)*0(0+1)*` (30 símbolos). Es distinta de la de este documento (22 símbolos) pero equivalente: se comparó con el autómata y con `(1+2)*0(0+1+2(1+2)*0)*` sobre todas las cadenas de longitud 0 a 10 sin ninguna discrepancia.
**Verificación:**

| Cadena | Autómata | Expresión | JFLAP (Multiple Run) |
|---|---|---|---|
| λ | rechaza | rechaza | Reject |
| 1 | rechaza | rechaza | Reject |
| 01 | acepta | acepta | Accept |
| 110 | acepta | acepta | Accept |
| 0101 | acepta | acepta | Accept |
| 2 | rechaza | rechaza | Reject |

`Convert to NFA` + `Compare Equivalence`: la expresión de JFLAP `((1+2)*0(0+1)*2)*(1+2)*0(0+1)*` se convirtió a un NFA de 44 estados y el comprobador de equivalencia de JFLAP (el de *Compare Equivalence*) lo da **equivalente** al AFD original.

**Simplificación.** No se simplifica: los dos factores `(1+2)*0` y `(0+1+2(1+2)*0)*` no comparten términos, y distribuir alargaría la expresión.

### Ejercicio 257

**Análisis previo.** Σ = {0, 1}; A inicial; B y C de aceptación. Desde A: 0 → B, 1 → C. En B hay un lazo con 1 y B → C con 0. C regresa a A con cualquier símbolo. El único ciclo que pasa por A tiene dos caminos: A → C → A y A → B → C → A. Se anticipa `(ciclo en A)*` seguido de las ramas que terminan en B o en C.

**Eliminación de estados** (orden B, C, A):

| Estado eliminado | Aristas que quedan |
|---|---|
| B (lazo `1`, A→B `0`, B→C `0`) | A→C: `1+01*0`; A→fin: `01*`; C→A: `0+1`; C→fin: `λ`; inicio→A: `λ` |
| C (sin lazo; entra A→C, sale C→A y C→fin) | A→A: `(1+01*0)(0+1)`; A→fin: `01*+1+01*0`; inicio→A: `λ` |
| A (lazo `(1+01*0)(0+1)`) | inicio→fin: `((1+01*0)(0+1))*(01*+1+01*0)` |

**Resultado de JFLAP 7.1** (*Convert FA to RE*): `((1+01*0)(0+1))*(01*+1+01*0)`, la misma expresión de este documento. Como hay dos estados de aceptación (B y C), JFLAP primero crea un estado final nuevo.

**Verificación:**

| Cadena | Autómata | Expresión | JFLAP (Multiple Run) |
|---|---|---|---|
| λ | rechaza | rechaza | Reject |
| 1 | acepta | acepta | Accept |
| 01 | acepta | acepta | Accept |
| 110 | acepta | acepta | Accept |
| 0101 | rechaza | rechaza | Reject |
| 10 | rechaza | rechaza | Reject |

`Convert to NFA` + `Compare Equivalence`: la expresión de JFLAP `((1+01*0)(0+1))*(01*+1+01*0)` se convirtió a un NFA de 48 estados y el comprobador de equivalencia de JFLAP (el de *Compare Equivalence*) lo da **equivalente** al AFD original.

**Simplificación.** Leyes de Hopcroft et al. (2007), sección 3.4:

1. `01*+1+01*0`
2. `= 01*+01*0+1` — conmutatividad de la unión.
3. `= 01*λ+01*0+1` — identidad de la concatenación (`R = Rλ`).
4. `= 01*(λ+0)+1` — ley distributiva izquierda.

La expresión resultante `((1+01*0)(0+1))*(01*(λ+0)+1)` tiene la misma longitud (28 símbolos) que la original; la ganancia es solo estructural, porque factoriza el sufijo común `01*` en vez de escribirlo dos veces. Es equivalente (comprobado para todas las cadenas hasta longitud 10).

### Ejercicio 258

**Análisis previo.** Σ = {0, 1}; A inicial; C de aceptación. De A se va a C con cualquier símbolo; C va a B con 0 y a A con 1; B regresa a A con 0 y a C con 1. El estado de aceptación C tiene tres ciclos que regresan a él: C → A → C, C → B → C y C → B → A → C. Se anticipa un prefijo `(0+1)` seguido de la repetición de esos tres ciclos.

**Eliminación de estados** (orden B, A, C):

| Estado eliminado | Aristas que quedan |
|---|---|
| B (entra C→B `0`, sale B→A `0` y B→C `1`) | A→C: `0+1`; C→A: `1+00`; C→C: `01`; C→fin: `λ`; inicio→A: `λ` |
| A (entra inicio y C, sale A→C) | C→C: `01+(1+00)(0+1)`; C→fin: `λ`; inicio→C: `0+1` |
| C (lazo `01+(1+00)(0+1)`) | inicio→fin: `(0+1)(01+(1+00)(0+1))*` |

**Resultado de JFLAP 7.1** (*Convert FA to RE*): `((0+1)(01)*(1+00))*(0+1)(01)*` (29 símbolos). Es distinta de la de este documento (22 símbolos) pero equivalente: se comparó con el autómata y con `(0+1)(01+(1+00)(0+1))*` sobre todas las cadenas de longitud 0 a 10 sin ninguna discrepancia.

**Verificación:**

| Cadena | Autómata | Expresión | JFLAP (Multiple Run) |
|---|---|---|---|
| λ | rechaza | rechaza | Reject |
| 1 | acepta | acepta | Accept |
| 01 | rechaza | rechaza | Reject |
| 110 | acepta | acepta | Accept |
| 0101 | rechaza | rechaza | Reject |
| 10 | rechaza | rechaza | Reject |

`Convert to NFA` + `Compare Equivalence`: la expresión de JFLAP `((0+1)(01)*(1+00))*(0+1)(01)*` se convirtió a un NFA de 44 estados y el comprobador de equivalencia de JFLAP (el de *Compare Equivalence*) lo da **equivalente** al AFD original.

**Simplificación.** No se simplifica: aplicar la ley distributiva al lazo da `01+10+11+000+001`, que es más larga y no se reduce más.

## 1.2 Comparación de métodos

Se obtuvo a mano la expresión de los autómatas **254** y **255** por tres métodos: eliminación de estados, construcción de las expresiones R_ij^(k) y sistema de ecuaciones con el lema de Arden. Los tres resultados se probaron con el software para todas las cadenas hasta longitud 10.

**Referencias por método.**

| Método | Dónde se apoya |
|---|---|
| Eliminación de estados | Hopcroft, Motwani y Ullman (2007), sección 3.2.2 (eliminación de estados en el autómata generalizado) |
| Expresiones R_ij^(k) | Hopcroft et al. (2007), sección 3.2.1 y teorema 3.4 |
| Sistema de ecuaciones y lema de Arden | Apunte del curso: Hurtado Avilés (s. f.), *Conversión de AFD a ER con el Lema de Arden* (semestre 2027/1), que sigue a De Castro Korgi (2004), secciones 2.10 a 2.12. El libro de Hopcroft et al. (2007) no desarrolla este método con ese nombre. |

**Leyes que se citan en los métodos 2 y 3** (numeración del apunte, que toma las leyes de Hopcroft et al. (2007), sección 3.4): R1 `R+∅ = R`; R2 `R∅ = ∅R = ∅`; R3 `Rλ = λR = R`; R4 `RT+ST = (R+S)T` (factor común por la derecha); R5 `(RS)T = R(ST)`; R6 `λ+RR* = R*`. Además se usan la ley distributiva por la izquierda, `R(S+T) = RS+RT`, y la conmutatividad de la unión, `R+S = S+R`.

### Autómata 254 (A inicial, B de aceptación; A–0→A, A–1→B, B–0→A, B–1→B)

**Método 1: eliminación de estados.** Es el cálculo de arriba (orden B, A): se obtiene **`(0+11*0)*11*`**. Pasos: 2 eliminaciones y 3 aristas actualizadas.

**Método 2: R_ij^(k).** Se numeran A = 1 y B = 2. R_ij^(k) = R_ij^(k−1) + R_ik^(k−1) (R_kk^(k−1))* R_kj^(k−1).

| | R_11 | R_12 | R_21 | R_22 |
|---|---|---|---|---|
| k = 0 | `λ+0` | `1` | `0` | `λ+1` |
| k = 1 | `(λ+0)+(λ+0)(λ+0)*(λ+0)` = `0*` | `1+(λ+0)(λ+0)*1` = `0*1` | `0+0(λ+0)*(λ+0)` = `00*` | `(λ+1)+0(λ+0)*1` = `λ+1+00*1` |

Con k = 2 solo hace falta R_12 (el lenguaje, porque A es inicial y B es el único de aceptación):

R_12^(2) = R_12^(1) + R_12^(1) (R_22^(1))* R_22^(1) = R_12^(1) (R_22^(1))* = **`0*1(1+00*1)*`**

(se usó `R + RS*S = RS*`, que sale de `S* = λ + S*S`, y `λ+1+00*1` dentro de la estrella equivale a `1+00*1`). Se calcularon 4 + 4 + 1 = 9 expresiones.

**Método 3: sistema de ecuaciones y lema de Arden.** Lema de Arden: si λ ∉ L(S), la ecuación X = SX + T tiene como solución X = S*T.

```
X_A = 0 X_A + 1 X_B
X_B = 0 X_A + 1 X_B + λ        (B es de aceptación)
```

De la segunda, X_B = 1 X_B + (0 X_A + λ), y por Arden X_B = 1*(0 X_A + λ) = 1*0 X_A + 1* (distributiva y R3). Se sustituye en la primera:

X_A = 0 X_A + 1(1*0 X_A + 1*) = 0 X_A + 11*0 X_A + 11* (distributiva y R5) = (0 + 11*0) X_A + 11* (R4)

y por Arden X_A = **`(0+11*0)*11*`**, que es la expresión del lenguaje (A es inicial). Pasos: 2 ecuaciones, 2 aplicaciones del lema y 1 sustitución.

### Autómata 255 (A inicial y de aceptación; A–0→B, A–1→B, B–0→A, B–1→B)

**Método 1: eliminación de estados.** Orden B, A: **`((0+1)1*0)*`**. Pasos: 2 eliminaciones y 3 aristas actualizadas.

**Método 2: R_ij^(k).** A = 1, B = 2.

| | R_11 | R_12 | R_21 | R_22 |
|---|---|---|---|---|
| k = 0 | `λ` | `0+1` | `0` | `λ+1` |
| k = 1 | `λ+λλ*λ` = `λ` | `(0+1)+λλ*(0+1)` = `0+1` | `0+0λ*λ` = `0` | `(λ+1)+0λ*(0+1)` = `λ+1+00+01` |

R_11^(2) = R_11^(1) + R_12^(1) (R_22^(1))* R_21^(1) = **`λ+(0+1)(1+00+01)*0`**. Se calcularon 9 expresiones.

**Método 3: Arden.**

```
X_A = 0 X_B + 1 X_B + λ        (A es de aceptación)
X_B = 0 X_A + 1 X_B
```

De la segunda, X_B = 1 X_B + 0 X_A, y por Arden X_B = 1*0 X_A. Se sustituye: X_A = 0 X_B + 1 X_B + λ = (0+1) X_B + λ (R4) = (0+1)1*0 X_A + λ (R5), y por Arden X_A = ((0+1)1*0)*λ = **`((0+1)1*0)*`** (R3). Pasos: 2 ecuaciones, 1 aplicación del lema en cada ecuación y 1 sustitución.

### Comparación

| | Autómata 254 | Autómata 255 |
|---|---|---|
| Longitud de la expresión: eliminación de estados | 12 símbolos | 11 |
| Longitud: R_ij^(k) | 12 | 18 |
| Longitud: Arden | 12 | 11 |
| Cálculos (eliminación) | 2 eliminaciones, 3 aristas | 2 eliminaciones, 3 aristas |
| Cálculos (R_ij^(k)) | 9 expresiones | 9 expresiones |
| Cálculos (Arden) | 2 ecuaciones, 2 aplicaciones del lema | 2 ecuaciones, 2 aplicaciones del lema |

- **Longitud.** La eliminación de estados y Arden dieron expresiones más cortas que R_ij^(k) en el 255, porque R_ij^(k) trabaja con todas las parejas (i, j) en cada nivel y arrastra términos como `λ+1+00+01` que solo se simplifican al final. En el 254 las tres dieron la misma longitud; con el orden A, B la eliminación de estados da `0*1(1+00*1)*`, que es la misma expresión que R_ij^(k).
- **Número de pasos.** R_ij^(k) hace un número fijo de cálculos (del orden de n³ expresiones para n estados, aquí 9 para n = 2), aunque la mayoría no entre al resultado. La eliminación y Arden trabajan solo con las aristas que existen: para estos dos autómatas, 3 actualizaciones. Con autómatas dispersos esto es una ventaja; con muchos estados las tres técnicas crecen.
- **Facilidad.** La eliminación de estados es la más visual (se hace directamente sobre el diagrama y es lo que automatiza JFLAP), pero el resultado depende del orden en que se eliminan los estados. R_ij^(k) es mecánica y no depende de ninguna decisión, pero es la más larga de escribir a mano. Arden es corta para pocos estados y exige cuidado con la condición λ ∉ L(S) y con la sustitución; para autómatas con muchos ciclos entrelazados se vuelve difícil de seguir.

## Referencias

Hopcroft, J. E., Motwani, R. y Ullman, J. D. (2007). *Introducción a la teoría de autómatas, lenguajes y computación* (3.ª ed.). Pearson Addison-Wesley. Secciones 3.2.1, 3.2.2 y 3.4. Ficha completa en [bibliografía](../bibliografia.md).

Rodger, S. H. y Finley, T. W. (2006). *JFLAP: An interactive formal languages and automata package*. Jones & Bartlett.
