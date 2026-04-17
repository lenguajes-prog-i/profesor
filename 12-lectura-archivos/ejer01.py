with open("data.txt", "r", encoding="utf-8") as archivo:
    for linea in archivo:
        nombre, edad = linea.strip().split(",")
        print(f"Nombre: {nombre} - Edad: {edad}")
