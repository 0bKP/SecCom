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
parser.add_argument("-s", "--stash", help="[Server option] Hide room from discovery", action="store_false")

args = parser.parse_args()

client = client.Client()
client.start()

if args.discover:
    client.discover_nodes()

if not args.username:
    if not args.discover and args.stash:
        USERNAME = input("Username: ")
else: USERNAME = args.username

if args.identity:
    ROOM_ID = args.identity
    client.connect_to_room(ROOM_ID, USERNAME)


if args.create:
    server = server.Server(listen_port=15000, room_id=args.create.encode(), stash=args.stash, username=USERNAME)
    server.start()
