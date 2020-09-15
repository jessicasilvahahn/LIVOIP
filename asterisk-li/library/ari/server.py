#!/opt/li-asterisk/tools/Python-3.6.7
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from enum import Enum
from ssl import SSLContext

class MimeType(Enum):
    
    TEXT = 'text/plain'
    HTML = 'text/html'
    AUDIO = 'audio/*'


class Server(HTTPServer):
    def __init__(self, address, port, handler,log):
        super().__init__((address, port), handler)
        self.RequestHandlerClass.log = log
        self.RequestHandlerClass.user = None
        self.RequestHandlerClass.password = None

    def run(self):
        super().serve_forever()

class HTTPS(HTTPServer):
   #https://docs.python.org/3.0/library/ssl.html#ssl-certificates
    def __init__(self, address, port, handler,log):
        super().__init__((address, port), handler)
        self.context = SSLContext()
        self.RequestHandlerClass.log = log
        self.RequestHandlerClass.user = None
        self.RequestHandlerClass.password = None

    def run(self):
        self.context.load_cert_chain("/opt/li-asterisk/certs/cert_and_key.pem",password="asterisk")
        self.socket = self.context.wrap_socket(self.socket, server_side=True)
        self.serve_forever()
