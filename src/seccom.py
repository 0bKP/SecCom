import argparse
import communication


parser = argparse.ArgumentParser(
    prog="SecCom",
    description='SecCom is a P2P, terminal-based, end-to-end encrypted secure chat.')
parser.add_argument("-d", "--discover", help="Discover active rooms", action="store_true")
parser.add_argument("-i", "--identity", help="Room ID you want to join", type=str)
parser.add_argument("-u", "--username", help="Username", type=str)

args = parser.parse_args()

ROOM_ID = args.i

if args.discover:
    communication.discover_nodes()

if args.username:
    USERNAME = args.username