import time
import sys
import os
import re
import mimetypes
import aiofiles
from urllib.parse import unquote
from datetime import datetime


REGEXP_REQUEST = re.compile(r'(?P<method>(GET|HEAD)) (?P<uri>.+) HTTP\/\d\.\d.+')
ALLOWED_METHODS = ['GET', 'HEAD']
MESSAGES = {
    200: 'OK',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed'
}


class AsyncRequestHandler:

    def __init__(self, document_root):
        self.document_root = document_root
        self.headers_buffer = []

    async def get_file_content(self, path):
        async with aiofiles.open(path, mode='rb') as f:
            contents = await f.read()
            return contents

    def process_uri(self, uri):
        uri = uri.lstrip("/").split('?')[0]
        return unquote(uri)

    def get_full_uri(self, uri):
        full_uri = os.path.join(self.document_root, uri)
        if full_uri.endswith('/'):
            full_uri = os.path.join(full_uri, 'index.html')
        return full_uri

    def is_uri_safe(self, uri):
        abs_uri = os.path.abspath(uri)
        if not abs_uri.startswith(os.path.abspath(os.curdir)):
            return False
        return True

    def parse_request(self, request):
        match = re.match(REGEXP_REQUEST, request)
        if match:
            return match.groupdict()['method'], self.process_uri(match.groupdict()['uri'])
        return None, None

    def get_status_line(self, status_code):
        return f'HTTP/1.1 {status_code} {MESSAGES[status_code]}\r\n'

    def get_content_type(self, uri):
        mimetype = mimetypes.guess_type(uri)[0]
        if mimetype is None:
            return 'text/html'
        return mimetype

    def get_date(self):
        dt = datetime.utcfromtimestamp(time.time())
        return dt.strftime('%a, %m %b %Y %H:%M:%S GMT')

    def get_server_name(self):
        return 'Nano HTTP Server - Python/' + sys.version.split()[0]

    def add_header(self, header_name, value):
        self.headers_buffer.append(f'{header_name}: {value}')

    def get_headers(self, content_type, content_length):
        self.add_header('Date', self.get_date())
        self.add_header('Server', self.get_server_name())
        self.add_header('Connection', 'close')
        self.add_header('Content-Type', content_type)
        self.add_header('Content-Length', content_length)
        headers = '\r\n'.join(self.headers_buffer) + '\r\n\r\n'
        self.headers_buffer = []
        return headers

    def generate_error_message(self, status_code):
        return f'<h1>{MESSAGES[status_code]}</h1>'.encode()

    def get_error_response(self, status_code):
        status_line = self.get_status_line(status_code)
        message_body = self.generate_error_message(status_code)
        headers = self.get_headers('text/html', len(message_body))
        return (status_line + headers).encode() + message_body

    async def get_response(self, request):
        method, uri = self.parse_request(request.decode())
        if method is None or uri is None:
            return self.get_error_response(400)
        if method not in ALLOWED_METHODS:
            return self.get_error_response(405)
        if not self.is_uri_safe(uri):
            return self.get_error_response(403)
        full_uri = self.get_full_uri(uri)
        try:
            message_body = await self.get_file_content(full_uri)
        except (FileNotFoundError, IsADirectoryError, NotADirectoryError):
            return self.get_error_response(404)
        headers = self.get_headers(self.get_content_type(full_uri), len(message_body))
        status_line = self.get_status_line(200)
        if method == 'HEAD':
            return (status_line + headers).encode()
        return (status_line + headers).encode() + message_body
