import pickle

datos = {
    "nombre": "Cortes Perez Andres Steven",
    "materia": "Lenguaje de Programacion I",
    "notas": [1, 2.5, 2.5, 3],
}

with open("data.txt", "wb") as archivo:
    pickle.dump(datos, archivo)

with open("data.txt", "rb") as archivo:
    datos_estudiantes = pickle.load(archivo)

print(datos_estudiantes)
