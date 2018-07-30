import socket
import asyncio
from .request_handler import AsyncRequestHandler


class AsyncServer:

    def __init__(self, host, port, root):
        self.host = host
        self.port = port
        self.handler = AsyncRequestHandler(root)
        self.loop = asyncio.get_event_loop()

    async def connect(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        server_socket.setblocking(False)

        while True:
            client_socket, _ = await self.loop.sock_accept(server_socket)
            handler = self.client_handler(client_socket)
            self.loop.create_task(handler)

    async def client_handler(self, client_socket):
        request = await self.loop.sock_recv(client_socket, 4096)
        response = await self.loop.create_task(self.handler.get_response(request))
        await self.loop.sock_sendall(client_socket, response)
        client_socket.close()

    def run(self):
        self.loop.create_task(self.connect())
        self.loop.run_forever()
        self.loop.close()
