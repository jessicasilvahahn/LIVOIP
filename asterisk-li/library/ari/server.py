#!/opt/li-asterisk/tools/Python-3.6.7
from http.server import HTTPServer
from enum import Enum

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