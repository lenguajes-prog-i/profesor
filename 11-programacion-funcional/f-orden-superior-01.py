def crear_multiplicador(factor):
    def multiplicar(numero):
        return numero * factor

    return multiplicar


doble = crear_multiplicador(2)
triple = crear_multiplicador(3)

print(doble(5))
print(triple(5))
