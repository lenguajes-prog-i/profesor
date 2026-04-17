names = ["Alice", "Carmen", "Ramon", "Sofia"]


def retor_names(nom):
    return nom[0] == "A"


lista_nombres = list(filter(lambda x: x[0] == "A", names))

print(lista_nombres)
