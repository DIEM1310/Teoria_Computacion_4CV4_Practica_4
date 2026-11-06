# Ejercicio 4. Aplicaciones: validadores

`src/validadores.py` implementa tres validadores (de los cinco que ofrece el enunciado: correo electrónico, teléfono, URL, fecha o contraseña). Cada uno se define **una sola vez**, como árbol de expresión (`expresiones.ER`), y de ahí salen, sin poder desincronizarse entre sí:

- el texto en la notación del curso (`Validador.notacion_completa`, con `expresiones.a_texto`);
- la traducción a la sintaxis de `re` de Python (`Validador.python_re`, con `expresiones.a_python`);
- el autómata, por el Ejercicio 2 completo (`validadores.construir_automata`: Thompson, quitar λ, subconjuntos, minimizar).

Por eso no hay dos copias de cada expresión que puedan contradecirse: el automáta y el patrón de `re` que se comparan en la prueba de congruencia (sección 4.4) nacen del mismo árbol.

## 4.1 Fecha (DD/MM/AAAA o AAAA-MM-DD)

**Notación del curso** (abreviada): `Dia/Mes/Anio + Anio-Mes-Dia`, con las clases D = 0+1+...+9 (un dígito), Dnz = 1+2+...+9 (sin el 0), Mes = (0 Dnz) + (1 (0+1+2)) (01 a 12), Dia = (0 Dnz) + ((1+2) D) + (3 (0+1)) (01 a 31) y Anio = D D D D (cuatro dígitos). Alfabeto: `{0,...,9, /, -}` (12 símbolos).

**Traducción a `re`** (generada por `a_python`, no escrita a mano): equivale a
`(?:(?:0[1-9]|[12][0-9]|3[01])/(?:0[1-9]|1[0-2])/[0-9]{4})|(?:[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01]))`
(con grupos no-capturantes y clases expandidas símbolo por símbolo, no con `[0-9]`; aquí se muestra abreviado por claridad).

**Estados.** AFD antes de minimizar (subconjuntos): 160. AFD mínimo: **26**.

**Qué queda fuera.** No comprueba que el mes tenga esa cantidad de días (acepta `31/02/2027` y `30/02/2024`, que no existen) ni los años bisiestos para el 29 de febrero, ni limita el año a un rango razonable (acepta `00/01/0000`). Quedan fuera los demás separadores (punto, espacio), el mes en letras (`5 de enero de 2027`) y el año con dos dígitos. Validar los días de cada mes por separado sí es regular, pero exige un caso por mes (doce ramas más); se dejó fuera para que la expresión quedara legible. Una expresión regular para fechas, como para correos o URL, siempre es una aproximación: aquí se consultó el formato de fecha de la Unión Europea/ISO 8601 para los dos órdenes de campos (día-mes-año y año-mes-día), sin más reglas de calendario.

## 4.2 Teléfono nacional (10 dígitos, seguidos o con guiones 2-4-4)

**Notación del curso**: `D¹⁰ + (D D guion D⁴ guion D⁴)` (D¹⁰ abrevia D concatenado diez veces: el curso no tiene notación de repetición, así que la expresión completa repite D explícitamente). Alfabeto: `{0,...,9, -}` (11 símbolos) — **no el espacio**: `expresiones.parsear` quita los espacios antes de leer la expresión (son solo separadores visuales, como en `a + b`), así que el espacio no puede ser símbolo de ningún alfabeto que use esta notación; por eso el separador elegido es el guion y no el espacio.

**Estados.** AFD antes de minimizar: 184. AFD mínimo: **17**.

**Qué queda fuera.** No comprueba que el código de dos dígitos sea una clave lada real ni rechaza los números que empiezan en `00`. No admite espacios (`55 1234 5678`, por la razón de arriba) ni paréntesis ni el prefijo `+52`; se dejaron fuera para que el alfabeto se mantuviera pequeño. Se consultó el formato de diez dígitos del plan de numeración de México (sin el código de país), sin validar contra una lista real de claves lada.

## 4.3 Contraseña (criterio propio)

El enunciado permite definir el criterio. Este valida: **longitud exactamente 8, el primer carácter es una letra minúscula y el último es un dígito**; los seis intermedios son letra o dígito. Notación: `L (L+D)⁶ D`, con L = a+b+...+z y D = 0+...+9 (alfabeto de 36 símbolos).

**Estados.** AFD antes de minimizar: 254. AFD mínimo: **10** — uno por posición (0 a 8) más un estado trampa, porque en cada posición todos los símbolos de la clase que corresponde llevan al mismo estado siguiente; es el AFD más pequeño de los tres porque el lenguaje, al tener longitud fija, es esencialmente "una posición a la vez" sin ninguna elección real que recordar.

**Qué queda fuera.** Es un criterio propio, no un estándar: longitud fija (no un rango), solo minúsculas y dígitos (sin mayúsculas ni símbolos como `#` o `_`), y exige que el primer carácter sea una letra y el último un dígito, pero no exige más de un dígito ni prohíbe que los seis caracteres intermedios sean todos dígitos. Se simplificó así para que el alfabeto y la expresión quedaran manejables; una política con mayúsculas, símbolos y longitud variable también es regular (longitud variable: con `L(L+D)*D`, por ejemplo), pero el autómata resultante sería mucho más grande y la expresión mucho más larga de leer.

## 4.4 Congruencia con `re.fullmatch`: generación y resultado

`validadores.generar_casos(v, cantidad, semilla)` arma al menos `cantidad` cadenas distintas (se usan 500, el mínimo que pide el enunciado) en dos mitades:

1. **La mitad válida**, recorriendo el árbol de la expresión al azar (`_generar`): en cada unión se elige una parte al azar, en cada estrella se repite entre 0 y 3 veces (también al azar) y en cada concatenación se generan todas las partes y se concatenan. Es un generador genérico —sirve para cualquier `ER`, no solo para estos tres validadores— y siempre produce una cadena que sí pertenece al lenguaje.
2. **La otra mitad**, corrompiendo una cadena válida (`_corromper`: quita, inserta, cambia o repite un carácter al azar, o trunca la cadena) o generando una cadena por completo al azar sobre el alfabeto, de longitud entre 0 y 16. La mayoría de estas quedan fuera del lenguaje, pero no se *fuerza* que lo estén: lo que importa no es si son válidas, sino que el autómata y `re.fullmatch` **coincidan** en cada una.

Con la misma semilla (`"practica4"` por omisión) el conjunto es siempre el mismo (`generar_casos` usa `random.Random(semilla)`), lo que hace la prueba reproducible. `tests/test_validadores.py::test_congruencia_con_re_fullmatch_sobre_quinientas_cadenas` construye el AFD mínimo de cada validador una sola vez (no en cada cadena), genera 500 cadenas y compara `automata.acepta(w)` contra `re.fullmatch(validador.python_re, w) is not None` para cada una:

| Validador | Cadenas generadas | Discrepancias |
|---|---|---|
| Fecha | ≥ 500 | 0 |
| Teléfono | ≥ 500 | 0 |
| Contraseña | ≥ 500 | 0 |

La prueba corre en la integración continua con Python 3.11, 3.12 y 3.13 (`.github/workflows/pruebas.yml`, sin cambios desde la Práctica 2), igual que el resto de la suite.
