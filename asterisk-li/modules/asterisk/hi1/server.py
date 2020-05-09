#!/opt/li-asterisk/tools/Python-3.6.7
from http.server import HTTPServer

class Server(HTTPServer):
    def __init__(self, address, port, handler):
        super().__init__((address, port), handler)

    def run(self):
        super().serve_forever()