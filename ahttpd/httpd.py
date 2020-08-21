import argparse
from ahttp.server import create_socket, serve_forever


def get_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root', type=str, default='', help='Document root')
    parser.add_argument('-a', '--addr', type=str, default='0.0.0.0', help='Server address')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Server port')
    parser.add_argument('-w', '--workers', type=int, default=2, help='Number of workers')
    return parser.parse_args()


if __name__ == '__main__':

    cmd_args = get_cmd_args()
    sock = create_socket(cmd_args.addr, cmd_args.port)
    serve_forever(
        cmd_args.root,
        sock, 
        cmd_args.workers
    )
