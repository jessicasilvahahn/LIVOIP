#!/opt/li-asterisk/tools/Python-3.6.7
from http.server import BaseHTTPRequestHandler
#from modules.asterisk.database.database import Database
from server import Server

class Hi1(BaseHTTPRequestHandler):
    
    def set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


    def do_GET(self):
        #cada resquest vai ter um objeto de banco
        self.set_headers()
        self.send_response(200)
        self.wfile.write("teste".encode('utf-8'))


class teste(Hi1):
    def __init__(self):
        pass


server_teste = Server('',8080,teste)
server_teste.run()
    