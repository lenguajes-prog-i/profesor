def calcular(a, b, op):
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/':
        if b == 0:
            return "Error: división por cero"
        return a / b
    return "Operador no válido"

print("=== Calculadora básica ===")
print("Operadores: + - * /")

while True:
    entrada = input("\nEjemplo: 5 + 3 (o 'salir'): ")
    if entrada.lower() == 'salir':
        break
    try:
        a, op, b = entrada.split()
        resultado = calcular(float(a), float(b), op)
        print(f"Resultado: {resultado}")
    except ValueError:
        print("Formato inválido. Usa: número operador número")
