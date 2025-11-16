var entero: Int = 42;
var flotante: Double = 3.14159;
var cadena: String = "Hola Swift";
var booleano: Boolean = true;
var nulo: Int = nil;

var numeros: [Int] = [1, 2, 3, 4, 5];
var diccionario: [String: Int] = ["a": 1, "b": 2];
var tupla: (Int, String) = (42, "respuesta");

let constante: Int = 100;
let flotante_const: Double = 2.718;

var x = 5;
x += 10;
x -= 3;
x *= 2;
x /= 4;

var a = 10;
var b = 20;
if (a < b) {
    var resultado = a + b;
}

if (a > 5 && b < 30) {
    var condicion = true;
}

if (a == 10) {
    var igualdad = true;
} else if (a != 10) {
    var diferente = true;
}

var mayor = a > b ? "Si" : "No";

for i in 1...10 {
    var elemento = i;
}

for j in 1..<5 {
    var rango = j;
}

var colores = ["Rojo", "Verde", "Azul"];
let primer = colores[0];
let segundo = colores[1];

colores[0] = "Amarillo";
colores[1] = "Naranja";

var matriz = [[1, 2], [3, 4]];
matriz[0][0] = 99;

func sumar(a: Int, b: Int) -> Int {
    return a + b;
}

func validar(numero: Int) -> Boolean {
    if (numero > 0) {
        return true;
    } else {
        return false;
    }
}

var resultado = sumar(5, 10);

if (resultado > 10) {
    var esGrande = true;
}

var datos: [String: Double] = ["pi": 3.14, "e": 2.71];
var valor = datos["pi"];

let tupla_simple: (String, Int, Double) = ("test", 42, 3.14);

var lista = [10, 20, 30];
if (lista[0] == 10
    lista[0] = 100;
}

var vector: [Double] = [1.1, 2.2 3.3];

let indefinido: Int = 
if (indefinido != nil) {
    var valido = true;
}

func procesarTupla(datos: (Int, String)) -> Boolean {
    return true;
}

var diccionario_incompleto: [String: Int] = [;

for numero in 1...100 {
    var contador = numero;
}

var combinado = (a > b ? "Mayor" : "Menor") || "Indefinido";

if (x >= 0 && y <= 100 || z != 50) {
    var compuesto = true;
}

var multi_asignacion = x += y -= z *= 2;

if ((a + b) * (c - d) > resultado) {
    var expresion_compleja = true;
}

var rango_abierto = 1..<50;
var rango_cerrado = 1...50;

func obtenerDatos() -> (String, Int, Boolean) {
    return ("data", 123, true);
}
