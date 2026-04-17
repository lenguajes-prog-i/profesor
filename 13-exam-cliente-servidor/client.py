import socket
import sys
import threading


class ChatClient:
    def __init__(self, host="127.0.0.1", port=5555, nickname="Anonimo"):
        self.host = host
        self.port = port
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def receive_messages(self):
        while self.connected:
            try:
                msg = self.client.recv(1024).decode("utf-8")
                if msg:
                    print(f"\n{msg}\n{self.nickname} > ", end="")
            except (ConnectionResetError, BrokenPipeError, OSError):
                print("\n[ERROR] Conexión perdida con el servidor.")
                self.connected = False
                break
            except UnicodeDecodeError:
                print("\n[ERROR] Error al decodificar mensaje.")
                break

    def start(self):
        try:
            self.client.connect((self.host, self.port))
            self.connected = True
            print(f"[INFO] Conectado al servidor {self.host}:{self.port}")

            self.client.send(self.nickname.encode("utf-8"))

            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()

            while self.connected:
                try:
                    msg = input(f"{self.nickname} > ").strip()

                    if not msg:
                        continue

                    if msg.lower() == "/quit":
                        self.client.send(msg.encode("utf-8"))
                        print("[INFO] Desconectando del servidor...")
                        self.connected = False
                        break
                    elif msg.lower() == "/help":
                        print("[INFO] Comandos disponibles:")
                        print("  /join <sala> - Unirse a una sala")
                        print("  /leave       - Salir de la sala actual")
                        print("  /rooms       - Listar salas disponibles")
                        print("  /msg <texto> - Enviar mensaje")
                        print("  /quit        - Desconectarse del servidor")
                        print("  /help        - Mostrar esta ayuda")
                        continue
                    elif (
                        msg.lower().startswith("/join ")
                        or msg.lower().startswith("/leave")
                        or msg.lower().startswith("/rooms")
                        or msg.lower().startswith("/msg ")
                        or msg.lower() == "/leave"
                        or msg.lower() == "/rooms"
                    ):
                        self.client.send(msg.encode("utf-8"))
                    else:
                        self.client.send(msg.encode("utf-8"))

                except EOFError:
                    self.connected = False
                    break
                except OSError as e:
                    print(f"\n[ERROR] Error de conexión: {e}")
                    self.connected = False
                    break

        except ConnectionRefusedError:
            print("[ERROR] No se pudo conectar al servidor. ¿Está ejecutándose?")
        except Exception as e:
            print(f"[ERROR] Error: {e}")
        finally:
            try:
                self.client.close()
            except OSError:
                pass


def main():
    nickname = None
    host = "127.0.0.1"
    port = 5555

    for i, arg in enumerate(sys.argv):
        if arg == "--nickname" and i + 1 < len(sys.argv):
            nickname = sys.argv[i + 1]
        elif arg == "--host" and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
        elif arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])

    if nickname is None:
        try:
            nickname = input("Ingresa tu nombre: ").strip()
            if not nickname:
                nickname = "Anonimo"
        except (EOFError, KeyboardInterrupt):
            nickname = "Anonimo"

    if not nickname:
        nickname = "Anonimo"

    client = ChatClient(host=host, port=port, nickname=nickname)
    client.start()


if __name__ == "__main__":
    main()
