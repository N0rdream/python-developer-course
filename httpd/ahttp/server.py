import asyncio
import socket
import concurrent.futures
from .request_handler import AsyncRequestHandler
from multiprocessing import Process


TIMEOUT_RECV = 10


class AsyncServer:

    def __init__(self, root, sock, loop):
        self.request_handler = AsyncRequestHandler(root)
        self.loop = loop
        self.sock = sock

    async def connect(self):
        while True:
            client_socket, _ = await self.loop.sock_accept(self.sock)
            handler = self.handle(client_socket)
            self.loop.create_task(handler)

    async def sock_recvall(self, sock, size):
        tmp = bytearray()
        while True:
            try:
                chunk = await asyncio.wait_for(self.loop.sock_recv(sock, size), TIMEOUT_RECV)
            except concurrent.futures.TimeoutError:
                break
            if not chunk:
                break
            tmp.extend(chunk)
            if b'\r\n\r\n' in tmp:
                break
        return tmp

    async def handle(self, client_socket):
        request = await self.sock_recvall(client_socket, 1024)
        response = self.request_handler.get_response(request)
        await self.loop.sock_sendall(client_socket, response)
        client_socket.close()


def create_socket(addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.listen()
    sock.setblocking(False)
    return sock


def run_server(root, sock):
    loop = asyncio.get_event_loop()
    serv = AsyncServer(root, sock, loop)
    loop.create_task(serv.connect())
    loop.run_forever()


def serve_forever(root, sock, workers):
    for i in range(workers):
        p = Process(target=run_server, args=(root, sock))
        p.start()
