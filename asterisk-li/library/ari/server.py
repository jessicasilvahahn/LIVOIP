#!/opt/li-asterisk/tools/Python-3.6.7
from http.server import HTTPServer
from enum import Enum
import ssl

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
   # https://docs.python.org/3.0/library/ssl.html#ssl-certificates
    def __init__(self, address, port, private_key, cert, handler,log):
        super().__init__((address, port), handler)
        self.RequestHandlerClass.log = log
        self.RequestHandlerClass.user = None
        self.RequestHandlerClass.password = None
        self.private_key = private_key
        self.cert = cert

    def run(self):
        if(self.private_key and self.cert):
            super().socket = ssl.wrap_socket(super().socket, (keyfile=self.private_key, certfile=self.cert), server_side=True)
        else:
            super().socket = ssl.wrap_socket(super().socket, certfile=self.cert, server_side=True)
 
        super().serve_forever()
