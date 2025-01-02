import socket
import threading
import encryption
import json

BROADCAST_MESSAGE = b"R u there?"


class Client(threading.Thread):
    def __init__(self, port=15000):
        super(Client, self).__init__()
        self.port = port
        self.conn_count = 0
        self.timeout = 5

    def discover_nodes(self, verbose=True):
        # Function broadcasts a message in order to detect active nodes
        active_rooms = dict()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as broadcast_socket:
            broadcast_socket.settimeout(self.timeout)

            broadcast_ip = self.get_broadcast_ip()
            # print(f"BC IP: {broadcast_ip}") #
            broadcast_socket.sendto(BROADCAST_MESSAGE, (broadcast_ip, self.port))
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
                        # print(active_rooms) #
                    return active_rooms
                    # connect_to_room()

    def get_broadcast_ip(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        octets = ip.split(".")
        octets[3] = "255"
        octets = ".".join(octets)

        return octets

    def connect_to_room(self, room_id, username):
        # x = input("connect_to_room exec") #
        active_rooms = self.discover_nodes(verbose=False)
        target_ip = active_rooms[room_id]
        # print(len(target_ip)) #
        # Zaimplementowac spanning tree dla len(active_rooms[room_id]) >= 5

        if not target_ip:
            print(f"[!] Room {room_id} not found.")
            return

        if len(target_ip) < 5:
            for ip in target_ip:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    client.connect((ip, self.port))
                    print(f"Connected to {ip}:{self.port}")
                    self.conn_count += 1
                    # self.exchange_keys(client)
                    threading.Thread(target=self.receive_message, args=(client,)).start()
                    threading.Thread(target=self.send_message, args=(client, username)).start()
                except Exception as e:
                    print(f"[!] Failed to connect to {ip}: {e}")

        """
        if self.conn_count > 0:
            server_inst = server.Server(listen_port=15000, room_id=room_id.encode())
            threading.Thread(target=server_inst.start).start()
        """

    def send_message(self, client_socket, username):
        # x = input("send_message exec") #
        # print("node_addr: ", node_addr) #
        while True:
            message = input("> ")
            packet = json.dumps({
                "message": message,
                "username": username,
                "MID": "M0001:000"
            })
            client_socket.send(packet.encode("utf-8"))

    def exchange_key(self, key):
        recv_rsa_key = encryption.receive_key(message_dict["key"])
        aes_key = encryption.generate_aes_key()
        encrypted_aes_key = encryption.encrypt_aes_key_with_rsa(aes_key, recv_rsa_key)

    def receive_message(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                message_dict = json.loads(message)
                if message_dict["MID"] == "M0000-000":
                    public_key = encryption.receive_key(message_dict["key"])
                    aes_key = encryption.generate_aes_key()
                    encrypted_aes_key = encryption.encrypt_aes_key_with_rsa(aes_key, public_key)
                    # print(public_key, aes_key, encrypted_aes_key)
                elif message_dict["MID"] != "M0000-000":
                    print("username" + ": " + message_dict["message"])
                else:
                    break
            except Exception as e:
                print("Wystapil blad!")
                print(e)

# discover_nodes() #
