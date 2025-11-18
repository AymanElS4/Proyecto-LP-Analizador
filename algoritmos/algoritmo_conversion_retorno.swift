var numero: Int = 42
var decimal: Double = 3.14
var texto: String = "Hola"
var booleano: Boolean = true

var numeroConvertido: Double = numero
var stringDelNumero: String = Int(100)

func obtenerValor() -> Int {
    return 42
}

func calcularPromedio(a: Int, b: Double) -> Double {
    let suma: Double = a + b
    return suma / 2
}

func procesar(valor: Int) -> String {
    if valor > 10 {
        return "Grande"
    } else {
        return "Pequeno"
    }
}

var resultado: Int = obtenerValor()
var promedio: Double = calcularPromedio(a: 10, b: 20.5)

let conversion1: Double = Double(numero)
let conversion2: String = String(42)
let conversion3: Int = Int("123")

func operaciones() -> Int {
    let x: Int = 5
    let y: Int = 3
    let suma: Int = x + y
    return suma
}

func comparacion(a: Int, b: Int) -> Boolean {
    return a > b
}

var array: [Int] = [1, 2, 3]
let elemento: Int = array[0]

func modificarArreglo(arr: [Int]) -> [Int] {
    return arr
}

func cadenas() -> String {
    let nombre: String = "Jordan"
    let apellido: String = "Sanchez"
    let completo: String = nombre + " " + apellido
    return completo
}

var x: Int = 10
var y: Double = 5.5
var operacion: Double = x + y

func retornoMultiple(n: Int) -> String {
    if n > 0 {
        return "Positivo"
    } else if n < 0 {
        return "Negativo"
    } else {
        return "Cero"
    }
}

var conversionInvalida: Int = "texto"

func faltaRetorno() -> Int {
    let valor: Int = 10
}

var tipoincompatible: Int = 3.14

func retornoIncorrecto() -> String {
    return 42
}

func parametrosNoCoinciden(a: Int, b: String) {
    return a + b
}

var funcionNoExiste: Int = funcionInexistente()

let conversionNoValida: Boolean = Int("abc")

func retornoVacio() -> Double {
    return
}

var asignacionTipoMalo: Int = Double(42)

func operacionInvalida() -> Int {
    let s: String = "texto"
    let n: Int = s + 5
    return n
}
