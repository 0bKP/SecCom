import socket
import threading
import server

PORT = 15000
BROADCAST_MESSAGE = b"R u there?"
TIMEOUT = 5
CONNECTION = False


class Client(threading.Thread):
    def __init__(self):
        super(Client, self).__init__()

    def discover_nodes(self, verbose=True):
        # Function broadcasts a message in order to detect active nodes
        active_rooms = dict()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as broadcast_socket:
            broadcast_socket.settimeout(TIMEOUT)
            broadcast_socket.sendto(BROADCAST_MESSAGE, ('192.168.175.255', PORT))
            # print(f"Broadcast sent on port {BROADCAST_PORT}") #
            if verbose: print("[i] Locating active rooms...")

            try:
                while True:
                    response, addr = broadcast_socket.recvfrom(1024)
                    active_rooms.setdefault(response.decode(), []).append(addr[0])
                    # print(f"Received response from {addr[0]} on port {BROADCAST_PORT}: {response.decode()}") #
            except socket.timeout:
                room_ids = set(active_rooms.keys())

                if not room_ids:
                    if verbose: print("[*] Active rooms not found.")
                else:
                    if verbose:
                        print("[*] Active rooms have been found: ")
                        print(room_ids)
                    return active_rooms
                    # connect_to_room()

    def connect_to_room(self, room_id, username):
        x = input("connect_to_room exec")  #
        active_rooms = self.discover_nodes(verbose=False)
        target_ip = active_rooms[room_id]
        # print(len(target_ip)) #
        # Zaimplementowac spanning tree dla len(active_rooms[room_id]) >= 5

        if len(target_ip) < 5:
            for ip in target_ip:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((ip, PORT))
                print(f"Polaczono z {ip}:{PORT}")  #
                CONNECTION = True
                threading.Thread(target=self.receive_message, args=(client,)).start()
                threading.Thread(target=self.send_message, args=(client, username)).start()

        """
        if CONNECTION:
            threading.Thread(target=server.hello_message).start()
            threading.Thread(target=server.start_server).start()
        """

    def send_message(self, client_socket, username):
        # x = input("send_message exec") #
        # print("node_addr: ", node_addr) #
        while True:
            message = input("> ")
            message = username + ": " + message
            client_socket.send(message.encode("utf-8"))

    def receive_message(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                if message:
                    print(message)
                else:
                    break
            except Exception as e:
                print("Wystapil blad!")
                print(e)

# discover_nodes() #
