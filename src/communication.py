import socket

BROADCAST_PORT = 15000
BROADCAST_MESSAGE = b"R u there?"
TIMEOUT = 5

"""It needs to run on a thread"""
def imhere_message():
    # Function responds to the "R u there" message
    LISTEN_PORT = 15000
    RESPONSE_MESSAGE = "Room ID"

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as hello_socket:
        hello_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        hello_socket.bind(("", LISTEN_PORT))

        # print(f"Listening on port {LISTEN_PORT}...")

        while True:
            message, addr = hello_socket.recvfrom(1024)
            # print(f"Received message from {addr[0]}: {message.decode()}")

            hello_socket.sendto(RESPONSE_MESSAGE, addr)
            # print(f"Response sent to {addr[0]}")


def discover_nodes():
    # Function broadcasts a message in order to detect active nodes
    active_rooms = dict()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as broadcast_socket:
        broadcast_socket.settimeout(TIMEOUT)
        broadcast_socket.sendto(BROADCAST_MESSAGE, ('192.168.1.255', BROADCAST_PORT))
        # print(f"Broadcast sent on port {BROADCAST_PORT}")
        print("[i] Locating active rooms...")

        # Listen for responses
        try:
            while True:
                # Receiving responses from any host that responds
                response, addr = broadcast_socket.recvfrom(1024)
                active_rooms.setdefault(response.decode(),[]).append(addr[0])
                # print(f"Received response from {addr[0]} on port {BROADCAST_PORT}: {response.decode()}")
        except socket.timeout:
            room_ids = set(active_rooms.keys())

            if not room_ids:
                print("[*] Active rooms not found.")
            else:
                print("[*] Active rooms have been found: ")
                print(room_ids)
