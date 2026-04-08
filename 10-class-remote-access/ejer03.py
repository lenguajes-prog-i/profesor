import pickle


class Auto:
    def __init__(self, modelo, placa):
        self.modelo = modelo
        self.placa = placa

    def __repr__(self):
        return f"El auto {self.modelo} tiene placa {self.placa}"


objeto_auto = Auto("Mazda", "ABC123")
objeto_auto1 = Auto("Mazda1", "ABC153")
objeto_auto2 = Auto("Mazda2", "ABC113")
objeto_auto3 = Auto("Mazda3", "ABC143")
objeto_auto4 = Auto("Mazda3", "ABC124")

# Esto guarda solo un objeto
# Escritura en autos.txt
archivo_auto = open("autos.txt", "wb")
pickle.dump(objeto_auto, archivo_auto)
archivo_auto.close()

# Lectura en autos.txt
archivo_auto = open("autos.txt", "rb")
autos = pickle.load(archivo_auto)
archivo_auto.close()

print(autos)
