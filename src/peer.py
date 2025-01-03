import threading
import socket
import sys
import encryption
import json

DEFAULT_TIMEOUT = 5

class Peer(threading.Thread):
    def __init__(self, port=15000, username="", room_id=None):
        super(Peer, self).__init__()
        self.port = port
        self.peers = []
        self.aes_key = None
        self.rsa_private_key = None
        self.running = True
        self.username = username.lstrip()
        self.room_id = room_id
        self.timeout = DEFAULT_TIMEOUT

        self.peers.append(self.get_ip("lhost"))
        
    def run(self):
        threading.Thread(target=self.listen_for_peers).start()

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", self.port))
        server_socket.listen(5)

        while self.running:
            client_socket, client_address = server_socket.accept()
            self.handle_peer(client_socket, client_address)
        
                         
    def discover_peers(self, verbose=True):
        BROADCAST_MESSAGE = b"R u there?"
        # Function broadcasts a message in order to detect active nodes
        active_rooms = dict()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as broadcast_socket:
            broadcast_socket.settimeout(self.timeout)

            broadcast_ip = self.get_ip("broadcast")
            # print(f"BC IP: {broadcast_ip}") #
            broadcast_socket.sendto(BROADCAST_MESSAGE, (broadcast_ip, self.port))
            # print(f"Broadcast sent on port {BROADCAST_PORT}") #
            if verbose: print("[i] Locating active rooms...")

            try:
                while True:
                    response, addr = broadcast_socket.recvfrom(1024)
                    response_data = json.loads(response.decode())
                    room_id = response_data.get("room_id")
                    hosts = response_data.get("peers", [])
                    if room_id:
                        active_rooms.setdefault(room_id, []).extend(hosts)
                    #print(f"Received response from {addr[0]} on port {self.port}: {response.decode()}") #
            except socket.timeout:
                for room_id in active_rooms:
                    active_rooms[room_id] = list(set(active_rooms[room_id])) # Delete duplicates

                if verbose:
                    if active_rooms:
                        print("[*] Active rooms have been found: ", active_rooms)
                    else:
                        print("[*] No active rooms found.")
                return active_rooms

    def listen_for_peers(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as hello_socket:
            hello_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            hello_socket.bind(("", self.port))

            if self.aes_key == None:
                self.aes_key = encryption.generate_aes_key()
                
            # print(f"Listening on port {self.listen_port}...")  #
            print("[i] Server has successfully started!")

            while self.running:
                message, addr = hello_socket.recvfrom(1024)
                # print(f"Received hello from {addr[0]}: {message.decode()}")  #

                #if addr[0] not in self.hosts:
                #    self.hosts.append(addr[0])

                response_data = {
                    "room_id" : self.room_id.decode(),
                    "peers" : self.peers}
                response_json = json.dumps(response_data)
                
                hello_socket.sendto(response_json.encode(), addr)
                # print(f"Response sent to {addr[0]}")  #
        
    def get_ip(self, req):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)

        if req == "lhost":
            return ip
        elif req == "broadcast":
            octets = ip.split(".")
            octets[3] = "255"
            octets = ".".join(octets)
        
            return octets

    def connect_to_room(self, room_id):
        # x = input("connect_to_room exec") #
        active_rooms = self.discover_peers(verbose=False)
        target_ip = active_rooms[room_id]
        # print(len(target_ip)) #
        # Zaimplementowac spanning tree dla len(active_rooms[room_id]) >= 5
    

        if not target_ip:
            print(f"[!] Room {room_id} not found.")
            return

        if len(target_ip) < 5:
            #self.rsa_private_key = encryption.send_rsa_key(
            for ip in target_ip:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    client_socket.connect((ip, self.port))
                    print(f"Connected to {ip}:{self.port}")
                    self.peers.append(client_socket)
                    # Wymiana kluczy
                    self.rsa_private_key = encryption.send_rsa_key(client_socket)
                        
                    threading.Thread(target=self.receive_message, args=(client_socket,)).start()
                    threading.Thread(target=self.send_message, args=(client_socket,)).start()
                except Exception as e:
                    print(f"[!] Failed to connect to {ip}: {e}")

    def handle_peer(self, client_socket, client_address):
        print(f"[i] Connected with {client_address[0]}")
        self.peers.append(client_address[0])
        
        # Tutaj odbywa sie wymiana kluczami z nowymi wezlami
        # Przyjmij cudzy klucz publiczny RSA.
        # Zaszyfruj klucz AES
        # Wyslij
        # Wezel go odszyfrowywuje swoim prywatnym kluczem RSA
        
        #self.rsa_private_key = encryption.send_rsa_key(client_socket)
        
        threading.Thread(target=self.send_message, args=(client_socket,)).start()
        threading.Thread(target=self.receive_message, args=(client_socket,)).start()
        
    def send_message(self, connection):
        while True:
            message = input(f"{self.username}: ")
            encrypted_message = encryption.encrypt_message_with_aes(message, self.aes_key)
            packet = json.dumps({
                "message" : encrypted_message,
                "username" : self.username,
                "MID" : "M0001-000"
            })
            connection.send(packet.encode("utf-8"))

    def receive_message(self, client_socket):        
        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                message_dict = json.loads(message)
                
                if message_dict["MID"] == "M0000-000": 
                    public_key = encryption.receive_rsa_key(message_dict["key"])
                    encrypted_aes_key = encryption.encrypt_aes_key_with_rsa(self.aes_key, public_key)
                    #print(public_key, aes_key, encrypted_aes_key)
                    encryption.send_aes_key(client_socket, encrypted_aes_key)
                elif message_dict["MID"] == "M0000-001":
                    public_key = message_dict["key"]
                    self.aes_key = encryption.receive_aes_key(public_key, self.rsa_private_key)
                else:
                    sys.stdout.write("\033[2K")
                    sys.stdout.write("\r")
                    sys.stdout.flush()

                    plaintext_message = encryption.decrypt_message_with_aes(message_dict["message"], self.aes_key)
                    print(message_dict["username"] + ": " + plaintext_message)

                    sys.stdout.write(f"{self.username}: ")  # Redisplay the prompt
                    sys.stdout.flush()
                    # self.forward_message(message, client_socket)
            except Exception as e:
                print(f"[!] An error occurred: {e}")
                #self.peers.remove(client_socket)
                #client_socket.close()
