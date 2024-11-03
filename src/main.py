import server

class SecCom():
    def __init__(self):
        self.verbose = False
        self.port = 12345
        self.id_method = 0
        self.peerIP = 0

        self.seccomserv = server.Server()

