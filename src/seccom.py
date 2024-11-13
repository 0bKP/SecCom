import argparse
import communication

parser = argparse.ArgumentParser(
    prog="SecCom",
    description='SecCom is a P2P, terminal-based, end-to-end encrypted secure chat.')
parser.add_argument("-d", "--discover", help="Discover active rooms", action="store_true")
parser.add_argument("-i", help="Room ID you want to join", type=str)

args = parser.parse_args()

if args.discover:
    communication.discover_nodes()

print(args)
input()
