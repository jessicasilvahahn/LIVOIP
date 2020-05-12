#!/opt/li-asterisk/tools/Python-3.6.7
from urllib import parse
from library.shared.ari.server import Server
from http.server import BaseHTTPRequestHandler
from os.path import exists
from os.path import join
import base64

class Pcap():

    def __init__(self):
        self.path = None
        self.uri = None

    def set(self, path, uri):
        self.path = path
        self.uri = uri

class Auth():
    def __init__(self):
        self.user = None
        self.password = None
    
    def set(self,user, password):
        self.user = user
        self.password = password

pcap = Pcap()
auth  = Auth()

class Handler(BaseHTTPRequestHandler):

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Access to the staging site", charset="UTF-8"\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def HEADER(self,file):
        self.send_response(200)
        self.send_header('Content-Disposition', 'attachment; filename=\"' + file + "\"")
        self.send_header('Content-type','application/octet-stream')
        self.end_headers()
        return
    
    def do_GET(self):
        if(self.headers['Authorization'] == None):
            self.do_AUTHHEAD()
            self.wfile.write(bytes('no auth header received', 'UTF-8'))
            return

        credentials = self.headers.get('Authorization')
        is_auth = self.auth(credentials)
        if(not is_auth):
            self.log.warnning("Server::do_GET: Alert: Not auth! , login: " + str(credentials))
            self.send_response(200)
            self.end_headers()
            self.wfile.write('Not auth!'.encode('utf-8'))
            return
        
        msg = ""
        parsed_path = (parse.urlparse(self.path)).path
        self.log.debug("Server::do_GET:" + str(parsed_path))
        if(parsed_path == pcap.uri):
            if("?" in self.path):
                for key,value in dict(parse.parse_qsl(self.path.split("?")[1], True)).items():
                    print(str(key) + str(value))
                    if(key == 'file'):
                        name = join(pcap.path,value)
                        if(exists(name)):
                            self.HEADER(value)
                            with open(name, 'rb') as reader:
                                bytes_line = reader.read()
                                while(bytes_line):
                                    self.wfile.write(bytes_line)
                                    bytes_line = reader.read()
                            return
                        else:
                            msg = "File not exists!"
                            
        else:
            msg = "Path not exists!"
            self.log.warning("Server::do_GET: Alert: " + str(msg))
    
        self.wfile.write(msg.encode('utf-8'))

    def auth(self,credentials:str):
        print(auth.user,auth.password)
        credentials_split = credentials.split(" ")
        credentials_decode = (base64.b64decode(credentials_split[1])).decode()
        (user,passwd) = credentials_decode.split(":")
        if(user == auth.user and passwd == auth.password):
            return True
        
        return False


class Server(Server):
    
    def __init__(self, address, port, path_pcap, uri, user, password, log):
        self.log = log
        pcap.set(path_pcap,uri)
        auth.set(user, password)
        super().__init__(address,port,Handler,log)
    
    def run(self):
        try:
            super().run()
        except Exception as error:
            self.log.error("Server::run: " + str(error))
        