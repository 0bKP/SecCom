import socket
import threading

LISTEN_PORT = 15000
RESPONSE_MESSAGE = b"Room ID"
def hello_message():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as hello_socket:
        hello_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        hello_socket.bind(("", LISTEN_PORT))

        print(f"Listening on port {LISTEN_PORT}...")  #

        while True:
            message, addr = hello_socket.recvfrom(1024)
            print(f"Received message from {addr[0]}: {message.decode()}")  #

            hello_socket.sendto(RESPONSE_MESSAGE, addr)
            print(f"Response sent to {addr[0]}")  #


def start_server():  # ZAMIANA NA SERWER ASYNCHRONICZNY
    # Tworzenie gniazda (socket) dla połączeń TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 15000))
    server_socket.listen(5)  # Kazdy host moze polaczyc sie maks do 3 innych wezlow

    print(f"Serwer nasłuchuje na 0.0.0.0:12345...")
    client_socket, client_address = server_socket.accept()
    # print(f"client_socket: {client_socket}") #
    # print(f"client_address: {client_address}") #
    print(f"Połączono z {client_address}")

    """
    try:
        while True:
            # Odbieranie wiadomości od klienta
            message = client_socket.recv(1024).decode('utf-8')
            print(f"{message}")

            # Zamknięcie połączenia z klientem

            #client_socket.close()
            #print("Połączenie zakończone.")
    except KeyboardInterrupt:
        print("Serwer został zatrzymany.")
    finally:
        server_socket.close()
    """
    threading.Thread(target=send_message, args=(client_socket,)).start()
    threading.Thread(target=receive_message, args=(client_socket,)).start()


def send_message(connection):
    while True:
        message = input("> ")
        connection.send(message.encode("utf-8"))


def receive_message(connection):
    while True:
        message = connection.recv(1024).decode("utf-8")
        if message:
            print(message)
        else:
            break


if __name__ == "__main__":
    # port = int(input("Podaj numer portu, na którym węzeł ma nasłuchiwać: "))
    port = 12345
    threading.Thread(target=hello_message).start()
    threading.Thread(target=start_server).start()

