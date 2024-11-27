import socket
import threading


class Server(threading.Thread):
    def __init__(self, listen_port=15000, room_id=None):
        super(Server, self).__init__()
        self.listen_port = listen_port
        self.room_id = room_id
        # print(f"Zainicjalizowano {listen_port}, {room_id}") #

    def hello_message(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as hello_socket:
            hello_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            hello_socket.bind(("", LISTEN_PORT))

            print(f"Listening on port {LISTEN_PORT}...")  #

            while True:
                message, addr = hello_socket.recvfrom(1024)
                print(f"Received message from {addr[0]}: {message.decode()}")  #

                hello_socket.sendto(self.room_id, addr)
                print(f"Response sent to {addr[0]}")  #

    def run(self):  # Function called by threading on start
        threading.Thread(target=self.hello_message).start()
        # Tworzenie gniazda (socket) dla połączeń TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", self.listen_port))
        server_socket.listen(5)  # Kazdy host moze polaczyc sie maks do 3 innych wezlow

        print(f"Serwer nasłuchuje na 0.0.0.0:15000...")
        client_socket, client_address = server_socket.accept()
        # print(f"client_socket: {client_socket}") #
        # print(f"client_address: {client_address}") #
        print(f"Połączono z {client_address}")

        threading.Thread(target=self.send_message, args=(client_socket,)).start()
        threading.Thread(target=self.receive_message, args=(client_socket,)).start()

    def send_message(self, connection):
        while True:
            message = input("> ")
            connection.send(message.encode("utf-8"))

    def receive_message(self, connection):
        while True:
            message = connection.recv(1024).decode("utf-8")
            if message:
                print(message)
            else:
                break
