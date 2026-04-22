import socket
import threading
import json
import operator
from functools import reduce


def validar_estructura(dato):
    if not isinstance(dato, dict):
        return False
    if "operacion" not in dato or "datos" not in dato:
        return False
    if not isinstance(dato["datos"], list):
        return False
    return True


def operacion_suma(datos):
    return reduce(operator.add, datos, 0)


def operacion_multiplicacion(datos):
    return reduce(operator.mul, datos, 1)


def operacion_filtrar_pares(datos):
    return list(filter(lambda x: x % 2 == 0, datos))


OPERACIONES = {
    "suma": operacion_suma,
    "multiplicacion": operacion_multiplicacion,
    "filtrar_pares": operacion_filtrar_pares,
}


class TaskServer:
    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))

    def procesar_tarea(self, tarea):
        if not validar_estructura(tarea):
            return {"estado": "error", "resultado": "Estructura inválida"}

        operacion = tarea.get("operacion")
        datos = tarea.get("datos")

        if operacion not in OPERACIONES:
            return {
                "estado": "error",
                "resultado": f"Operación '{operacion}' no soportada",
            }

        try:
            resultado = OPERACIONES[operacion](datos)
            return {"estado": "ok", "resultado": resultado}
        except Exception as e:
            return {"estado": "error", "resultado": str(e)}

    def handle_client(self, client_conn):
        try:
            while True:
                data = client_conn.recv(4096)
                if not data:
                    break

                try:
                    tarea = json.loads(data.decode("utf-8"))
                except json.JSONDecodeError:
                    respuesta = json.dumps(
                        {"estado": "error", "resultado": "JSON inválido"}
                    ).encode("utf-8")
                    client_conn.send(respuesta)
                    continue

                if isinstance(tarea, list):
                    resultados = []
                    for t in tarea:
                        resultados.append(self.procesar_tarea(t))
                    respuesta = json.dumps(
                        {"estado": "ok", "resultados": resultados}
                    ).encode("utf-8")
                else:
                    respuesta = json.dumps(self.procesar_tarea(tarea)).encode("utf-8")

                client_conn.send(respuesta)

        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            client_conn.close()

    def start(self):
        self.server.listen()
        print(f"[INFO] Servidor iniciado en {self.host}:{self.port}")
        print("[INFO] Operaciones disponibles: suma, multiplicacion, filtrar_pares")
        try:
            while True:
                client_conn, addr = self.server.accept()
                print(f"[INFO] Conexión entrante desde {addr}")
                thread = threading.Thread(
                    target=self.handle_client, args=(client_conn,), daemon=True
                )
                thread.start()
        except KeyboardInterrupt:
            print("\n[INFO] Servidor detenido por el usuario.")
        finally:
            self.server.close()


if __name__ == "__main__":
    server = TaskServer()
    server.start()
