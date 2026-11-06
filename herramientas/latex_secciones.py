"""Secciones del documento de LaTeX de la 3.ª Lista (enunciados, procedimientos y respuestas)."""

import itertools
import shutil

import latex_base as B
from latex_base import (E, F, K, RAIZ, X, conj, datos, er_tex, figura, figuras_en_pares, mono, por_nombre, pruebas, tabla_simple,
                        tabla_tex, traza_tex, tx)

ENUN_LISTA2 = {
    "97": r"Las palabras de $\Sigma_1=\{0,1,2\}$ cuya longitud es un m\'ultiplo de 3.",
    "99": r"Las palabras de $\Sigma_1$ que terminan con la cadena \texttt{001001}.",
    "102": r"Las palabras de $\Sigma_3=\{a,b\}$ que contienen la cadena \texttt{abbbab}.",
    "103": r"Las palabras de $\Sigma_3$ que contienen la cadena \texttt{aabbba}.",
    "106": r"Las palabras de $\Sigma_1$ que incluyen la subcadena \texttt{1101001}.",
    "107": r"Las palabras de $\Sigma_1$ que incluyen al menos una vez la subcadena \texttt{0101} y al menos una vez \texttt{021}.",
    "109": r"Las palabras de $\Sigma_2=\{a,b,c,0,1\}$ que incluyen \texttt{abbcb} y \texttt{cbaabb}, asumiendo que s\'i se pueden traslapar.",
    "111": r"Las palabras de $\Sigma_1$ que contienen exactamente tres veces la subcadena \texttt{01002}.",
    "112": r"Las palabras de $\Sigma_1$ que contienen dos veces la subcadena \texttt{010}, sin traslape (se interpreta como exactamente dos).",
    "113": r"Las palabras de $\Sigma_1$ que contienen dos veces la subcadena \texttt{010}, con traslape (se interpreta como exactamente dos).",
    "118": r"$L=\{w\in\Sigma_3 : w=axabya,\ x,y\in\Sigma_3^{*}\}$.",
    "120": r"Las palabras de $\Sigma_1$ tales que el primer car\'acter y el \'ultimo son distintos.",
    "121": r"Las palabras de $\Sigma_1$ de longitud $3n$ tales que, divididas en $n$ bloques de longitud 3, cada bloque tiene al menos un 0.",
    "122": r"Las palabras de $\Sigma_1$ tales que cualquier cadena de tres s\'imbolos consecutivos tiene un 0.",
    "123": r"Las palabras de $\Sigma_3$ de la forma $wxw$, con $w\in\Sigma_3^{2}$ y $x\in\Sigma_3^{*}$.",
}

PISTA = {
    "99": r"se adivina en qu\'e posici\'on empieza el sufijo \texttt{001001}; hasta ah\'i el estado inicial lee cualquier s\'imbolo",
    "102": r"se adivina d\'onde empieza \texttt{abbbab}; antes y despu\'es se lee cualquier s\'imbolo",
    "103": r"se adivina d\'onde empieza \texttt{aabbba}; antes y despu\'es se lee cualquier s\'imbolo",
    "106": r"se adivina d\'onde empieza \texttt{1101001}; antes y despu\'es se lee cualquier s\'imbolo",
    "118": r"se adivina d\'onde empieza \texttt{ab} y d\'onde est\'a la \texttt{a} final; $x$ e $y$ son lazos",
    "120": r"al leer el primer s\'imbolo se recuerda cu\'al fue; se adivina cu\'al es el \'ultimo y se comprueba que es otro",
    "123": r"se recuerda $w$ (4 posibilidades) y se adivina d\'onde empieza la segunda $w$; $x$ es un lazo",
}

NUEVOS_AFN = [("99", "Ej_099_afn_termina_en_001001"), ("102", "Ej_102_afn_contiene_abbbab"), ("103", "Ej_103_afn_contiene_aabbba"),
              ("106", "Ej_106_afn_contiene_1101001"), ("118", "Ej_118_afn_forma_axabya"),
              ("120", "Ej_120_afn_primer_y_ultimo_distintos"), ("123", "Ej_123_afn_forma_wxw")]

LENGUAJE_158_161 = {"158": r"$\{01\}$", "159": er_tex("1*01"), "160": er_tex("01(0+1)*"), "161": er_tex("(010)*(λ+01)")}

RAZONA_158_161 = {
    "158": r"Desde $q_1$ solo se avanza leyendo \texttt{0} y desde $q_2$ solo leyendo \texttt{1}; $q_3$ es el \'unico estado de aceptaci\'on y no "
           r"tiene transiciones. La \'unica cadena que llega a $q_3$ es \texttt{01}.",
    "159": r"$q_1$ tiene un lazo con \texttt{1}, as\'i que lee cualquier cantidad de unos; despu\'es \texttt{0} lleva a $q_2$ y \texttt{1} a $q_3$ "
           r"(aceptaci\'on, sin salidas). Por eso $L=1^{*}01$.",
    "160": r"Igual que en el 158 hasta llegar a $q_3$, pero $q_3$ tiene un lazo con \texttt{0} y \texttt{1}: tras \texttt{01} se acepta cualquier "
           r"continuaci\'on. Por eso $L=01(0+1)^{*}$.",
    "161": r"El camino $q_1\to q_2\to q_3$ lee \texttt{01}, y $q_3$ vuelve a $q_1$ con \texttt{0}: cada vuelta completa lee \texttt{010}. Como $q_1$ "
           r"(inicial) y $q_3$ son de aceptaci\'on, se acepta tras $n$ vueltas ($q_1$) o tras $n$ vueltas m\'as \texttt{01} ($q_3$): $L=(010)^{*}(\lambda+01)$.",
}

PREAMBULO = r"""% !TEX program = pdflatex
\documentclass[11pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[spanish,es-tabla]{babel}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,longtable,array}
\usepackage{float}
\usepackage{caption}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage[margin=2cm,top=2.4cm,headheight=15pt]{geometry}
\usepackage[hidelinks]{hyperref}
\captionsetup{font=small,labelfont=bf}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}
\setlist{nosep}
\newcommand{\figauto}[2]{%
  \ifdim #2pt>\linewidth
    \includegraphics[width=\linewidth]{#1}%
  \else
    \includegraphics[width=#2pt]{#1}%
  \fi}
\pagestyle{fancy}
\fancyhf{}
\lhead{\small @@NOMBRE@@}
\chead{\small Boleta @@BOLETA@@}
\rhead{\small Grupo @@GRUPO@@}
\cfoot{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\fancypagestyle{plain}{\fancyhf{}\lhead{\small @@NOMBRE@@}\chead{\small Boleta @@BOLETA@@}\rhead{\small Grupo @@GRUPO@@}\cfoot{\small\thepage}\renewcommand{\headrulewidth}{0.4pt}}
\hypersetup{pdftitle={Tercera lista de problemas y ejercicios}, pdfauthor={@@NOMBRE@@}}
\begin{document}
"""

PORTADA = r"""\begin{center}
{\large Instituto Polit\'ecnico Nacional\\ Escuela Superior de C\'omputo}\\[1.2cm]
{\Large\bfseries Teor\'ia de la Computaci\'on}\\[0.4cm]
{\Large 3.\textordfeminine\ Lista de problemas y ejercicios}\\[0.2cm]
{\large 2027/1}\\[1.0cm]
\begin{tabular}{rl}
\textbf{Alumno:} & @@NOMBRE@@\\
\textbf{Boleta:} & @@BOLETA@@\\
\textbf{Grupo:} & @@GRUPO@@\\
\textbf{Profesor:} & @@PROFESOR@@\\
\end{tabular}
\end{center}
\vspace{0.6cm}
Se resuelven los ejercicios con asterisco (los dem\'as son opcionales), m\'as los 196 a 200, que no llevan asterisco pero
sirven para la conversi\'on de AFND-$\lambda$ a AFD. Cada ejercicio incluye su enunciado, el procedimiento y la respuesta.

\textbf{Convenciones.} En las tablas, $\rightarrow$ marca el estado inicial y $*$ los estados de aceptaci\'on; $\emptyset$ es ninguna transici\'on.
En los diagramas, el estado inicial lleva una flecha sin origen y los de aceptaci\'on un doble c\'irculo.

\textbf{Figuras de ejecuci\'on.} Cada aut\'omata se prob\'o con cinco cadenas v\'alidas y cinco inv\'alidas de distinta longitud. La tabla da,
para cada cadena, el resultado y el recorrido (los estados activos tras leer cada s\'imbolo; en los no deterministas, adem\'as,
cu\'antos caminos de c\'omputo hay y cu\'antos aceptan). Las figuras muestran la ejecuci\'on de una cadena v\'alida y una inv\'alida con
el diagrama del simulador: \textcolor[RGB]{200,120,0}{en amarillo, los estados activos al terminar de leer la cadena} y
\textcolor[RGB]{216,67,21}{en rojo, las transiciones del \'ultimo paso}. Una cadena se acepta si al terminar queda activo alg\'un estado de aceptaci\'on.
Los aut\'omatas se simularon con un simulador propio, del que el anexo~\ref{anexo:capturas} muestra capturas.

\tableofcontents
\clearpage
"""


def mt(nombre):
    """Nombre de estado dentro de una fórmula."""
    return nombre.replace("{", r"\{").replace("}", r"\}").replace("∅", r"\emptyset ").replace("_", r"\_")


def miles(n):
    return f"{n:,}".replace(",", r"\,")


def consulta_tex(c):
    if c[0] == "delta_hat":
        return r"$\hat{\delta}(\{" + ",".join(c[1]) + r"\},\ \mathtt{" + c[2] + "})$"
    if c[0] == "clausura":
        return r"$\mathrm{Cl}(\{" + ",".join(c[1]) + r"\})$"
    return r"$\delta(" + c[1] + r",\mathtt{" + c[2] + "})$"


def pasos_de_subconjuntos(a, conv):
    """La construcción de subconjuntos como lista, con la notación del curso."""
    items = []
    for nombre, S in conv.subconjuntos.items():
        miembros = a._ordenar(S)
        for simbolo in a.alfabeto:
            partes = [conj(a, a.destinos(q, simbolo)) for q in miembros]
            union = a.clausura(a.mover(S, simbolo))
            izq = r"\delta'(" + mt(nombre) + r",\mathtt{" + simbolo + "})"
            medio = r"\cup ".join(r"\delta(" + mt(q) + r",\mathtt{" + simbolo + "})" for q in miembros)
            if len(miembros) == 1:
                items.append(r"\item $" + izq + "=" + medio + "$ $=$ " + conj(a, union))
            else:
                items.append(r"\item $" + izq + "=" + medio + "$ $=$ " + " $\\cup$ ".join(partes) + " $=$ " + conj(a, union))
    return "\n".join([r"\begin{itemize}[leftmargin=1.2em]"] + items + [r"\end{itemize}"])


# ---------------------------------------------------------------------------
# 151 a 157
# ---------------------------------------------------------------------------

def sec_simplificacion():
    L = [r"\section{Aut\'omatas finitos y simplificaci\'on (151--157)}", "",
         r"\textbf{Enunciado (151--155).} Hallar el diagrama de transiciones del aut\'omata definido en cada tabla y simplificarlo "
         r"eliminando los estados que no son accesibles. \textbf{(156--157).} Hallar la tabla de transiciones del aut\'omata que se muestra "
         r"y simplificarlo encontrando una partici\'on y/o eliminando los estados inaccesibles.", "",
         r"\textbf{M\'etodo.} Un estado es \emph{accesible} si existe una cadena que lo alcanza desde el inicial; se obtienen con un "
         r"recorrido a lo ancho. Para la partici\'on se parte de $\{$aceptaci\'on$\}$ y $\{$no aceptaci\'on$\}$ y en cada ronda se "
         r"separan los estados que, con alg\'un s\'imbolo, van a clases distintas; el proceso termina cuando la partici\'on ya no cambia, "
         r"y los estados de una misma clase son equivalentes y se fusionan."]
    for n in range(151, 158):
        orig = por_nombre(f"Ej_{n}_original")
        inaccesibles = [q for q in orig.estados if q not in orig.accesibles()]
        minimo = por_nombre(f"Ej_{n}_minimo")
        origen = "figura" if n >= 156 else "tabla"
        L += [rf"\subsection{{Ejercicio {n}}}", "", f"Aut\\'omata de la {origen} del enunciado ({datos(orig)}).", "",
              tabla_tex(orig), figura(orig, f"Ejercicio {n}: aut\\'omata del enunciado.")]
        L += [r"\textbf{Estados accesibles} (en el orden en que se descubren desde " + tx(orig.inicial) + "): "
              + ", ".join(tx(q) for q in orig.accesibles()) + ". ",
              (r"\textbf{Estados inaccesibles:} " + ", ".join(tx(q) for q in inaccesibles) + ".") if inaccesibles
              else "No hay estados inaccesibles: todos se alcanzan desde el inicial, as\\'i que quitarlos no cambia el aut\\'omata.", ""]
        if inaccesibles:
            sin = por_nombre(f"Ej_{n}_sin_inaccesibles")
            L += [r"\textbf{Aut\'omata sin los estados inaccesibles} (" + datos(sin) + "):", tabla_tex(sin),
                  figura(sin, f"Ejercicio {n}: sin los estados inaccesibles ({', '.join(tx(q) for q in inaccesibles)}).")]
        part = orig.particiones()
        L += [r"\textbf{Partici\'on.}", r"\begin{itemize}[leftmargin=1.2em]"]
        L += [r"\item " + tx(x) for x in K.lineas_de_particiones(part)] + [r"\end{itemize}"]
        equivalentes = [c for c in part.rondas[-1] if len(c) > 1]
        L += [("Estados equivalentes: " + "; ".join(r"$\{$" + ", ".join(tx(q) for q in c) + r"$\}$" for c in equivalentes) + ". ")
              if equivalentes else "No hay estados equivalentes: el aut\\'omata ya es m\\'inimo. ",
              f"El aut\\'omata simplificado tiene {len(minimo.estados)} estados (el original, {len(orig.estados)}).", "",
              r"\textbf{AFD m\'inimo:}", tabla_tex(minimo), figura(minimo, f"Ejercicio {n}: AFD m\\'inimo."),
              r"\textbf{Pruebas} (el original y el simplificado reconocen el mismo lenguaje):", pruebas(orig), ""]
    return L


def sec_afn_descritos():
    L = [r"\section{AFN descritos por su diagrama (158--161)}", "",
         r"\textbf{Enunciado.} Describir lo que hacen los aut\'omatas finitos no deterministas mostrados, con $\Sigma=\{0,1\}$. "
         r"En ninguno hay dos transiciones con el mismo s\'imbolo desde un estado: son deterministas (parciales); si falta una "
         r"transici\'on, la cadena se rechaza."]
    for n in range(158, 162):
        a = por_nombre(f"Ej_{n}_figura")
        L += [rf"\subsection{{Ejercicio {n}}}", "", r"\textbf{Lenguaje:} " + LENGUAJE_158_161[str(n)] + ".", "",
              r"\textbf{Razonamiento:} " + RAZONA_158_161[str(n)], "", tabla_tex(a),
              figura(a, f"Ejercicio {n}."), pruebas(a), ""]
    return L


# ---------------------------------------------------------------------------
# 162 a 190
# ---------------------------------------------------------------------------

def afd_lista2(numero):
    return F.leer_archivo(next((RAIZ / "automatas" / "lista2-afd").glob(f"Ej_{int(numero):03d}_*.jff")))


def sec_afn_lista2():
    L = [r"\section{AFN de los ejercicios de la 2.\textordfeminine\ Lista (162--188)}", "",
         r"\textbf{Enunciado.} Encontrar un aut\'omata finito no determinista para cada uno de los problemas 94--123 de la tarea 2 "
         r"(los obligatorios son los que tienen asterisco). Cuando sea posible, el diagrama del AFN debe ser m\'as simple que el del AFD. "
         r"El enunciado no dice qu\'e n\'umero corresponde a cada problema, por lo que se identifican por su n\'umero de la 2.\textordfeminine\ Lista.", "",
         r"\textbf{Criterio.} Se compara el n\'umero de estados y de transiciones del AFN con los del AFD ya entregado. Donde el AFN es m\'as simple "
         r"se da el AFN; donde no lo es, se reutiliza el AFD (todo AFD es un AFN) y se explica por qu\'e."]
    filas = []
    for numero, clave in NUEVOS_AFN:
        afn, afd = por_nombre(clave), afd_lista2(numero)
        filas.append([numero, f"{len(afn.estados)} / {len(afd.estados)}", f"{len(afn.transiciones())} / {len(afd.transiciones())}", "AFN nuevo"])
    for numero in E.AFD_COMO_AFN:
        filas.append([numero, "--", "--", "se reutiliza el AFD"])
    L += [tabla_simple(["Ejercicio", "Estados AFN / AFD", "Transiciones AFN / AFD", "Resultado"], sorted(filas, key=lambda f: int(f[0])), "cccl"), ""]
    for numero, clave in NUEVOS_AFN:
        a, afd = por_nombre(clave), afd_lista2(numero)
        L += [rf"\subsection{{Ejercicio {numero} de la 2.\textordfeminine\ Lista: AFN}}", "", r"\textbf{Enunciado:} " + ENUN_LISTA2[numero], "",
              r"\textbf{Idea de dise\~no:} " + PISTA[numero] + ".",
              f"El AFN tiene {len(a.estados)} estados y {len(a.transiciones())} transiciones; el AFD, {len(afd.estados)} y {len(afd.transiciones())}.", "",
              tabla_tex(a), figura(a, f"AFN del ejercicio {numero} de la 2.\\textordfeminine\\ Lista."), pruebas(a), ""]
    L += [r"\subsection{Ejercicios en los que se reutiliza el AFD}", "",
          "En estos ejercicios el AFN no mejora al AFD, por lo que el AFD (que ya es un AFN) es la respuesta:", ""]
    for numero, motivo in E.AFD_COMO_AFN.items():
        afd = afd_lista2(numero)
        L += [rf"\subsubsection*{{Ejercicio {numero}}}", r"\textbf{Enunciado:} " + ENUN_LISTA2[numero], "",
              r"\textbf{Por qu\'e no mejora:} " + tx(motivo) + f". ({datos(afd)}.)", "",
              figura(afd, f"Ejercicio {numero}: el AFD de la 2.\\textordfeminine\\ Lista, que es tambi\\'en su AFN."),
              pruebas(afd, con_figuras=len(afd.estados) <= 15), ""]
    L += [r"\subsubsection*{Ejercicio 116}", r"\textbf{Enunciado:} $L=\{w\in\Sigma_2 : w=a^{n}b^{m}c^{n+1},\ m,n\in\mathbb{N}\}$.", "",
          r"\textbf{No existe AFN (ni AFD).} El lenguaje no es regular. Si lo fuera, $L'=L\cap a^{*}c^{*}=\{a^{n}c^{n+1} : n\in\mathbb{N}\}$ "
          r"tambi\'en lo ser\'ia (los regulares se cierran bajo intersecci\'on). Pero para $n_1\neq n_2$ las cadenas $a^{n_1}$ y $a^{n_2}$ son "
          r"distinguibles por el sufijo $c^{n_1+1}$ ($a^{n_1}c^{n_1+1}\in L'$ y $a^{n_2}c^{n_1+1}\notin L'$), as\'i que por el teorema de "
          r"Myhill--Nerode hay infinitas clases de equivalencia y $L'$ no es regular. Reconocerlo exige comparar el n\'umero de $a$ con el de $c$, "
          r"y un aut\'omata finito no tiene memoria para contar sin l\'imite.", ""]
    return L


def ruta_tex(c):
    return tx(c.estados[0]) + "".join(r" $\xrightarrow{\texttt{" + tx(l if l else "λ") + "}}$ " + tx(h) for (_, l, h) in c.transiciones)


def sec_189_190():
    L = [r"\section{Aut\'omatas con dos patrones (189 y 190)}"]
    casos = [("189", "Ej_189_afn_00101_o_00110", "1001011",
              r"Encuentre un aut\'omata finito no determinista, con $\Sigma=\{0,1\}$, que identifique las palabras que contienen la cadena "
              r"\texttt{00101} o la cadena \texttt{00110}. Realice el diagrama de transiciones de la palabra \texttt{1001011}.",
              r"Los dos patrones comparten el prefijo \texttt{001}; despu\'es se bifurca en \texttt{01} o \texttt{10}. El estado inicial "
              r"tiene un lazo y adivina d\'onde empieza \texttt{001}."),
             ("190", "Ej_190_afn_11010_y_10100", "01101010100",
              r"Encuentre un aut\'omata finito no determinista, con $\Sigma=\{0,1\}$, que identifique las palabras que contienen la cadena "
              r"\texttt{11010} y la cadena \texttt{10100}. Realice el diagrama de transiciones de la palabra \texttt{01101010100}.",
              r"Se adivina cu\'al patr\'on aparece primero (dos ramas desde el estado inicial). Los patrones se traslapan: \texttt{10100} puede empezar "
              r"en el segundo s\'imbolo de \texttt{11010} (comparten \texttt{1010}) o en el cuarto (comparten \texttt{10}); eso se resuelve con dos "
              r"transiciones desde la rama de \texttt{11010} hacia la cadena de \texttt{10100}. Ignorar el traslape dar\'ia un AFN incorrecto.")]
    for num, clave, w, enun, idea in casos:
        a = por_nombre(clave)
        r = a.simular(w)
        c = a.caminos(w, limite=2000)
        aceptan = sum(x.aceptado for x in c.caminos)
        L += [rf"\subsection{{Ejercicio {num}}}", "", r"\textbf{Enunciado:} " + enun, "", r"\textbf{Idea de dise\~no:} " + idea,
              f"({datos(a)}.)", "", tabla_tex(a), figura(a, f"AFN del ejercicio {num}."),
              rf"\textbf{{Diagrama de transiciones de la palabra}} {mono(w)}. Hay {len(c.caminos)} caminos de c\'omputo y {aceptan} aceptan; "
              r"el \'arbol de ejecuci\'on tiene una rama por cada camino:", r"\begin{enumerate}[leftmargin=1.6em]"]
        for x in c.caminos[:30]:
            L.append(r"\item " + ruta_tex(x) + (r" \textbf{(acepta)}" if x.aceptado else " (rechaza: " + tx(x.motivo) + ")"))
        if len(c.caminos) > 30:
            L.append(rf"\item \ldots y {len(c.caminos) - 30} caminos m\'as ({aceptan} aceptan en total).")
        L += [r"\end{enumerate}", "Conjuntos de estados activos: " + traza_tex(a, r) + ". " + r"\textbf{Resultado:} "
              + ("ACEPTA " if r.aceptada else "RECHAZA ") + mono(w) + ".",
              figuras_en_pares(a, [(w, r)]), r"\textbf{Otras cadenas de prueba:}", pruebas(a, con_figuras=False), ""]
    return L


# ---------------------------------------------------------------------------
# 191 a 195, 260 a 263
# ---------------------------------------------------------------------------

def bloque_conversion(num, nombre_afn, enunciado, preguntas=True):
    afn = por_nombre(nombre_afn)
    conv = afn.a_afd()
    afd = por_nombre(f"Ej_{num}_afd")
    minimo = afd.minimizar()
    n = len(afn.estados)
    L = [rf"\subsection{{Ejercicio {num}}}", "", r"\textbf{Enunciado:} " + enunciado, "",
         r"\textbf{AFN} (" + datos(afn) + "):", tabla_tex(afn), figura(afn, f"AFN del ejercicio {num}."),
         r"\textbf{Construcci\'on de subconjuntos.} El estado inicial del AFD es $\{" + tx(afn.inicial) + r"\}$; para cada estado "
         r"$S$ del AFD y cada s\'imbolo $a$, $\delta'(S,a)=\bigcup_{q\in S}\delta(q,a)$. Solo se crean los conjuntos que se alcanzan.",
         pasos_de_subconjuntos(afn, conv),
         r"\textbf{AFD equivalente} (" + datos(afd) + r"). Cada estado es un conjunto de estados del AFN; los de aceptaci\'on son los que "
         r"contienen un estado de aceptaci\'on del AFN.",
         tabla_tex(afd), figura(afd, f"AFD equivalente del ejercicio {num}."),
         f"El AFN tiene {n} estados y el AFD {len(afd.estados)} (la cota es $2^{{{n}}}={miles(2 ** n)}$); el AFD m\\'inimo tiene {len(minimo.estados)}.", ""]
    if preguntas and num in E.CONSULTAS:
        filas = []
        for inciso, c in E.CONSULTAS[num]:
            res = E.responder(afn, c)
            camino = r" $\to$ ".join(K.trazas_de_subconjuntos(afn, set(c[1]), c[2])).replace("{", r"$\{$").replace("}", r"$\}$").replace("∅", r"$\emptyset$")
            filas.append([inciso, consulta_tex(c), conj(afn, res), r"\small " + camino])
        L += [r"\textbf{Preguntas.} $\hat{\delta}$ es la funci\'on de transici\'on extendida del AFN y $\hat{\delta}_D$ la del AFD. Como los estados del AFD "
              r"son conjuntos y $\delta_D(S,a)=\bigcup_{q\in S}\delta(q,a)$, ambas dan el mismo conjunto (el AFD empieza en $Z$ y recorre los conjuntos de la \'ultima columna).",
              tabla_simple(["Inciso", "Pregunta", r"$\hat{\delta}=\hat{\delta}_D$", "Recorrido en el AFD"], filas, r"clcp{7.5cm}"), ""]
    L += [r"\textbf{Pruebas en el AFN} (el AFD acepta exactamente las mismas cadenas):", pruebas(afn), ""]
    return L


ENUN_191_195 = {
    "192": r"Para el AFN de la tabla, encuentre un AFD equivalente y calcule $\hat{\delta}(Z,\omega)$ y $\hat{\delta}_D(Z,\omega)$ para (a) $Z=\{A\},\ \omega=0111$ y (b) $Z=\{B,C\},\ \omega=010111$.",
    "193": r"Para el AFN de la tabla, encuentre un AFD equivalente y calcule $\hat{\delta}$ y $\hat{\delta}_D$ para (a) $Z=\{A\},\omega=01101$; (b) $Z=\{A,B\},\omega=1101$; (c) $Z=\{C\},\omega=1101$.",
    "194": r"Para el AFN de la tabla ($\Sigma=\{0,1,2\}$), encuentre un AFD equivalente y calcule $\hat{\delta}$ y $\hat{\delta}_D$ para (a) $Z=\{A,C\},\omega=0121$; (b) $Z=\{B\},\omega=20111$; (c) $Z=\{C\},\omega=02112$; (d) $Z=\{A,B\},\omega=0121$.",
    "195": r"Para el AFN de la tabla, encuentre un AFD equivalente y calcule $\hat{\delta}$ y $\hat{\delta}_D$ para (a) $Z=\{A\},\omega=10010$; (b) $Z=\{A,D\},\omega=0110$; (c) $Z=\{B,E\},\omega=0100$; (d) $Z=\{B,C,D\},\omega=10100$.",
}


def sec_conversiones():
    L = [r"\section{De AFN a AFD (191--195)}", "",
         r"\textbf{Enunciado (191).} En los problemas 191--194 (las tablas est\'an en 192--195), considere el aut\'omata finito no determinista "
         r"$A=(Q,\Sigma,\delta,A_0,F)$ definido en cada tabla. Encuentre un AFD equivalente y calcule (a) $\hat{\delta}(Z,\omega)$, con $\delta$ la funci\'on de "
         r"transici\'on del aut\'omata, y (b) $\hat{\delta}_D(Z,\omega)$, con $\delta_D$ la del AFD asociado."]
    for num in ("192", "193", "194", "195"):
        L += bloque_conversion(num, f"Ej_{num}_tabla", ENUN_191_195[num])
    return L


def sec_260_263():
    L = [r"\section{Equivalencia de AFD y AFN (260--263)}"]
    enun = {"260": r"Encuentre un AFD equivalente al siguiente AFN. Describa a detalle c\'omo lo obtuvo (los pasos de la construcci\'on de subconjuntos est\'an abajo).",
            "261": r"Dado el AFN de la figura (con $q_0$ inicial y $q_2$ de aceptaci\'on), determine el AFD equivalente. Los estados $q_3$ y $q_4$ no llevan a ning\'un estado de aceptaci\'on.",
            "262": r"Dise\~ne un AFN que acepte el conjunto $\{ab,ba\}$ y util\'icelo para encontrar un AFD que lo acepte. El AFN resulta determinista; el AFD solo agrega el estado $\emptyset$ para completarlo.",
            "263": r"Dado el AFN de la figura (acepta las cadenas que terminan en \texttt{01}), determine el AFD equivalente."}
    nombres = {"260": "Ej_260_tabla", "261": "Ej_261_figura", "262": "Ej_262_ab_ba", "263": "Ej_263_figura"}
    for num in ("260", "261", "262", "263"):
        L += bloque_conversion(num, nombres[num], enun[num], preguntas=False)
    return L


# ---------------------------------------------------------------------------
# 196 a 200
# ---------------------------------------------------------------------------

def sec_lambda():
    L = [r"\section{AFND con transiciones $\lambda$ (196--200)}", "",
         r"\textbf{Enunciado.} Dibuje el diagrama de transiciones de cada aut\'omata, encuentre un AFD equivalente (con su tabla y su diagrama) y halle "
         r"la informaci\'on que se pide en cada inciso. $\mathrm{Cl}$ es la $\lambda$-clausura: los estados alcanzables con solo transiciones $\lambda$, "
         r"incluido el propio estado. La funci\'on extendida aplica la clausura al inicio y despu\'es de cada s\'imbolo: "
         r"$\hat{\delta}(Z,\varepsilon)=\mathrm{Cl}(Z)$ y $\hat{\delta}(Z,wa)=\mathrm{Cl}\big(\bigcup_{q\in\hat{\delta}(Z,w)}\delta(q,a)\big)$.", "",
         r"\textbf{M\'etodo.} Primero se quitan las $\lambda$: $\delta'(q,a)=\mathrm{Cl}(\delta(\mathrm{Cl}(\{q\}),a))$ y $q$ es de aceptaci\'on si "
         r"$\mathrm{Cl}(\{q\})$ contiene un estado de aceptaci\'on. Despu\'es se aplica la construcci\'on de subconjuntos al AFND resultante."]
    for num in ("196", "197", "198", "199", "200"):
        a = por_nombre(f"Ej_{num}_tabla")
        sin = por_nombre(f"Ej_{num}_afnd")
        conv = sin.a_afd()
        afd = por_nombre(f"Ej_{num}_afd")
        clausuras = [[tx(q), conj(a, a.clausuras()[q])] for q in a.estados]
        filas = [[inciso, consulta_tex(c), conj(a, E.responder(a, c))] for inciso, c in E.CONSULTAS[num]]
        L += [rf"\subsection{{Ejercicio {num}}}", "", r"\textbf{AFND-$\lambda$} (" + datos(a) + "):", tabla_tex(a),
              figura(a, f"AFND-$\\lambda$ del ejercicio {num}."), r"\textbf{$\lambda$-clausura de cada estado:}",
              tabla_simple(["Estado", r"$\mathrm{Cl}(\text{estado})$"], clausuras, "lc"), r"\textbf{Respuestas:}",
              tabla_simple(["Inciso", "Pregunta", "Respuesta"], filas, "lcc"),
              r"\textbf{Paso 1: de AFND-$\lambda$ a AFND} (" + datos(sin) + "):", tabla_tex(sin),
              figura(sin, f"AFND sin transiciones $\\lambda$, ejercicio {num}."),
              r"\textbf{Paso 2: de AFND a AFD} (subconjuntos):", pasos_de_subconjuntos(sin, conv),
              r"\textbf{AFD equivalente} (" + datos(afd) + "):", tabla_tex(afd), figura(afd, f"AFD equivalente del ejercicio {num}."),
              f"Tama\\~nos: AFND-$\\lambda$ {len(a.estados)} estados, AFND {len(sin.estados)}, AFD {len(afd.estados)} "
              f"(cota $2^{{{len(sin.estados)}}}={2 ** len(sin.estados)}$).",
              r"\textbf{Pruebas en el AFND-$\lambda$} (la clausura es necesaria: sin las transiciones $\lambda$ cambiar\'ia el resultado):", pruebas(a), ""]
    return L


# ---------------------------------------------------------------------------
# 201 a 240 y 254 a 258
# ---------------------------------------------------------------------------

AFIRMACIONES = [("a", "a+b"), ("a", "ab"), ("a", "a*+b*"), ("a", "ab*"), ("a", "a*b"), ("ab", "a+b"), ("ab", "ab"), ("ab", "λa*b"),
                ("ab", "∅a*b"), ("ab", "(a+b)*"), ("ab", "abc*"), ("ab", "ab*c"), ("ab", "ab*c*"), ("ab", "(a+b+c)*"), ("ab", "(abc)*"),
                ("ab", "(ab)*c"), ("ab", "a(bc)*"), ("ab", "a(b+c)*"), ("ab", "(a+b)*c"), ("ab", "(a+b)*c*"), ("aa", "a+b"), ("aa", "a*+b*"),
                ("aa", "a*b*"), ("aa", "(a+b)*"), ("aa", "a(a+b)*"), ("", "a"), ("", "(a+b)*"), ("", "(a+b)*+a"), ("", "∅"), ("", "λ"),
                ("", "λ+a"), ("", "λa"), ("", "ab*"), ("", "(ab)*")]

LENGUAJES_236_240 = [
    ("236", r"$L=\{x001y : x,y\in\Sigma^{*}\}$", "(0+1)*001(0+1)*", lambda w: "001" in w,
     r"Cualquier cadena, luego \texttt{001}, luego cualquier cadena."),
    ("237", r"$L=\{x010 : x\in\Sigma^{*}\}$", "(0+1)*010", lambda w: w.endswith("010"), r"Cualquier cadena seguida de \texttt{010}."),
    ("238", r"$L=\Sigma^{3}\cup\Sigma^{5}$", "(0+1)(0+1)(0+1)(λ+(0+1)(0+1))", lambda w: len(w) in (3, 5),
     r"Tres s\'imbolos cualesquiera, y opcionalmente otros dos: longitud 3 o 5."),
    ("239", r"$L$ es el lenguaje de las cadenas que comienzan con \texttt{01} o que terminan con \texttt{10}.", "01(0+1)*+(0+1)*10",
     lambda w: w.startswith("01") or w.endswith("10"), r"Uni\'on de las que empiezan con \texttt{01} y las que terminan con \texttt{10}."),
    ("240", r"$L$ es el lenguaje de las cadenas que tienen longitud par y contienen la subcadena \texttt{01}.",
     "((0+1)(0+1))*01((0+1)(0+1))*+(0+1)((0+1)(0+1))*01(0+1)((0+1)(0+1))*", lambda w: len(w) % 2 == 0 and "01" in w,
     r"Si \texttt{01} empieza en posici\'on par, lo que queda antes y despu\'es tiene longitud par; si empieza en posici\'on impar, ambas son impares."),
]


def sec_regex():
    L = [r"\section{Expresiones regulares (201--240)}", "", r"\subsection{Ejercicios 201--235: verdadero o falso}", "",
         r"\textbf{Enunciado.} Indique si las afirmaciones son verdaderas (V) o falsas (F). Se obtuvo el lenguaje de cada expresi\'on y se comprob\'o si "
         r"contiene la cadena; $\lambda$ es la cadena vac\'ia y $\emptyset$ el lenguaje vac\'io (que no tiene ninguna cadena).", ""]
    filas = []
    for i, (w, r) in enumerate(AFIRMACIONES, start=201):
        e = X.parsear(r)
        pal = X.palabras(e, 2, "abc")
        corto = ", ".join(mono(p) for p in pal[:6]) + (r", \ldots" if len(pal) > 6 else "")
        filas.append([str(i), mono(w) + r" $\in L(" + er_tex(r).strip("$") + ")$", "V" if X.acepta(e, w) else "F",
                      r"\small " + (r"$\{$" + corto + r"$\}$" if pal else r"$\emptyset$")])
    filas.append(["235", r"$\emptyset\in L(\emptyset)$", "F", r"\small $L(\emptyset)=\emptyset$: $\emptyset$ no es una cadena, as\'i que no pertenece."])
    L += [tabla_simple([r"N.\textordmasculine", r"Afirmaci\'on", "Resp.", r"Cadenas de $L(r)$ de longitud $\leq 2$"], filas, r"clcp{8.2cm}"), ""]
    L += [r"\subsection{Ejercicios 236--240: expresi\'on regular de un lenguaje}", "",
          r"\textbf{Enunciado.} Para cada lenguaje $L$, con $\Sigma=\{0,1\}$, encuentre una expresi\'on regular cuyo lenguaje sea $L$."]
    for num, enun, regex, pert, razon in LENGUAJES_236_240:
        e = X.parsear(regex)
        muestra = ["", "0", "1", "00", "01", "10", "11", "001", "010", "0101", "1100", "0110", "10101", "011001", "1001", "0010"]
        filas = [[mono(w), "s\\'i" if pert(w) else "no", "s\\'i" if X.acepta(e, w) else "no"] for w in muestra]
        coincide = all(pert(w) == X.acepta(e, w) for n in range(13) for t in itertools.product("01", repeat=n) for w in ["".join(t)])
        assert coincide, f"la expresión de {num} no coincide con su lenguaje"
        L += [rf"\subsection*{{Ejercicio {num}}}", enun, "", r"\textbf{Expresi\'on regular:} " + er_tex(regex), "",
              r"\textbf{Razonamiento:} " + razon, "", tabla_simple(["Cadena", r"$\in L$", r"La expresi\'on la genera"], filas, "lcc"),
              r"Se compar\'o la expresi\'on con la definici\'on de $L$ para todas las cadenas hasta longitud 12: coinciden.", ""]
    L += [r"\subsection{Ejercicios 254--258: expresi\'on regular de un aut\'omata}", "",
          r"\textbf{Enunciado.} Para cada aut\'omata de la tabla encuentre una expresi\'on regular que lo represente.", "",
          r"\textbf{M\'etodo: eliminaci\'on de estados.} Se agregan un estado \texttt{inicio} (con una arista $\lambda$ al estado inicial) y un estado \texttt{fin} "
          r"(con una arista $\lambda$ desde cada estado de aceptaci\'on). Al eliminar un estado $k$, cada camino $p\to k\to q$ se reemplaza por la arista "
          r"$R(p,k)\,R(k,k)^{*}\,R(k,q)$, que se une a la que ya hubiera de $p$ a $q$. Al quedar solo \texttt{inicio} y \texttt{fin}, la etiqueta de la arista "
          r"que los une es la expresi\'on."]
    for n in range(254, 259):
        a = por_nombre(f"Ej_{n}_tabla")
        er, orden, pasos = X.desde_automata(a)
        L += [rf"\subsection*{{Ejercicio {n}}}", tabla_tex(a), figura(a, f"Ejercicio {n}."),
              r"\textbf{Orden de eliminaci\'on:} " + ", ".join(tx(q) for q in orden) + ". Aristas que quedan tras cada paso:", r"\begin{itemize}[leftmargin=1.2em]"]
        for p in pasos:
            aristas = "; ".join(f"{tx(o)} $\\to$ {tx(d)}: {er_tex(t)}" for o, d, t in p.aristas)
            L.append(r"\item al quitar " + tx(p.eliminado) + ": " + aristas)
        buenas, malas = K.casos_de_prueba(a)
        filas = [[mono(w), "acepta" if a.acepta(w) else "rechaza", "s\\'i" if X.acepta(er, w) else "no"] for w in buenas + malas]
        L += [r"\end{itemize}", r"\textbf{Expresi\'on regular:} " + er_tex(str(er)), "",
              tabla_simple(["Cadena", r"Aut\'omata", r"La expresi\'on la genera"], filas, "lcc"), ""]
    return L


# ---------------------------------------------------------------------------
# Anexos y documento completo
# ---------------------------------------------------------------------------

def anexo_resumen():
    filas = []
    for nombre in E.CONVERSIONES_AFN:
        num = nombre.split("_")[1]
        afn = E.POR_NOMBRE[nombre].fabrica()
        afd = E.POR_NOMBRE[f"Ej_{num}_afd"].fabrica()
        filas.append([num, str(len(afn.estados)), str(len(afd.estados)), str(len(afd.minimizar().estados)), miles(2 ** len(afn.estados))])
    for nombre in E.CONVERSIONES_LAMBDA:
        num = nombre.split("_")[1]
        sin = E.POR_NOMBRE[f"Ej_{num}_afnd"].fabrica()
        afd = E.POR_NOMBRE[f"Ej_{num}_afd"].fabrica()
        filas.append([num + r" ($\lambda$)", str(len(sin.estados)), str(len(afd.estados)), str(len(afd.minimizar().estados)), miles(2 ** len(sin.estados))])
    return [r"\appendix", r"\section{Resumen de las conversiones}", "",
            r"Estados del AFN (o del AFND sin $\lambda$), del AFD que da la construcci\'on de subconjuntos, del AFD m\'inimo y la cota $2^n$. "
            r"En ning\'un caso se alcanza la cota.", "",
            tabla_simple(["Ejercicio", "Estados AFN", "Estados AFD", r"AFD m\'inimo", r"Cota $2^{n}$"], filas, "lcccc"), ""]


LEYENDAS = {
    "01_afn_valida": r"Simulador: ejecuci\'on de la cadena v\'alida \texttt{10100010001} en el AFN del ejercicio 192. Acepta: al terminar quedan "
                     r"activos $\{B,C\}$ y $C$ es de aceptaci\'on. A la derecha, la traza completa con el paso actual resaltado.",
    "02_afn_invalida": r"Simulador: ejecuci\'on de la cadena inv\'alida \texttt{0110} en el mismo AFN. Tras leer \texttt{01} no queda ning\'un "
                       r"estado activo: el aut\'omata se bloquea y rechaza.",
    "03_lambda_inicio": r"Simulador: paso inicial del AFND-$\lambda$ del ejercicio 196 con la cadena \texttt{01}. La $\lambda$-clausura de $A$ es "
                        r"$\{A,B\}$ y se resalta la transici\'on $\lambda$.",
    "04_quitar_lambda": r"Simulador: conversi\'on del AFND-$\lambda$ del ejercicio 196 a un AFND sin transiciones $\lambda$.",
    "05_afd_subconjuntos": r"Simulador: construcci\'on de subconjuntos del ejercicio 196 y AFD resultante.",
}


def anexo_capturas():
    archivos = sorted(p for p in B.CAPTURAS.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg")) if B.CAPTURAS.is_dir() else []
    L = [r"\section{El simulador en ejecuci\'on}\label{anexo:capturas}", "",
         r"Capturas de la aplicaci\'on (Flet) que se desarroll\'o para la pr\'actica: definici\'on del aut\'omata, simulaci\'on paso a paso "
         r"con el estado actual, la transici\'on tomada y la traza completa, y conversiones."]
    for p in archivos:
        destino = B.IMG / f"captura-{p.stem.replace('_', '-')}{p.suffix.lower()}"
        shutil.copy(p, destino)
        pie = LEYENDAS.get(p.stem) or tx(p.stem.split("_", 1)[1].replace("_", " ") if "_" in p.stem else p.stem)
        L += [r"\begin{figure}[H]\centering", rf"\includegraphics[width=0.92\linewidth]{{img/{destino.name}}}", rf"\caption{{{pie}}}", r"\end{figure}"]
    if not archivos:
        L += [r"(No se encontraron capturas en \texttt{herramientas/capturas/}.)"]
    return L


def construir():
    cuerpo = []
    for seccion in (sec_simplificacion, sec_afn_descritos, sec_afn_lista2, sec_189_190, sec_conversiones, sec_lambda, sec_regex,
                    sec_260_263, anexo_resumen, anexo_capturas):
        cuerpo += seccion() + [""]
    texto = PREAMBULO + PORTADA + "\n".join(cuerpo) + "\n\\end{document}\n"
    for clave, valor in (("@@NOMBRE@@", B.ALUMNO["nombre"]), ("@@BOLETA@@", B.ALUMNO["boleta"]), ("@@GRUPO@@", B.ALUMNO["grupo"]),
                         ("@@PROFESOR@@", B.ALUMNO["profesor"])):
        texto = texto.replace(clave, valor)
    return texto
