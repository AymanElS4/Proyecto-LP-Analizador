let x: Int = 10
let y: Double = 3.14
let z: Bool = true
let letra: Character = 'a'
let mensaje: String = "Hola Swift"
let resultado = x + 5 * (2 + 3)
let edades = ["Ana": 20, "Luis": 18, "Carlos": 22]
let vacio: [String:Int] = [:]
let mezclado: [String:Any] = ["x": 10, "y": true, "z": "texto"]
for i in 0...5 {
    print(i)
}

for nombr in ["Ana", "Luis", "Carlos"] {
    print("Hola \(nombre)")
}
print("Ingresa tu nombre: ")
let nombre = readLine()
print("Hola \(nombre!)")
let calc = 10 + 5 * 3 - (8 / 2) + 4 % 3
let logicos = (x > 5 && y < 10) || !(z == false)
if x > 5 && y < 10 || z == true {
    print("Condición compleja")
}
let sinValor =
let faltaParentesis = (5 + 3