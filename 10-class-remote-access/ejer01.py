import pickle

data = {"mesaje": "Hola"}

serializacion = pickle.dumps(data)
mesaje = pickle.loads(serializacion)

print(mesaje)
