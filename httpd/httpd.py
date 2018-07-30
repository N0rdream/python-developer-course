import argparse
from ahttp.server import AsyncServer


def get_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root', type=str, default='', help='Document root')
    parser.add_argument('-a', '--addr', type=str, default='0.0.0.0', help='Server address')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Server port')
    return parser.parse_args()


if __name__ == '__main__':
    cmd_args = get_cmd_args()
    s = AsyncServer(cmd_args.addr, cmd_args.port, cmd_args.root)
    s.run()
