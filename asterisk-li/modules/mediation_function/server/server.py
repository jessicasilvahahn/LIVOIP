#!/opt/li-asterisk/tools/Python-3.6.7
from urllib import parse
from library.shared.ari.server import Server
from library.shared.ari.server import MimeType
from http.server import BaseHTTPRequestHandler
from os.path import exists
from os.path import join
from library.shared.database.database import Database
import base64

class UriEvidences():
    def __init__(self):
        self.path = None

    def set(self,path):
        self.path = path


database = Database()
uri_evidences = UriEvidences()


class Handler(BaseHTTPRequestHandler):

    def HEADER(self,mime_type,file=None):
        content_type = MimeType.HTML.value
        self.send_response(200)
        if(file):
            self.send_header('Content-Disposition', 'attachment; filename=' + file)

        if(mime_type == MimeType.TEXT):
            content_type = MimeType.TEXT.value
        elif(mime_type == MimeType.AUDIO):
            content_type = MimeType.AUDIO.value
        
        self.send_header('Content-type',content_type)
        self.end_headers()
        return

    def login(self,target,file):
        self.HEADER(MimeType.HTML)
        form = '''<html><form action="" method="GET">
            User Name :
            <input type="text" name="username" id="username" placeholder="Enter User Name"> <br>
            Password  :
            <input type="password" name="password" id="password" placeholder="Enter Password"> <br>
            Target:
            <input type="text" name="target" id="target" value="''' + str(target) + '''"> <br>
            File:
            <input type="text" name="file" id="file" value="''' + str(file) + '''"> <br>

            <button type="submit" id="submit">Sign in</button>
        </form></html>'''

        self.wfile.write(form.encode('utf-8'))

    def do_GET(self):
        user = None
        passowrd = None
        cpf = None
        file = None
        mime_type = MimeType.TEXT
        query_string = parse.urlparse(self.path).query
        fields = parse.parse_qs(query_string)
        self.log.info("Server::do_GET: fields: " + str(fields))
        try:
            cpf = fields.get('target')[0]
            file = fields.get('file')[0]
            user = fields.get('username')[0]
            password = fields.get('password')[0]
            if(user and password):
                auth = self.auth(user,password)
                if(not auth):
                    self.log.debug("Server::do_GET: Not authorized! , user: " + str(user) + " and password: " + str(passowrd))
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write('Not authorized!'.encode('utf-8'))
                    return

                path = join(uri_evidences.path + '/' + str(cpf), file)
                is_pcap = file.split(".")
                if(is_pcap[0] == "wav"):
                    mime_type = MimeType.AUDIO

                self.get_file(path,mime_type,file)
                
            else:
                self.login(cpf)
        except Exception as error:
            self.log.warning("Server::do_GET: Alert: " + str(error))
            self.login(cpf,file)

    def auth(self,user:str,password:str):
        auth = False
        database.connect()
        query = "SELECT id from lea where user=\'" + user + "\' and password=\'" + password + "\'"
        (cursor,conn) = database.execute_query(query)
        lea_exists = cursor.fetchone()
        database.disconnect()
        if(lea_exists):
            auth = True
        
        return auth
    
    def get_file(self,path,mime_type,file):
        self.log.debug("Server::get_file: Trying get file: " + str(path))
        if(exists(path)):
            self.HEADER(mime_type,file)
            with open(path, 'rb') as reader:
                bytes_line = reader.read()
                while(bytes_line):
                    self.wfile.write(bytes_line)
                    bytes_line = reader.read()
        return


class Server(Server):
    
    def __init__(self, address, port, db_name, path, log):
        self.log = log
        uri_evidences.set(path)
        database.set_attributes(db_name,log)
        super().__init__(address,port,Handler,log)

    def run(self):
        try:
            super().run()
        except Exception as error:
            self.log.error("IriServer::run: " + str(error))
        