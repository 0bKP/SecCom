import socket
import threading
import encryption
import json
import sys

BROADCAST_MESSAGE = b"R u there?"


class Client(threading.Thread):
    def __init__(self, port=15000):
        super(Client, self).__init__()
        self.port = port
        self.conn_count = 0
        self.timeout = 5
        self.aes_key = None
        self.connections = []

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
                    response_data = json.loads(response.decode())
                    room_id = response_data.get("room_id")
                    hosts = response_data.get("hosts", [])
                    if room_id:
                        active_rooms.setdefault(room_id, []).extend(hosts)
                    # print(f"Received response from {addr[0]} on port {self.port}: {response.decode()}") #
            except socket.timeout:
                for room_id in active_rooms:
                    active_rooms[room_id] = list(set(active_rooms[room_id]))  # Delete duplicates

                if verbose:
                    if active_rooms:
                        print("[*] Active rooms have been found: ", active_rooms)
                    else:
                        print("[*] No active rooms found.")
                return active_rooms

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
        self.username = username.lstrip()
        # print(len(target_ip)) #
        # Zaimplementowac spanning tree dla len(active_rooms[room_id]) >= 5

        if not target_ip:
            print(f"[!] Room {room_id} not found.")
            return

        if len(target_ip) < 5:
            for ip in target_ip:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    client_socket.connect((ip, self.port))
                    print(f"Connected to {ip}:{self.port}")
                    self.connections.append(client_socket)
                    # self.exchange_keys(client)
                    threading.Thread(target=self.receive_message, args=(client_socket,)).start()
                    threading.Thread(target=self.send_message, args=(client_socket, self.username)).start()
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
            message = input(f"{username}: ")
            encrypted_message = encryption.encrypt_message_with_aes(message, self.aes_key)
            packet = json.dumps({
                "message": encrypted_message,
                "username": self.username,
                "MID": "M0001:000"
            })
            client_socket.send(packet.encode("utf-8"))

    def receive_message(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                message_dict = json.loads(message)
                if message_dict["MID"] == "M0000-000":
                    public_key = encryption.receive_key(message_dict["key"])
                    self.aes_key = encryption.generate_aes_key()
                    encrypted_aes_key = encryption.encrypt_aes_key_with_rsa(self.aes_key, public_key)
                    # print(public_key, aes_key, encrypted_aes_key)
                    encryption.send_aes_key(client_socket, encrypted_aes_key)
                elif message_dict["MID"] != "M0000-000":
                    sys.stdout.write("\033[2K")
                    sys.stdout.write("\r")
                    sys.stdout.flush()

                    print(message_dict["username"] + ": " + message_dict["message"])

                    sys.stdout.write(f"{self.username}: ")  # Redisplay the prompt
                    sys.stdout.flush()
                    self.forward_message(message, client_socket)
                else:
                    break
            except Exception as e:
                print(f"[!] An error occurred: {e}")
                self.connections.remove(client_socket)
                client_socket.close()

    def forward_message(self, message, sender_socket):
        for connection in self.connections:
            if connection != sender_socket:
                try:
                    connection.send(message)
                except:
                    self.connections.remove(connection)

# discover_nodes() #
