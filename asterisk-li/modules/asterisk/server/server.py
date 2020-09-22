#!/opt/li-asterisk/tools/Python-3.6.7
from urllib import parse
from library.ari.server import HTTPS
from library.ari.server import BaseHTTPRequestHandler
from os.path import exists
from os.path import join
import base64
from modules.asterisk.register.register import Register
from library.ari import uris
import json
from library.database.database import Database
from urllib import parse
from urllib.parse import parse_qs

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
database = Database(None,None)

class Handler(BaseHTTPRequestHandler):

    def get_files(self, table, interception_id, call_id):
        self.log.debug("Server::get_files: " + str(table))
        file = None
        result = None
        proxy = False
        
        query = "SELECT " + str(table) + " from " + str(table) + " where call_id=" + str(call_id) + " and interception_id=" + interception_id

        if(table == "iri"):
            proxy = True
            query = "SELECT " + str(table) + ",proxy from " + str(table) + " where call_id=" + str(call_id) + " and interception_id=" + interception_id

        database.connect()
        (cursor,conn) = self.database.execute_query(query)
        if(cursor):
            result = cursor.fetchone()
            if(result):
                name_file = result[0]
                file = {"file": name_file}
                if(proxy):
                    file = {"file": name_file, "proxy": result[1]}

                
        
        return file


    def format_json(self, msg):
        self.log.debug("Server::format_json: " + str(msg))
        msg_json = (json.dumps(msg)).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Content-Length',str(len(msg_json)))
        self.end_headers()
        return msg_json

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
                self.wfile.write(bytes('No auth header received', 'UTF-8'))
                return

            credentials = self.headers.get('Authorization')
            is_auth = self.auth(credentials)
            if(not is_auth):
                self.log.info("Server::do_GET: Alert: Not auth! , login: " + str(credentials))
                self.send_response(200)
                self.end_headers()
                self.wfile.write('You are not authorized to enter this application!'.encode('utf-8'))
                return
            parsed_path = (parse.urlparse(self.path)).path
            self.log.debug("Server::do_GET: " + str(parsed_path))
            if(parsed_path == pcap.uri):
                parameters = parse_qs(parse(self.path).query)
                self.log.debug("Server::do_GET: parameters" + str(parameters))
                name_file = join(pcap.path,parameters["file"])
                if(exists(name_file)):
                    self.HEADER(name_file)
                    with open(name_file, 'rb') as reader:
                        bytes_line = reader.read()
                        while(bytes_line):
                            self.wfile.write(bytes_line)
                            bytes_line = reader.read()
                    return
                else:
                    msg = "File not exists!"
            else:
                msg = "URL not exists!"

            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            self.wfile.write(msg.encode('utf-8'))

        except Exception as error:
            self.log.debug("Server::do_GET: error: " + str(error))

    
    def do_POST(self):
        try:
            if(self.headers['Authorization'] == None):
                self.do_AUTHHEAD()
                self.wfile.write(bytes('No auth header received', 'UTF-8'))
                return

            credentials = self.headers.get('Authorization')
            is_auth = self.auth(credentials)
            if(not is_auth):
                self.log.info("Server::do_POST: Alert: Not auth! , login: " + str(credentials))
                self.send_response(200)
                self.end_headers()
                self.wfile.write('You are not authorized to enter this application!'.encode('utf-8'))
                return
            
            msg = ""
            id_interception = None
            uri = None
            body = None
            parsed_path = (parse.urlparse(self.path)).path
            self.log.debug("Server::do_POST: " + str(parsed_path))
            if(parsed_path == uris.ADD_INTERCEPTION.format("")):
                target = None
                self.log.debug("Server::do_POST: ADD_INTERCEPTION")
                if(self.headers['Content-Type'] == 'application/json'):
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length)
                    target = json.loads(body.decode())["target"]
                    (id_interception,cpf) = register.add_interception(target)
                    msg = {"id": id_interception,"cpf": cpf}
                        
                else:
                    msg = {"error": "Header content-type not valid!"}
                        
                self.log.debug("Server::do_POST: msg: " + str(msg))
                msg_json = self.format_json(msg)
                self.log.debug("Server::do_POST: json: " + str(msg_json))
                self.wfile.write(msg_json)
                return


            elif(parsed_path == uris.INACTIVE_INTERCEPTION.format("")):
                self.log.debug("Server::do_POST: INACTIVE_INTERCEPTION")
                if(self.headers['Content-Type'] == 'application/json'):
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length)
                    id_interception = int(json.loads(body.decode())["id_interception"])
                    if(register.inactive_interception(id_interception)):
                        msg = "OK"
                    else:
                        msg = "Problem to delete interception!"
            
            elif(parsed_path == uris.GET_IRI.format("")):
                self.log.debug("Server::do_POST::GET_IRI")
                file = None
                call_id = None
                interception_id = None
                if(self.headers['Content-Type'] == 'application/json'):
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length)
                    call_id = json.loads(body.decode())["call_id"]
                    interception_id = json.loads(body.decode())["interception_id"]
                    file = self.get_files("iri", interception_id, call_id)
                
                msg_json = self.format_json(file)
                self.log.debug("Server::do_POST::GET_IRI: json" + str(msg_json))
                self.wfile.write(msg_json)

            elif(parsed_path == uris.GET_CC.format("")):
                self.log.debug("Server::do_POST::GET_CC")
                file = None
                call_id = None
                interception_id = None
                if(self.headers['Content-Type'] == 'application/json'):
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length)
                    call_id = json.loads(body.decode())["call_id"]
                    interception_id = json.loads(body.decode())["interception_id"]
                    file = self.get_files("cc", interception_id, call_id)
                
                msg_json = self.format_json(file)
                self.log.debug("Server::do_POST::GET_CC: json" + str(msg_json))
                self.wfile.write(msg_json)
            else:
                msg = "Path not exists!"
                self.log.info("Server::cc_name: Alert: " + str(msg))
        
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            self.wfile.write(msg.encode('utf-8'))
        
        except Exception as error:
            self.log.debug("Server::do_POST: error: " + str(error))

    def auth(self,credentials:str):
        credentials_split = credentials.split(" ")
        credentials_decode = (base64.b64decode(credentials_split[1])).decode()
        (user,passwd) = credentials_decode.split(":")
        if(user == auth.user and passwd == auth.password):
            return True
        
        return False


class Server(HTTPS):
    
    def __init__(self, address, port, path_pcap, uri, user, password, db_name, log):
        self.log = log
        pcap.set(path_pcap,uri)
        auth.set(user, password)
        register.set(log,db_name)
        database.set_attributes(db_name,log)
        super().__init__(address,port,Handler,log)
    
    def run(self):
        try:
            super().run()
        except Exception as error:
            self.log.error("Server::run: " + str(error))
        