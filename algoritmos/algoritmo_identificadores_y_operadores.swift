import Foundation

// Identificadores y variables
var numero: Int = 10
var mensaje: String = "Hola, Ariel"
var _resultado: Double = 3.14
let saludo = "¡Buen día!"

print(mensaje, numero, _resultado, saludo)

// Operadores básicos
let a = 7
let b = 3
let suma = a + b
let resta = a - b
let mult = a * b
let div = a / b
let resto = a % b
print("suma=\(suma) resta=\(resta) mult=\(mult) div=\(div) resto=\(resto)")

// Comparaciones y operadores lógicos
let esMayor = a > b
let esIgual = a == b
let condicion = (a > 0) && (b > 0)
let condicion2 = !(a < 0)
print("esMayor=\(esMayor) esIgual=\(esIgual) condicion=\(condicion) condicion2=\(condicion2)")

// Funciones
func incrementar(_ valor: Int, en inc: Int = 1) -> Int {
    return valor + inc
}
print("incrementar(5) =", incrementar(5))
print("incrementar(5, en: 3) =", incrementar(5, en: 3))

// Tuplas
let tupla: (Int, String, Double) = (42, "respuesta", 2.718)
let (miEntero, miString, miDouble) = tupla
print("tupla:", miEntero, miString, miDouble)

// While
var contador = 3
var acumulador = 0
while contador > 0 {
    acumulador += contador
    contador -= 1
}
print("acumulador =", acumulador)

// Resultado final
print("Prueba completada correctamente — identificadores y operadores OK")
