# Ejercicio 1. Investigación sobre expresiones regulares

## 1.1 Lenguaje regular y expresión regular

Sea Σ un alfabeto finito y Σ* el conjunto de todas las cadenas finitas sobre Σ, incluida la cadena vacía λ. Un **lenguaje** es cualquier subconjunto L ⊆ Σ*. La clase de los **lenguajes regulares** sobre Σ se define por recursión (Hopcroft, Motwani y Ullman, 2007, sección 3.1; Sipser, 2012, sección 1.3):

1. **Casos base.** El lenguaje vacío ∅, el lenguaje {λ} y, para cada símbolo a ∈ Σ, el lenguaje {a} son regulares.
2. **Casos inductivos.** Si L₁ y L₂ son regulares, también lo son:
   - la **unión** L₁ ∪ L₂ = {w : w ∈ L₁ o w ∈ L₂};
   - la **concatenación** L₁L₂ = {xy : x ∈ L₁, y ∈ L₂};
   - la **cerradura de Kleene** L₁* = {w₁w₂···wₙ : n ≥ 0, cada wᵢ ∈ L₁} (con n = 0 se obtiene λ).
3. Ningún otro lenguaje sobre Σ es regular.

Una **expresión regular** sobre Σ es, en cambio, una cadena de símbolos que *describe* un lenguaje regular siguiendo esa misma recursión, pero en la sintaxis: ∅ y λ son expresiones regulares, cada a ∈ Σ es una expresión regular y, si R y S son expresiones regulares, también lo son (R+S), (RS) y (R*). El **lenguaje de una expresión**, L(R), se obtiene aplicando las operaciones anteriores: L(∅) = ∅, L(λ) = {λ}, L(a) = {a}, L(R+S) = L(R) ∪ L(S), L(RS) = L(R)L(S) y L(R*) = L(R)*. Por eso, aunque "expresión regular" y "lenguaje regular" se usan a veces como sinónimos, son objetos distintos: la expresión es la notación (un árbol sintáctico, el tipo `ER` de [src/expresiones.py](../../src/expresiones.py)) y el lenguaje regular es el conjunto de cadenas que esa notación nombra; dos expresiones distintas, como `(a+b)*` y `a*(ba*)*`, pueden nombrar el mismo lenguaje (Sipser, 2012, sección 1.3).

La precedencia de los operadores, de mayor a menor, es cerradura, concatenación y unión; los paréntesis la alteran. Esta práctica usa la notación del curso: `+` para la unión, la yuxtaposición para la concatenación, `*` para la cerradura de Kleene, `λ` para la palabra vacía y `∅` para el lenguaje vacío (la misma que define el enunciado y que ya usaba `src/expresiones.py` desde la Práctica 3). Para alfabetos grandes, esta documentación abrevia con clases de símbolos, como `D = 0+1+...+9`; el analizador (`expresiones.parsear` y `expresiones.parsear_sin_simplificar`) no entiende esa abreviatura como sintaxis: las clases se expanden en el árbol antes de construir el autómata (así se hace en [src/validadores.py](../../src/validadores.py), función `_clase`).

## 1.2 Los lenguajes regulares en la jerarquía de Chomsky

Chomsky (1956) clasifica las gramáticas formales —y los lenguajes que generan— en cuatro tipos anidados: tipo 0 (sin restricción, aceptados por una máquina de Turing), tipo 1 (sensibles al contexto), tipo 2 (libres de contexto, aceptados por un autómata de pila) y tipo 3 (regulares). Los regulares son el nivel más restringido: **regulares ⊊ libres de contexto ⊊ sensibles al contexto ⊊ recursivamente enumerables** (Hopcroft, Motwani y Ullman, 2007, sección 1.1 y capítulo 9). Una gramática regular (tipo 3) solo permite producciones de la forma A → aB, A → a o A → λ (lineales por la derecha), lo que coincide con que un autómata finito solo recuerda "en qué estado está" y no puede llevar una pila ni una cinta. Por eso un lenguaje como {aⁿbⁿ : n ≥ 0} (sección 1.5) sí es libre de contexto —una gramática S → aSb | λ lo genera— pero no es regular: reconocerlo exigiría contar sin límite, y un autómata finito tiene memoria acotada (el mismo argumento que usa el lema de bombeo).

## 1.3 El teorema de Kleene

El **teorema de Kleene** (Kleene, 1956) establece la equivalencia entre las expresiones regulares y los autómatas finitos: *un lenguaje es regular si y solo si existe una expresión regular que lo describe* (Sipser, 2012, teorema 1.54, secciones 1.1–1.3). La demostración tiene dos direcciones independientes, que son justamente los Ejercicios 2 y 3 de esta práctica:

- **Parte I (expresión → autómata).** Para toda expresión regular R existe un AFN-λ que reconoce L(R). Se demuestra por inducción en la estructura de R, con una construcción para cada caso base (∅, λ, cada símbolo) y cada operador (unión, concatenación, cerradura); la construcción con dos estados nuevos por caso —la de Thompson (1968)— es la que implementa `expresiones.desde_expresion` (Hopcroft, Motwani y Ullman, 2007, sección 3.2.3, "Converting a Regular Expression to an Automaton" — *verificar el número exacto de sección y de teorema contra el ejemplar físico, igual que se dejó pendiente para la Práctica 3*; Sipser, 2012, lema 1.55).
- **Parte II (autómata → expresión).** Para todo AFD existe una expresión regular equivalente. Se demuestra con el **método de eliminación de estados** sobre el autómata generalizado: se agregan un estado `inicio` y un estado `fin`, y se quita un estado a la vez, acumulando en cada arista restante la expresión del camino que se perdería (Hopcroft, Motwani y Ullman, 2007, sección 3.2.2, teorema 3.4, citado ya en `docs/practica3/01-afd-a-er-jflap.md`). Es el método que implementa `expresiones.desde_automata` desde la Práctica 3 y que el Ejercicio 3 reutiliza tal cual.

Que las dos direcciones sean construcciones (no solo pruebas de existencia) es lo que permite programarlas: `desde_expresion` y `desde_automata` son, literalmente, el teorema de Kleene hecho código, y el ejercicio 278 de la Lista 4 ("el ciclo completo") las encadena una tras otra sobre la misma expresión para comprobar que el resultado es equivalente al original.

## 1.4 Leyes algebraicas usadas para simplificar (Práctica 3)

`src/expresiones.py` simplifica automáticamente al construir una expresión: `union()` aplana uniones anidadas, quita repetidos y descarta ∅; `concat()` aplana concatenaciones, descarta las λ de más y anula todo si aparece ∅; `estrella()` colapsa `∅* = λ* = λ`, `(R*)* = R*` y `(λ+R)* = R*`. Son, en notación de Hopcroft, Motwani y Ullman (2007, sección 3.4), las leyes:

| Ley | Identidad | Dónde se aplica |
|---|---|---|
| Identidad de la unión | R + ∅ = R | `union()` descarta los operandos ∅ |
| Idempotencia de la unión | R + R = R | `union()` quita repetidos |
| Conmutatividad y asociatividad de la unión | R + S = S + R; (R+S)+T = R+(S+T) | `union()` aplana en una sola lista y la compara por igualdad estructural |
| Identidad de la concatenación | Rλ = λR = R | `concat()` descarta los operandos λ |
| Anulación de la concatenación | R∅ = ∅R = ∅ | `concat()` devuelve ∅ si algún operando lo es |
| Asociatividad de la concatenación | (RS)T = R(ST) | `concat()` aplana las concatenaciones anidadas |
| Cerradura de ∅ y de λ | ∅* = λ* = λ | caso base de `estrella()` |
| Idempotencia de la cerradura | (R*)* = R* | caso `e.tipo == "estrella"` de `estrella()` |
| (λ+R)* = R* | — | caso `e.tipo == "union"` de `estrella()`, quita el sumando λ antes de cerrar |

Las leyes que requieren comparar dos *autómatas* en vez de dos árboles —como `(R*S)*R* = (R+S)*`, usada en `docs/practica3/01-afd-a-er-jflap.md` para el ejercicio 254— no están mecanizadas: se aplicaron a mano y se comprobaron con `expresiones.acepta` sobre muchas cadenas, porque demostrarlas en general exige un argumento sobre lenguajes, no una reescritura local del árbol.

## 1.5 Expresiones regulares de la teoría contra las de los lenguajes de programación

Las expresiones regulares de un lenguaje de programación —el módulo `re` de Python, PCRE, POSIX— **extienden** la notación teórica con construcciones que ya no describen necesariamente un lenguaje regular: clases de caracteres (`[a-z]`), cuantificadores acotados (`a{2,4}`), anclas (`^`, `$`, `\b`), *lookahead*/*lookbehind* y, sobre todo, las **referencias hacia atrás** (`\1`, `\2`, …), que repiten literalmente lo que capturó un grupo anterior (Davis, Michael IV, Coghlan, Servant y Lee, 2019, sección 2, documentan esta y otras extensiones no regulares en motores de uso real). `expresiones.a_python` traduce la notación del curso a `re` sin usar ninguna de estas extensiones —solo grupos no-capturantes `(?:...)`— precisamente para que la traducción siga describiendo un lenguaje regular.

**El patrón `(a*)b\1` no es regular.** Sobre Σ = {a, b}, ese patrón acepta exactamente las cadenas de la forma aⁿbaⁿ, con n ≥ 0: el grupo `(a*)` captura aⁿ, se exige la `b` literal y `\1` exige que lo que sigue sea, otra vez, exactamente lo que capturó el grupo. El lenguaje L = {aⁿbaⁿ : n ≥ 0} no es regular, por el lema de bombeo:

> **Demostración.** Supóngase, para contradicción, que L es regular, con longitud de bombeo p (la que da el lema para L). La cadena s = aᵖbaᵖ pertenece a L y |s| = 2p+1 ≥ p. Por el lema de bombeo existe una descomposición s = xyz con |xy| ≤ p, |y| ≥ 1 y xyⁱz ∈ L para todo i ≥ 0. Como |xy| ≤ p, la pieza xy está contenida por completo en el primer bloque de aes (antes de la única b de s), así que y = aᵏ para algún k ≥ 1. Al bombear con i = 0 se obtiene xz = a^(p−k) b aᵖ. Para que xz ∈ L, los dos exponentes de a tendrían que ser iguales, pero p − k ≠ p porque k ≥ 1: contradicción. Por lo tanto L no es regular. ∎

Esta es, además, la razón de fondo por la que un motor de expresiones regulares con referencias hacia atrás **no puede** implementarse con el algoritmo de esta práctica (AFN-λ, construcción de subconjuntos y minimización): esos algoritmos solo reconocen lenguajes regulares, y reconocer `(a*)b\1` exigiría comparar dos bloques de longitud arbitraria, para lo que un autómata finito no tiene memoria suficiente (el mismo argumento que para {aⁿbⁿ}, sección 1.2). Los motores reales que sí soportan referencias hacia atrás dejan de ser deterministas en tiempo polinomial: en general resuelven la búsqueda con retroceso (*backtracking*), que en el peor caso es exponencial en el tamaño de la cadena.

## 1.6 Cinco aplicaciones de las expresiones regulares

1. **Análisis léxico en compiladores.** El analizador léxico agrupa cada categoría de token (identificadores, enteros, operadores) como un lenguaje regular y construye un único AFD que los reconoce todos a la vez (exactamente la construcción de subconjuntos del Ejercicio 2, aplicada a la unión de un AFN-λ por categoría). Un identificador típico de C es `L(L+D)*`, con L = a+...+z+A+...+Z+\_ y D = 0+...+9: una letra o guion bajo, seguido de cualquier cantidad de letras, dígitos o guiones bajos. `src/validadores.py` usa la misma idea para la contraseña (`L(L+D)⁶D`).
2. **Búsqueda de patrones en texto.** Herramientas como `grep` o la búsqueda de un editor usan expresiones regulares para describir qué buscar sin enumerar cada variante. Por ejemplo, `(0+1)*001(0+1)*` (ejercicio 236 de la Lista 3) describe "contiene la subcadena 001 en cualquier parte"; `grep -E '001'` hace exactamente esa búsqueda, construyendo internamente un autómata equivalente al de ese patrón.
3. **Validación de datos de entrada.** Un formulario valida que un campo tenga la forma correcta antes de procesarlo: el validador de fecha de esta práctica (Ejercicio 4) usa `Dia/Mes/Anio + Anio-Mes-Dia` para aceptar `31/12/2026` o `2026-12-31` y rechazar `32/01/2027` o `00/01/2027`, sin ejecutar ninguna lógica de calendario, solo el autómata.
4. **Filtrado y extracción en registros (*logs*).** Un sistema de monitoreo filtra las líneas de una bitácora que coinciden con un patrón de error, por ejemplo `(0+1+2)(0+1+2+3+4+5+6+7+8+9)` para un código HTTP de la forma 4xx o 5xx al inicio de la línea (aquí simplificado a dígitos sin las palabras del texto alrededor); el mecanismo que decide "coincide o no" en cada línea es, de nuevo, un AFD que recorre la línea símbolo a símbolo.
5. **Automatización en sistemas operativos y DevOps.** Las reglas de reescritura de un servidor web (por ejemplo, un `.htaccess` o la configuración de nginx) usan expresiones regulares para decidir a qué recurso redirigir una URL, como `/articulos/D+` (D = 0+...+9) para reconocer rutas `/articulos/123` y extraer el identificador numérico; también se usan para filtrar nombres de archivo en una tarea programada, como `.*\.jff` para "todo archivo que termine en .jff" (la notación `.` y la extensión con escape ya son de la sintaxis de `re`, no de la notación del curso, lo que ilustra la diferencia de la sección 1.5).

## Referencias

Chomsky, N. (1956). Three models for the description of language. *IRE Transactions on Information Theory, 2*(3), 113-124. https://doi.org/10.1109/TIT.1956.1056813

Davis, J. C., Michael IV, L. G., Coghlan, C. A., Servant, F. y Lee, D. (2019). Why aren't regular expressions a lingua franca? An empirical study on the re-use and portability of regular expressions. En *Proceedings of the 2019 27th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering* (pp. 443-454). ACM. https://doi.org/10.1145/3338906.3338909

Hopcroft, J. E., Motwani, R. y Ullman, J. D. (2007). *Introducción a la teoría de autómatas, lenguajes y computación* (3.ª ed.). Pearson Addison-Wesley. Secciones 1.1, 3.1, 3.2.2, 3.2.3 y 3.4, y capítulo 9. Ficha completa en [bibliografía](../bibliografia.md).

Kleene, S. C. (1956). Representation of events in nerve nets and finite automata. En C. E. Shannon y J. McCarthy (Eds.), *Automata Studies* (pp. 3-41). Princeton University Press.

Sipser, M. (2012). *Introduction to the Theory of Computation* (3.ª ed.). Cengage. Secciones 1.1-1.3 (teorema 1.54 y lema 1.55) y 1.4 (lema de bombeo). Es la bibliografía básica del programa de Teoría de la Computación del IPN (programa ISC2020).

Thompson, K. (1968). Programming techniques: Regular expression search algorithm. *Communications of the ACM, 11*(6), 419-422. https://doi.org/10.1145/363347.363387
