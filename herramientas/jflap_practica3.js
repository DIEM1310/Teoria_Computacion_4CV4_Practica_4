// Ejecuta con las clases de JFLAP 7.1 (sin abrir la ventana) lo que pide el Ejercicio 1.1:
// expresion regular (Convert FA to RE), NFA de esa expresion (Convert to NFA),
// comprobacion de equivalencia (Compare Equivalence) y Multiple Run sobre el AFD.
// Uso, desde la raiz del repositorio (Java 8; jjs es el interprete de JavaScript de Java 8):
//   jjs -J-Djava.awt.headless=true -cp RUTA/JFLAP7.1.jar herramientas/jflap_practica3.js
// Salida (una linea por autometa): ejercicio, ER, estados del NFA, equivalentes, respuesta a cada cadena.
// La lambda se imprime como "?" si la consola no usa UTF-8.
var base = "automatas/practica3/afd-a-er/";
var Codec = Java.type("file.XMLCodec"), File = Java.type("java.io.File");
var RE = Java.type("regular.RegularExpression");
var Env = Java.type("gui.environment.RegularEnvironment");
var Pane = Java.type("gui.regular.ConvertToAutomatonPane");
var Eq = Java.type("automata.graph.FSAEqualityChecker");
var Conv = Java.type("automata.fsa.FSAToRegularExpressionConverter");
var SF = Java.type("automata.SimulatorFactory");
function campoDeTipo(obj, tipo){
  var cl = obj.getClass();
  while (cl != null){
    var fs = cl.getDeclaredFields();
    for (var i=0;i<fs.length;i++){
      if (tipo.isAssignableFrom(fs[i].getType())) { fs[i].setAccessible(true); return fs[i].get(obj); }
    }
    cl = cl.getSuperclass();
  }
  return null;
}
function cargar(n){ return new Codec().decode(new File(base+"Ej_"+n+"_tabla.jff"), null); }
function nfaDe(er){
  var pane = new Pane(new Env(new RE(er)));
  var ctrl = campoDeTipo(pane, Java.type("gui.regular.REToFSAController").class);
  ctrl.completeAll();
  return campoDeTipo(ctrl, Java.type("automata.fsa.FiniteStateAutomaton").class);
}
function necesitaFinalUnico(fa){ var fs = fa.getFinalStates(); return !(fs.length == 1 && fs[0] != fa.getInitialState()); }
function er_jflap(n){
  var fa = cargar(n);
  if (necesitaFinalUnico(fa)) Conv.getSingleFinalState(fa);
  Conv.convertToSimpleAutomaton(fa);
  return Conv.convertToRegularExpression(fa);
}
var cadenas = {
  254: ["", "1", "01", "110", "0101", "10"],
  255: ["", "1", "01", "110", "0101", "10"],
  256: ["", "1", "01", "110", "0101", "2"],
  257: ["", "1", "01", "110", "0101", "10"],
  258: ["", "1", "01", "110", "0101", "10"]
};
[254,255,256,257,258].forEach(function(n){
  var er = er_jflap(n);
  var orig = cargar(n);
  var nfa = nfaDe(er);
  var eq = new Eq().equals(orig, nfa);
  var sim = SF.getSimulator(orig);
  var salida = cadenas[n].map(function(s){ return (s===""?"λ":s) + "=" + (sim.simulateInput(s) ? "Accept" : "Reject"); });
  print(n + "\t" + er + "\t" + nfa.getStates().length + "\t" + eq + "\t" + salida.join(" "));
});
