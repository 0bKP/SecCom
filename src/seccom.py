"""
- Dodac mechanizm czyszczenia terminala podczas otrzymywania wiadomosci
"""


import argparse
import client
import server

USERNAME = 0

parser = argparse.ArgumentParser(
    prog="SecCom",
    description='SecCom is a P2P, terminal-based, end-to-end encrypted secure chat.')
parser.add_argument("-d", "--discover", help="Discover active rooms", action="store_true")
parser.add_argument("-i", "--identity", help="Room ID you want to join", type=str)
parser.add_argument("-u", "--username", help="Username", type=str)
parser.add_argument("-c", "--create", help="Room ID you want to create", type=str)

args = parser.parse_args()

client = client.Client()
client.start()

if args.discover:
    client.discover_nodes()

if args.username:
    USERNAME = args.username

if args.identity:
    ROOM_ID = args.identity
    if USERNAME:
        client.connect_to_room(ROOM_ID, USERNAME)
    else:
        print("[!] You must enter username.")

if args.create:
    server = server.Server(listen_port=15000, room_id=args.create.encode())
    server.start()
