#!/opt/li-asterisk/tools/Python-3.6.7
from urllib import parse
from library.shared.ari.server import Server
from http.server import BaseHTTPRequestHandler
from os.path import exists
from os.path import join
import base64
from modules.asterisk.register.register import Register
from library.shared.ari import uris
import json

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
register = Register()

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
        try:
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
            id_interception = None
            uri = None
            parsed_path = (parse.urlparse(self.path)).path
            self.log.debug("Server::do_GET: " + str(parsed_path))
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
            
            elif(parsed_path == uris.ADD_INTERCEPTION.format("","")):
                self.log.debug("Server::do_GET: ADD_INTERCEPTION")
                if("?" in self.path):
                    for key,value in dict(parse.parse_qsl(self.path.split("?")[1], True)).items():
                        self.log.debug("Server::do_GET: ADD_INTERCEPTION, " + str(key) + ", " + str(value))
                        if(key == 'target'):
                            target = value
                            (id_interception,uri) = register.add_interception(target)
                            msg = {"id": id_interception,"uri": uri}
                        else:
                            msg = {"error": "Key is not valid!"}
                        
                        self.log.debug("Server::do_GET: msg: " + str(msg))
                        msg_json = (json.dumps(msg)).encode('utf-8')
                        self.send_response(200)
                        self.send_header('Content-type','application/json')
                        self.send_header('Content-Length',str(len(msg_json)))
                        self.end_headers()
                        self.wfile.write(msg_json)
                        return


            elif(parsed_path == uris.INACTIVE_INTERCEPTION.format("","")):
                self.log.debug("Server::do_GET: INACTIVE_INTERCEPTION")
                if("?" in self.path):
                    for key,value in dict(parse.parse_qsl(self.path.split("?")[1], True)).items():
                        self.log.debug("Server::do_GET: INACTIVE_INTERCEPTION, " + str(key) + ", " + str(value))
                        if(key == 'interception'):
                            id_interception = int(value)
                            if(register.inactive_interception(id_interception)):
                                msg = "OK"
                        else:
                            msg = "Key is not valid!"
            else:
                msg = "Path not exists!"
                self.log.warning("Server::do_GET: Alert: " + str(msg))
        
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            self.wfile.write(msg.encode('utf-8'))
        
        except Exception as error:
            self.log.debug("Server::do_GET: error: " + str(error))

    def auth(self,credentials:str):
        credentials_split = credentials.split(" ")
        credentials_decode = (base64.b64decode(credentials_split[1])).decode()
        (user,passwd) = credentials_decode.split(":")
        if(user == auth.user and passwd == auth.password):
            return True
        
        return False


class Server(Server):
    
    def __init__(self, address, port, path_pcap, uri, user, password, db_name, log):
        self.log = log
        pcap.set(path_pcap,uri)
        auth.set(user, password)
        register.set(log,db_name)
        super().__init__(address,port,Handler,log)
        
    
    def run(self):
        try:
            super().run()
        except Exception as error:
            self.log.error("Server::run: " + str(error))
        