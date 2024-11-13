import thread
import socket
import argparse

# Funkcja wysyla broadcast po calej sieci, aby znalezc wolne pokoje.
# W odpowiedzi otrzymuje ID pokojow oraz adresy podlaczone do danego pokoju
# Funkcja uruchamia sie przy przekazaniu komendy --discover
def discover_nodes():
    # VARIABLES IT TAKES:
    BROADCAST_PORT = 15000
    BROADCAST_MESSAGE = b"R u there?"
    TIMEOUT = 5

    active_rooms = dict()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as broadcast_socket:
        broadcast_socket.settimeout(TIMEOUT)
        broadcast_socket.sendto(BROADCAST_MESSAGE, ('192.168.1.255', BROADCAST_PORT))
        #print(f"Broadcast sent on port {BROADCAST_PORT}")
        print("Trwa wykrywanie aktywnych pokojow...")

        # Listen for responses
        try:
            while True:
                # Receiving responses from any host that responds
                response, addr = broadcast_socket.recvfrom(1024)
                active_rooms.setdefault(response.decode(),[]).append(addr[0])
                #print(f"Received response from {addr[0]} on port {BROADCAST_PORT}: {response.decode()}")
        except socket.timeout:
            print("Broadcast response listening timed out.")
            room_ids = set(active_rooms.keys())
            print(room_ids)

# Funkcja odpowiadajaca na wiadomosc "R u there"
# W odpowiedzi wysyla ID pokoju
# Funkcja musi dzialac w osobnym watku
def hello_message():
    LISTEN_PORT = 15000
    RESPONSE_MESSAGE = "Room ID"

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as hello_socket:
        hello_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        hello_socket.bind(("", LISTEN_PORT))

        #print(f"Listening on port {LISTEN_PORT}...")

        while True:
                message, addr = hello_socket.recvfrom(1024)
                #print(f"Received message from {addr[0]}: {message.decode()}")

                hello_socket.sendto(RESPONSE_MESSAGE, addr)
                #print(f"Response sent to {addr[0]}")


# SECCOM MAIN
parser = argparse.ArgumentParser(
    prog="SecCom",
    description='SecCom is a P2P, terminal-based, end-to-end encrypted secure chat.')
parser.add_argument("-d", "--discover", help="Discover active rooms", action="store_true")
parser.add_argument("-i", help="Room ID you want to join", type=str)

args = parser.parse_args()

if args.discover: discover_nodes()
# SECCOM
