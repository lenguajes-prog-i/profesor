import socket
import threading


class ChatServer:
    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
        self.clients = []
        self.nicknames = []
        self.rooms = {"general": [], "deportes": []}
        self.client_rooms = {}
        self.lock = threading.Lock()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))

    def broadcast(self, message, sender_conn=None):
        """Envía el mensaje a todos los clientes excepto al remitente."""
        with self.lock:
            for client in self.clients:
                if client != sender_conn:
                    try:
                        client.send(message)
                    except (BrokenPipeError, ConnectionResetError, OSError):
                        self.remove_client(client)

    def broadcast_to_room(self, room_name, message, sender_conn=None):
        """Envía el mensaje solo a clientes en la sala especificada."""
        with self.lock:
            room_clients = self.rooms.get(room_name, [])
            for client in room_clients:
                if client != sender_conn:
                    try:
                        client.send(message)
                    except (BrokenPipeError, ConnectionResetError, OSError):
                        self.remove_client(client)

    def join_room(self, client_conn, room_name):
        """Une un cliente a una sala."""
        with self.lock:
            current_room = self.client_rooms.get(client_conn)
            if current_room and client_conn in self.rooms.get(current_room, []):
                self.rooms[current_room].remove(client_conn)

            if room_name not in self.rooms:
                self.rooms[room_name] = []

            self.rooms[room_name].append(client_conn)
            self.client_rooms[client_conn] = room_name

        return current_room

    def leave_room(self, client_conn):
        """Saca al cliente de su sala actual."""
        with self.lock:
            current_room = self.client_rooms.get(client_conn)
            if current_room and client_conn in self.rooms.get(current_room, []):
                self.rooms[current_room].remove(client_conn)
            self.client_rooms.pop(client_conn, None)

        return current_room

    def list_rooms(self):
        """Lista las salas disponibles."""
        with self.lock:
            return list(self.rooms.keys())

    def remove_client(self, client_conn):
        with self.lock:
            if client_conn in self.clients:
                self.clients.remove(client_conn)
            current_room = self.client_rooms.get(client_conn)
            if current_room and client_conn in self.rooms.get(current_room, []):
                self.rooms[current_room].remove(client_conn)
            self.client_rooms.pop(client_conn, None)
            try:
                client_conn.close()
            except OSError:
                pass

    def handle_client(self, client_conn):
        """Atiende a un cliente específico en un hilo."""
        nickname = None
        current_room = None
        try:
            while True:
                message = client_conn.recv(1024)
                if not message:
                    break

                decoded_msg = message.decode("utf-8")

                if nickname is None:
                    nickname = decoded_msg
                    with self.lock:
                        self.nicknames.append(nickname)
                        self.clients.append(client_conn)
                    print(f"[+] {nickname} conectado")
                    current_room = self.join_room(client_conn, "general")
                    client_conn.send(
                        f"[INFO] Bienvenido a la sala 'general'. Usa /help para ver comandos.".encode(
                            "utf-8"
                        )
                    )
                    self.broadcast_to_room(
                        "general",
                        f"[+] {nickname} se ha unido a la sala 'general'".encode(
                            "utf-8"
                        ),
                        client_conn,
                    )
                else:
                    if decoded_msg.startswith("/join "):
                        room_name = decoded_msg[6:].strip()
                        old_room = self.join_room(client_conn, room_name)
                        old_room_name = old_room or "ninguna"
                        client_conn.send(
                            f"[INFO] Te uniste a la sala '{room_name}'".encode("utf-8")
                        )
                        print(f"[+] {nickname} se unió a sala '{room_name}'")
                        self.broadcast_to_room(
                            room_name,
                            f"[+] {nickname} se ha unido a la sala '{room_name}'".encode(
                                "utf-8"
                            ),
                            client_conn,
                        )
                    elif decoded_msg == "/leave":
                        old_room = self.leave_room(client_conn)
                        if old_room:
                            client_conn.send(
                                "[INFO] Saliste de la sala".encode("utf-8")
                            )
                            print(f"[-] {nickname} salió de sala '{old_room}'")
                            self.broadcast_to_room(
                                old_room,
                                f"[-] {nickname} ha salido de la sala".encode("utf-8"),
                                client_conn,
                            )
                        else:
                            client_conn.send(
                                "[INFO] No estás en ninguna sala".encode("utf-8")
                            )
                    elif decoded_msg == "/rooms":
                        room_list = self.list_rooms()
                        client_conn.send(
                            f"[INFO] Salas disponibles: {', '.join(room_list)}".encode(
                                "utf-8"
                            )
                        )
                    elif decoded_msg == "/quit":
                        client_conn.send("[INFO] Desconectando...".encode("utf-8"))
                        break
                    elif decoded_msg == "/help":
                        help_text = "[INFO] Comandos: /join <sala>, /leave, /rooms, /msg <texto>, /quit"
                        client_conn.send(help_text.encode("utf-8"))
                    elif decoded_msg.startswith("/msg "):
                        msg_text = decoded_msg[5:]
                        current_room = self.client_rooms.get(client_conn)
                        if current_room:
                            full_msg = (
                                f"[{current_room}] {nickname}: {msg_text}".encode(
                                    "utf-8"
                                )
                            )
                            self.broadcast_to_room(current_room, full_msg, client_conn)
                            print(f"[INFO] Mensaje broadcast a sala '{current_room}'")
                        else:
                            client_conn.send(
                                "[ERROR] No estás en ninguna sala".encode("utf-8")
                            )
                    else:
                        current_room = self.client_rooms.get(client_conn)
                        if current_room:
                            full_msg = (
                                f"[{current_room}] {nickname}: {decoded_msg}".encode(
                                    "utf-8"
                                )
                            )
                            self.broadcast_to_room(current_room, full_msg, client_conn)
                            print(f"[INFO] Mensaje broadcast a sala '{current_room}'")
                        else:
                            client_conn.send(
                                "[ERROR] No estás en ninguna sala. Usa /join <sala>".encode(
                                    "utf-8"
                                )
                            )

        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            if nickname:
                print(f"[-] {nickname} desconectado")
                current_room = self.client_rooms.get(client_conn)
                if current_room:
                    self.broadcast_to_room(
                        current_room,
                        f"[-] {nickname} ha salido del chat".encode("utf-8"),
                        client_conn,
                    )
                    with self.lock:
                        if (
                            current_room in self.rooms
                            and client_conn in self.rooms[current_room]
                        ):
                            self.rooms[current_room].remove(client_conn)
                with self.lock:
                    if nickname in self.nicknames:
                        self.nicknames.remove(nickname)
            self.remove_client(client_conn)

    def start(self):
        self.server.listen()
        print(f"[INFO] Servidor iniciado en {self.host}:{self.port}")
        try:
            while True:
                client_conn, addr = self.server.accept()
                print(f"[INFO] Conexión entrante desde {addr}")
                thread = threading.Thread(
                    target=self.handle_client, args=(client_conn,)
                )
                thread.start()
        except KeyboardInterrupt:
            print("\n[INFO] Servidor detenido por el usuario.")
        finally:
            self.server.close()


if __name__ == "__main__":
    server = ChatServer()
    server.start()
