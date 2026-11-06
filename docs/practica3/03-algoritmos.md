# Ejercicio 3. Documentación de los algoritmos

Este documento describe los algoritmos del Ejercicio 2. Para cada uno se da el problema que resuelve, el resultado teórico que lo respalda, el pseudocódigo con su correspondencia en el código, un ejemplo de la Lista 3 resuelto a mano y por el software, y una estimación del número de pasos.

**Notación de las estimaciones.** n = |Q| (estados), k = |Σ| (símbolos), t = número de transiciones del autómata (t ≤ n²·(k+1) si hay λ), m = |w| (longitud de la cadena). Un «paso» es una operación elemental sobre conjuntos de estados: agregar un estado, buscar una transición o comparar dos etiquetas.

**Dónde está el código.** Todo vive en [src/automata.py](../../src/automata.py) (núcleo, sin Flet) y en [src/controlador.py](../../src/controlador.py) (textos de la interfaz y validación por lotes). Las pruebas están en [tests/test_practica3.py](../../tests/test_practica3.py). La numeración de secciones del libro corresponde a la tercera edición de Hopcroft et al. (2007) y debe contrastarse con el ejemplar del curso (véase «Referencias» al final).

## Autómatas de los ejemplos

Los ejemplos salen de la Lista 3. Los archivos están en [automatas/practica3/casos-de-prueba/](../../automatas/practica3/casos-de-prueba/).

**Ejercicio 196 (AFN-λ).** Q = {A, B, C}, Σ = {0, 1}, estado inicial A, F = {C}.

| Estado | λ | 0 | 1 |
|---|---|---|---|
| →A | {B} | {A} | ∅ |
| B | ∅ | {A, B} | {C} |
| *C | ∅ | ∅ | ∅ |

**Ejercicio 156 (AFD de 5 estados).** Q = {A, B, C, D, E}, Σ = {0, 1}, inicial A, F = {E}.

| Estado | 0 | 1 |
|---|---|---|
| →A | B | C |
| B | C | E |
| C | D | C |
| D | C | E |
| *E | B | E |

---

## A1. λ-clausura y función de transición extendida

### Problema y resultado teórico

**Problema.** Dado un AFN-λ y un conjunto de estados S, hallar Cl(S): los estados a los que se llega desde S usando solo transiciones λ (incluidos los de S).

**Respaldo.** Hopcroft, Motwani y Ullman (2007), sección 2.5.3 (clausuras épsilon): Cl(q) es el conjunto de estados alcanzables desde q por arcos etiquetados con ε, y se define de forma inductiva (q ∈ Cl(q); si p ∈ Cl(q) y r ∈ δ(p, ε), entonces r ∈ Cl(q)). La sección 2.5.4 define la función extendida δ̂(q, wa) = Cl(δ(δ̂(q, w), a)), que es lo que usa la simulación.

### Pseudocódigo

```
Cl(S):
    visto ← S ;  pendientes ← lista(S)
    mientras pendientes no esté vacía:
        q ← sacar(pendientes)
        para cada r en δ(q, λ):
            si r ∉ visto: agregar r a visto y a pendientes
    devolver visto

δ̂(S, w):
    actual ← Cl(S)
    para cada símbolo a de w:
        actual ← Cl( ⋃ q∈actual δ(q, a) )
    devolver actual
```

| Pseudocódigo | Función |
|---|---|
| `Cl(S)` | `Automata.clausura(conjunto)` |
| `Cl(q)` para todo q (tabla) | `Automata.clausuras()` y `controlador.filas_de_clausuras(a)` |
| Clausura de un estado elegido, con las λ que se siguen | `controlador.clausura_de_estado(a, estado)` |
| ⋃ δ(q, a) sin clausura | `Automata.mover(conjunto, a)` |
| `δ̂(S, w)` | `Automata.delta_hat(conjunto, w)` |

La búsqueda marca los estados ya vistos, así que termina aunque haya ciclos de transiciones λ.

### Ejemplo a mano (Ejercicio 196)

- Cl(A): desde A hay A –λ→ B, y desde B no sale ninguna λ. Cl(A) = {A, B}.
- Cl(B) = {B} y Cl(C) = {C}, porque ni B ni C tienen transiciones λ.

### Ejemplo con el software

En la pestaña *Conversiones*, el botón «λ-clausuras» da la tabla y «λ-clausura de este estado» (con A en el campo) da:

```
Cl(A) = {A, B}, por las transiciones A –λ→ B.
Tabla: A → {A, B}   B → {B}   C → {C}
```

### Comparación

Coinciden las tres clausuras. La prueba `test_clausura_de_un_estado_elegido` y `test_clausuras_de_196_a_200` (en `tests/test_lista3.py`) comprueban las clausuras de los ejercicios 196 a 200.

### Estimación de pasos

Una clausura por búsqueda en profundidad visita cada estado una vez y cada transición λ una vez: **O(n + t_λ)**, con t_λ ≤ n² el número de transiciones λ. La tabla de las n clausuras cuesta **O(n·(n + t_λ))**. Calcular δ̂(S, w) cuesta **O(m·(n + t))**: por símbolo se recorre `mover` (a lo más t transiciones) y una clausura.

---

## A2. Simulación directa de un AFN-λ

### Problema y resultado teórico

**Problema.** Decidir si un AFN-λ acepta w, sin convertirlo, mostrando en cada paso los estados activos antes y después de aplicar la λ-clausura.

**Respaldo.** Hopcroft, Motwani y Ullman (2007), sección 2.5.4: w se acepta si δ̂(q₀, w) ∩ F ≠ ∅. Calcular δ̂ símbolo por símbolo es seguir todos los caminos a la vez; la sección 2.3.2 hace lo mismo para un AFN sin λ.

### Pseudocódigo

```
simular(w):
    S ← Cl({q0})
    registrar paso 0: antes = {q0}, después = S
    para cada símbolo a de w (i = 1, 2, ...):
        antes ← ⋃ q∈S δ(q, a)          # δ aplicada, sin clausura
        S     ← Cl(antes)              # clausura
        registrar paso i: antes, después = S, y las transiciones usadas
        si S = ∅: terminar (el autómata se bloqueó)
    aceptada ← S ∩ F ≠ ∅
```

| Pseudocódigo | Función |
|---|---|
| `simular(w)` | `Automata.simular(w)`, que devuelve un `Recorrido` de `Paso` |
| conjunto «antes» de la clausura | campo `Paso.antes` |
| conjunto «después» de la clausura | campo `Paso.conjunto` |
| veredicto sin guardar el recorrido | `Automata.acepta(w)` |
| texto de cada paso en pantalla | `controlador.descripcion_de_paso(a, recorrido, k)` y `Recorrido.texto(orden)` |
| enumerar caminos individuales | `Automata.caminos(w)` |

La simulación directa no depende de `a_afd()`: no construye ningún AFD.

### Ejemplo a mano (Ejercicio 196, w = 001)

| Paso | Símbolo | Antes de Cl | Después de Cl |
|---|---|---|---|
| 0 | — | {A} | Cl({A}) = {A, B} |
| 1 | 0 | δ(A,0) ∪ δ(B,0) = {A} ∪ {A, B} = {A, B} | {A, B} |
| 2 | 0 | {A, B} | {A, B} |
| 3 | 1 | δ(A,1) ∪ δ(B,1) = ∅ ∪ {C} = {C} | {C} |

C ∈ F, así que **001 se acepta**. Con w = 00 el conjunto final es {A, B}, que no contiene a C: **00 se rechaza**.

### Ejemplo con el software

```
Cadena: 001 (3 símbolos)
Inicio: λ-clausura del estado inicial = {A, B}   [A –λ→ B]
Paso 1, lee «0»: ...   →   antes de la λ-clausura {A, B}, después {A, B}
Paso 2, lee «0»: ...   →   antes de la λ-clausura {A, B}, después {A, B}
Paso 3, lee «1»: B –1→ C   →   antes de la λ-clausura {C}, después {C}
ACEPTADA: el conjunto final contiene el estado de aceptación C.
```

Para 00 el programa responde RECHAZADA.

### Comparación

Los conjuntos de cada paso, antes y después de la clausura, y los dos veredictos coinciden. Las pruebas `test_cada_paso_guarda_los_estados_antes_y_despues_de_la_clausura` y `test_la_simulacion_directa_coincide_con_la_del_afd_equivalente` lo comprueban para los ejercicios 196 a 200.

### Estimación de pasos

Por cada símbolo se calcula `mover` (a lo más t transiciones) y una clausura (O(n + t_λ)), y el conjunto activo nunca pasa de n estados: **O(m·(n + t))** en tiempo y **O(n)** en espacio, sin contar el recorrido guardado (que ocupa O(m·n)). Convertir antes a AFD costaría hasta 2ⁿ estados (véase A4), aunque después cada símbolo se procesaría en un solo paso.

---

## A3. Eliminación de transiciones λ

### Problema y resultado teórico

**Problema.** Transformar un AFN-λ en un AFN sin transiciones λ que reconozca el mismo lenguaje, mostrando las transiciones que se añaden y los estados que pasan a ser de aceptación.

**Respaldo.** Hopcroft, Motwani y Ullman (2007), sección 2.5.5 (eliminación de transiciones ε) y el teorema 2.22 de esa sección: δ'(q, a) = Cl(δ(Cl({q}), a)) y F' = {q : Cl({q}) ∩ F ≠ ∅}. El AFN resultante tiene los mismos estados que el original.

### Pseudocódigo

```
quitar_lambda(N):
    para cada estado q de N:
        C ← Cl({q})
        si C ∩ F ≠ ∅: marcar q como de aceptación en N'
        para cada símbolo a:
            para cada r en Cl( ⋃ p∈C δ(p, a) ):
                agregar la transición q –a→ r a N'
    añadidas  ← transiciones de N' que no están en N
    quitadas  ← transiciones λ de N
    nuevas_F  ← estados de F' que no están en F
```

| Pseudocódigo | Función |
|---|---|
| `quitar_lambda(N)` | `Automata.quitar_lambda()` |
| `añadidas`, `quitadas`, `nuevas_F` | `Automata.quitar_lambda_detalle()` (devuelve `ResultadoSinLambda`) |
| texto explicado, línea por línea | `controlador.lineas_de_quitar_lambda(a, resultado)` |

### Ejemplo a mano (Ejercicio 196)

| q | Cl(q) | a = 0: Cl(δ(Cl(q), 0)) | a = 1: Cl(δ(Cl(q), 1)) | ¿Cl(q) ∩ F ≠ ∅? |
|---|---|---|---|---|
| A | {A, B} | δ(A,0) ∪ δ(B,0) = {A, B} | δ(A,1) ∪ δ(B,1) = {C} | no |
| B | {B} | {A, B} | {C} | no |
| C | {C} | ∅ | ∅ | sí, pero C ya está en F |

El AFN resultante tiene las transiciones A–0→A, A–0→B, A–1→C, B–0→A, B–0→B y B–1→C. Las que no estaban en el original son **A–0→B y A–1→C**; desaparece **A–λ→B**; ningún estado nuevo pasa a ser de aceptación.

### Ejemplo con el software

```
Cl(A) = {A, B}   Cl(B) = {B}   Cl(C) = {C}
Transiciones λ que desaparecen (1): A –λ→ B
Transiciones que se añaden (2): A –0→ B, A –1→ C
Ningún estado pasa a ser de aceptación.
```

### Comparación

Las listas de transiciones añadidas y quitadas coinciden con el cálculo a mano. En el ejercicio 197, donde el software informa «A, B y C pasan a ser de aceptación» porque su clausura contiene a D, se obtiene lo mismo aplicando F' = {q : Cl(q) ∩ F ≠ ∅}; lo verifica `test_quitar_lambda_en_197_agrega_lo_que_se_alcanza_por_lambda`.

### Estimación de pasos

Para cada uno de los n estados y cada uno de los k símbolos se hace una clausura, un `mover` y otra clausura: **O(n·k·(n + t))**, que con t ≤ n²·(k+1) queda acotado por **O(n³·k²)**. El AFN resultante tiene a lo más n²·k transiciones.

---

## A4. Construcción de subconjuntos (AFN → AFD)

### Problema y resultado teórico

**Problema.** Transformar un AFN en un AFD equivalente construyendo solo los subconjuntos alcanzables desde el inicial, mostrando la tabla conforme se genera e indicando qué subconjuntos son de aceptación y por qué.

**Respaldo.** Hopcroft, Motwani y Ullman (2007), sección 2.3.5 (equivalencia entre AFD y AFN) y el teorema 2.11: δ_D(S, a) = ⋃ p∈S δ_N(p, a), con F_D = {S : S ∩ F_N ≠ ∅}. La sección 2.3.5 también explica la «evaluación perezosa» de los subconjuntos, que es construir solo los alcanzables. Para un AFN-λ se aplica con Cl, según la sección 2.5.5.

### Pseudocódigo

```
subconjuntos(N):
    inicio ← Cl({q0})
    nombres ← { inicio }  ;  cola ← [inicio]
    mientras cola no esté vacía:
        S ← sacar el primero de cola
        para cada símbolo a:
            movido ← ⋃ p∈S δ(p, a)
            T ← Cl(movido)
            registrar el renglón  (S, a, movido, T)
            si T ≠ ∅ (o si se pide el AFD completo):
                si T es un subconjunto nuevo: agregar T a nombres y a cola
                agregar la transición S –a→ T
    F_D ← { S : S ∩ F ≠ ∅ }
```

| Pseudocódigo | Función |
|---|---|
| `subconjuntos(N)` | `Automata.a_afd(completo=False)` (devuelve `Conversion`) |
| renglones de la tabla, en el orden en que se generan | `Automata.pasos_subconjuntos(completo)` (devuelve `PasoSubconjunto`) |
| filas para la tabla en pantalla | `controlador.filas_de_pasos_de_subconjuntos(pasos)` |
| razón de que un subconjunto sea de aceptación | `Automata.razon_de_aceptacion(S)` y `controlador.lineas_de_aceptacion(a, conversion)` |
| incluir ∅ como estado trampa | parámetro `completo=True` |

La interfaz muestra la tabla renglón por renglón con «Siguiente renglón». Se rechaza una conversión de más de `LIMITE_ESTADOS_AFD` estados.

### Ejemplo a mano (AFN sin λ del ejercicio 196)

Se parte del AFN que dejó A3. Como no tiene λ, Cl({A}) = {A}.

| Subconjunto S | a | ⋃ δ(p, a) | Destino | ¿Nuevo? |
|---|---|---|---|---|
| {A} (inicial) | 0 | {A, B} | {A, B} | sí |
| {A} | 1 | {C} | {C} | sí |
| {A, B} | 0 | {A} ∪ {A, B} = {A, B} | {A, B} | no |
| {A, B} | 1 | ∅ ∪ {C} = {C} | {C} | no |
| {C} | 0 | ∅ | sin transición | — |
| {C} | 1 | ∅ | sin transición | — |

Estados del AFD: {A}, {A, B} y {C}, de un máximo posible de 2³ = 8. Aceptación: {C}, porque contiene a C ∈ F; {A} y {A, B} no la tienen porque ni A ni B están en F.

### Ejemplo con el software

```
{A}   0 {A, B} {A, B} {A,B}  nuevo=sí
{A}   1 {C}    {C}    {C}    nuevo=sí
{A,B} 0 {A, B} {A, B} {A,B}  nuevo=no
{A,B} 1 {C}    {C}    {C}    nuevo=no
{C}   0 ∅      ∅      (sin transición)
{C}   1 ∅      ∅      (sin transición)
{C} es de aceptación porque contiene C, que es de aceptación en el original.
{A} y {A, B} no son de aceptación: ninguno de sus estados lo es en el original.
```

### Comparación

Coinciden los tres subconjuntos, la tabla y los estados de aceptación. Observación adicional: si se aplica `a_afd()` directamente al AFN-λ original (sin pasar por A3), el estado inicial es Cl({A}) = {A, B} y el AFD resultante tiene solo dos estados, {A, B} y {C}. La prueba `test_la_tabla_paso_a_paso_reproduce_el_afd` verifica los 19 casos de la práctica.

### Estimación de pasos

Hay a lo más 2ⁿ subconjuntos y por cada uno se calculan k destinos, cada uno con un `mover` y una clausura: **O(2ⁿ·k·(n + t))** en el peor caso, con una tabla de a lo más 2ⁿ·k renglones. El peor caso se alcanza de verdad (por ejemplo, «el n-ésimo símbolo desde el final es 1»). En los ejercicios de la Lista 3 el AFD resulta de tamaño comparable al AFN, como muestra la tabla de `herramientas/medir_costos.py`.

---

## A5. Eliminación de estados inaccesibles y minimización de un AFD

### Problema y resultado teórico

**Problema.** Quitar los estados inaccesibles y obtener el AFD con el menor número de estados que reconoce el mismo lenguaje, mostrando la partición en cada ronda.

**Respaldo.** Hopcroft, Motwani y Ullman (2007), sección 4.4 (equivalencia y minimización de autómatas): la sección 4.4.1 define estados equivalentes y el algoritmo de rellenado de tabla, y la 4.4.3 prueba que el AFD que resulta de fundir los estados equivalentes, después de quitar los inaccesibles, es el mínimo y es único salvo el nombre de los estados. El software usa el refinamiento de particiones (método de Moore), que obtiene las mismas clases de equivalencia que la tabla de pares distinguibles.

### Pseudocódigo

```
minimizar(D):
    D ← quitar_inaccesibles(D)             # búsqueda desde q0 por cualquier transición
    D ← completar(D)                       # estado trampa si el AFD es parcial
    P0 ← { F , Q \ F }                     # separa aceptación y no aceptación
    repetir:
        para cada estado q: firma(q) ← ( clase(q), clase(δ(q,a1)), ..., clase(δ(q,ak)) )
        P' ← agrupar los estados con la misma firma
        si |P'| = |P|: terminar
        P ← P'  ;  registrar la partición
    cada clase de P es un estado del AFD mínimo
    descartar la clase del estado trampa
```

| Pseudocódigo | Función |
|---|---|
| `quitar_inaccesibles(D)` | `Automata.accesibles()` y `Automata.quitar_inaccesibles()` |
| `completar(D)` | `Automata.completar()` |
| rondas de particiones | `Automata.particiones()` (devuelve `ResultadoParticion`) y `controlador.lineas_de_particiones(r)` |
| `minimizar(D)` | `Automata.minimizar()` |

### Ejemplo a mano (Ejercicio 156)

Todos los estados son accesibles. Partición inicial: P₀ = {A, B, C, D}, {E}.

| Estado | clase(δ(q,0)) | clase(δ(q,1)) |
|---|---|---|
| A | B → clase 0 | C → clase 0 |
| B | C → clase 0 | E → clase 1 |
| C | D → clase 0 | C → clase 0 |
| D | C → clase 0 | E → clase 1 |

A y C tienen la misma firma (0, 0); B y D, la firma (0, 1). Entonces P₁ = {A, C}, {B, D}, {E}. En la ronda siguiente: A–0→B y C–0→D (ambos en {B, D}); A–1→C y C–1→C (ambos en {A, C}); B y D van a {A, C} con 0 y a {E} con 1. No hay cambios, así que P₁ es la partición final. El AFD mínimo tiene **3 estados**: {A, C}, {B, D} y {E}.

### Ejemplo con el software

```
Partición 0: {A, B, C, D}  {E}
Partición 1: {A, C}  {B, D}  {E}
AFD mínimo: 5 estados → 3
Estados: {A,C}, {B,D}, E      inicial: {A,C}      aceptación: E
{A,C} –0→ {B,D}   {A,C} –1→ {A,C}   {B,D} –0→ {A,C}   {B,D} –1→ E   E –0→ {B,D}   E –1→ E
```

### Comparación

Las particiones y el AFD mínimo coinciden con el cálculo a mano (y con `test_en_156_los_estados_equivalentes_son_a_c_y_b_d` de la Práctica 2). La prueba `test_el_minimo_no_tiene_mas_estados_que_el_afd_del_que_procede` verifica la condición del apartado 2.6 en los 19 casos.

### Estimación de pasos

Quitar inaccesibles es una búsqueda: O(n·k). Completar agrega a lo más un estado y n·k transiciones. Cada ronda de refinamiento calcula n firmas de k+1 componentes: O(n·k). Hay a lo más n − 1 rondas, porque cada una aumenta el número de clases: **O(n²·k)** en el peor caso. El algoritmo de Hopcroft mejoraría esto a O(n·k·log n); no se implementó. El método de la tabla de pares examina O(n²) pares y repite hasta estabilizarse, también O(n²·k) por ronda.

---

## A6. Equivalencia de dos AFD por sus AFD mínimos

### Problema y resultado teórico

**Problema.** Decidir si dos AFD reconocen el mismo lenguaje: lo hacen si sus autómatas mínimos coinciden salvo el nombre de los estados.

**Respaldo.** Hopcroft, Motwani y Ullman (2007), sección 4.4.3: el AFD mínimo de un lenguaje regular es único salvo isomorfismo (cambio de nombre de los estados). La sección 4.4.2 da otro método, unir los dos autómatas y comprobar si los estados iniciales son equivalentes. El software no implementa ese método tal cual, sino un decisor análogo: `lenguajes_iguales` recorre a la vez los conjuntos de estados activos de los dos autómatas hasta hallar una cadena que uno acepte y el otro no. Se usa en las pruebas como segundo decisor.

### Pseudocódigo

```
equivalentes(D1, D2):
    M1 ← minimizar(D1) ;  M2 ← minimizar(D2)
    correspondencia ← { q0(M1) ↦ q0(M2) } ;  pendientes ← [ q0(M1) ]
    mientras pendientes no esté vacía:
        p ← sacar(pendientes) ;  q ← correspondencia[p]
        si (p ∈ F1) ≠ (q ∈ F2): devolver NO
        para cada símbolo a:
            si solo uno de δ1(p,a), δ2(q,a) existe: devolver NO
            si existen: (r, s) ← (δ1(p,a), δ2(q,a))
                si r ya tiene imagen distinta de s, o s ya tiene preimagen distinta de r: devolver NO
                si r es nuevo: correspondencia[r] ← s ;  agregar r a pendientes
    devolver SÍ, con la correspondencia
```

| Pseudocódigo | Función |
|---|---|
| `equivalentes(D1, D2)` | `automata.comparar_por_minimo(a, b)` (devuelve `ResultadoEquivalencia`) |
| comparación de dos AFD ya mínimos | `automata.isomorfismo(a, b)` |
| texto en pantalla | `controlador.lineas_de_equivalencia(resultado)` |
| decisor alterno por producto | `automata.lenguajes_iguales(a, b)` y `cadena_distintiva(a, b)` |

### Ejemplo a mano

**Equivalentes.** El AFD del ejercicio 156 y su mínimo (A5). El mínimo de este último es él mismo (3 estados). Los mínimos de ambos coinciden con la correspondencia {A,C} ↦ {A,C}, {B,D} ↦ {B,D}, E ↦ E: mismos inicial, misma aceptación y mismas transiciones. **Son equivalentes.**

**No equivalentes.** Ejercicio 156 contra ejercicio 157 (6 estados). El mínimo del 156 tiene 3 estados. En el 157 la partición P₀ = {A, B, C, D, E}, {F} se refina en P₁ = {A}, {B, C, D}, {E}, {F}, y el mínimo tiene **4 estados**. Con 3 y 4 estados no pueden ser isomorfos: **no son equivalentes**. (Un testigo: 1 lo acepta el 157, pero el 156 no.)

### Ejemplo con el software

```
AFD mínimo de A: 3 estados. AFD mínimo de B: 3 estados.
SON EQUIVALENTES. Los AFD mínimos tienen 3 estados y coinciden salvo el nombre.
Correspondencia de estados (A → B): {A,C} → {A,C}, {B,D} → {B,D}, E → E

AFD mínimo de A: 3 estados. AFD mínimo de B: 4 estados.
NO SON EQUIVALENTES. Los AFD mínimos tienen 3 y 4 estados: no pueden coincidir.
```

### Comparación

Los dos veredictos y los tamaños de los mínimos coinciden. `test_dos_afd_de_distinto_lenguaje_no_son_equivalentes` verifica que la decisión por mínimos coincide con el decisor exacto `lenguajes_iguales` para todos los pares de los ejercicios 151 a 157 con el mismo alfabeto.

### Estimación de pasos

Dos minimizaciones, O(n²·k) cada una (A5), y un isomorfismo que recorre cada estado alcanzable una vez y examina k símbolos: **O(n·k)**. El total lo domina la minimización: **O(n²·k)**. El decisor por producto recorre hasta n₁·n₂ pares de estados: O(n₁·n₂·k).

---

## A7. Validación de varias cadenas

### Problema

Cargar un archivo de texto con una cadena por línea, validarlas todas con el autómata actual y guardar un informe con el resultado de cada una.

### Pseudocódigo

```
validar_lote(A, archivo):
    cadenas ← leer las líneas no vacías del archivo (la línea «λ» es la cadena vacía)
    para cada w en cadenas:
        intentar: resultado ← simular(A, w) → ACEPTADA o RECHAZADA
        si falla por un símbolo fuera del alfabeto: resultado ← ERROR (y seguir con la siguiente)
    escribir un informe: una línea por cadena y un resumen
```

| Pseudocódigo | Función |
|---|---|
| leer las cadenas | `controlador.leer_cadenas(texto)` y `controlador.cargar_cadenas(ruta)` |
| validar | `controlador.validar_lote(a, cadenas)` |
| informe | `controlador.informe_de_lote(a, resultados, origen)` y `controlador.guardar_informe(...)` |

El informe se guarda en `salidas/` como `.txt`. Las líneas en blanco se ignoran y el archivo se lee como UTF-8 con o sin BOM.

### Estimación de pasos

**O(Σ|wᵢ|·(n + t))** para N cadenas, es decir, N veces el costo de A2.

---

## Longitud de las cadenas en las pruebas del apartado 2.6

Las pruebas comparan el autómata original, el AFN sin λ, el AFD de subconjuntos y el AFD mínimo sobre **todas las cadenas del alfabeto hasta una longitud N** que se calcula para cada caso: N = max(p + q − 2, 6), con p y q los estados del AFD de subconjuntos y del mínimo, ambos completados.

**Justificación.** Por el teorema de Moore (ligado a la sección 4.4.1 del libro), si dos AFD completos de p y q estados aceptan lenguajes distintos, existe una cadena de longitud a lo más p + q − 2 que uno acepta y el otro no. Con N ≥ p + q − 2 la comparación entre el AFD y su mínimo es, por lo tanto, **exhaustiva**: no queda ningún caso sin probar. Los otros dos autómatas (original y AFN sin λ) se prueban hasta la misma longitud como comprobación empírica, y además todas las versiones se comparan con el decisor exacto `lenguajes_iguales`, que no depende de ninguna longitud. El piso de 6 evita que un caso muy pequeño (por ejemplo, el 197, cuya cota p + q − 2 es 1) se pruebe con casi ninguna cadena. El mayor N de los casos es 15, en el ejercicio 154 (2¹⁶ − 1 cadenas).

## Referencias

Hopcroft, J. E., Motwani, R. y Ullman, J. D. (2007). *Introducción a la teoría de autómatas, lenguajes y computación* (3.ª ed.). Pearson Addison-Wesley. Secciones citadas: 2.3.5 y teorema 2.11 (subconjuntos), 2.5.3 a 2.5.5 y teorema 2.22 (λ-clausura y eliminación de λ), 4.4.1 a 4.4.3 (equivalencia y minimización) y 3.2.1 y 3.2.2 (de AFD a expresión regular, para el Ejercicio 1). Ficha completa en [bibliografía](../bibliografia.md).
