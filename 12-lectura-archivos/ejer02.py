import json

with open("files/data.json", "r", encoding="utf-8") as archivo:
    datos = json.load(archivo)

for usuario in datos:
    print(f"Usuario: {usuario['nombre']} - Edad: {usuario['edad']}")
