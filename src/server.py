import socket
import threading
import encryption
import json


class Server(threading.Thread):
    def __init__(self, listen_port=15000, room_id=None, stash=True):
        super(Server, self).__init__()
        self.listen_port = listen_port
        self.room_id = room_id
        self.stash = stash
        self.clients = []
        self.hosts = []
        # print(f"Zainicjalizowano {listen_port}, {room_id}") #

    def hello_message(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as hello_socket:
            hello_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            hello_socket.bind(("", self.listen_port))

            print(f"Listening on port {self.listen_port}...")  #

            while True:
                message, addr = hello_socket.recvfrom(1024)
                print(f"Received hello from {addr[0]}: {message.decode()}")  #

                if addr[0] not in self.hosts:
                    self.hosts.append(addr[0])

                response_data = {
                    "room_id": self.room_id.decode(),
                    "hosts": self.hosts}
                response_json = json.dumps(response_data)

                hello_socket.sendto(response_json.encode(), addr)
                print(f"Response sent to {addr[0]}")  #

    def handle_client(self, client_socket, client_address):
        print(f"Połączono z {client_address}")
        self.clients.append(client_socket)

        encryption.send_rsa_key(client_socket)
        threading.Thread(target=self.send_message, args=(client_socket,)).start()
        threading.Thread(target=self.receive_message, args=(client_socket,)).start()

    def broadcast_message(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    # Remove disconnected clients
                    self.client.remove(client)

    def run(self):  # Function called by threading on start
        threading.Thread(target=self.hello_message).start()

        # Tworzenie gniazda (socket) dla połączeń TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", self.listen_port))
        server_socket.listen(5)  # Kazdy host moze polaczyc sie maks do 3 innych wezlow

        print(f"Serwer nasłuchuje na 0.0.0.0:15000...")
        # client_socket, client_address = server_socket.accept()
        # print(f"client_socket: {client_socket}") #
        # print(f"client_address: {client_address}") #

        while True:
            client_socket, client_address = server_socket.accept()
            self.handle_client(client_socket, client_address)

    def send_message(self, connection):
        while True:
            message = input("> ")
            packet = json.dumps({
                "message": message,
                # "username" : username,
                "MID": "M0001:000"
            })
            connection.send(packet.encode("utf-8"))

    def receive_message(self, connection):
        while True:
            message = connection.recv(1024).decode("utf-8")
            message_dict = json.loads(message)
            if message:
                print(message_dict["username"] + ": " + message_dict["message"])
            else:
                break
