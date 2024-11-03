import threading
import socket

class Server(threading.Thread):
    def __init__(self):
        self.host = ""
        self.port = 5000
        self.connected = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()

    def handle_connections(self):
        conn, addr = self.socket.accept()

    def run(self): pass