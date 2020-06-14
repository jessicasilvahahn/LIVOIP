#!/opt/li-asterisk/tools/Python-3.6.7
from modules.adm_function.adm_function import Adm
from urllib import parse
from library.shared.ari.server import Server
from library.shared.ari.server import MimeType
from http.server import BaseHTTPRequestHandler
from os.path import exists
from os.path import join
from library.shared.database.database import Database
import base64
import cgi
import paramiko
import os

class UriEvidences():
    def __init__(self):
        self.path = None
        self.user_sftp = None
        self.password_sftp = None
        self.host_sftp = None
        self.mode = None

    def set(self,path, host_sftp, user_sftp, password_sftp, mode):
        self.path = path
        self.user_sftp = user_sftp
        self.password_sftp = password_sftp
        self.host_sftp = host_sftp
        self.mode = mode


database = Database()
uri_evidences = UriEvidences()
adm = Adm()


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

    def unregister_li(self):
        self.HEADER(MimeType.HTML)
        form = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "https://www.w3.org/TR/html4/strict.dtd">
        <html>
            <form action="" method="post">
                <fieldset>
                <legend>Remove Lawful Interception</legend>
                <label>Id da interceptação</label><br>
                <input type="text" name="id" id="id"><br><br>
                </fieldset>
                <br>
                <button type="submit">Remove</button>
                <button type="reset">Reset</button>
            </form>
        </html>'''

        self.wfile.write(form.encode('utf-8'))

    def register_li(self):
        self.HEADER(MimeType.HTML)
        form = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
            "https://www.w3.org/TR/html4/strict.dtd">
            <html>
                <form action="" method="post">
                    <fieldset>
                    <legend>Register Lawful Interception</legend>
                    <label>Usuário</label><br>
                    <input type="text" name="usuario" id="usuario"><br><br>
                    <label>Senha</label><br>
                    <input type="password" name="senha" id="senha"><br><br>
                    <label>E-mail</label><br>
                    <input type="email" name="email">
                    
                    </fieldset>

                    <fieldset>
                        <legend>Ofício</legend> 
                        <label>CPF do alvo</label><br>
                        <input type="text" name="cpf" id="cpf"><br><br>
                        <label>Data da interceptação</label><br>
                        <input type="date" name="data" id="data"><br><br>
                    </fieldset>
                    <br>
                    <button type="submit">Register</button>
                    <button type="reset">Reset</button>
                </form>
            </html>'''

            self.wfile.write(form.encode('utf-8'))

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
    
    def login(self):
        self.HEADER(MimeType.HTML)
        form = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "https://www.w3.org/TR/html4/strict.dtd">
        <html>
            <form action="" method="post">
                <fieldset>
                <legend>Login</legend>
                <label>Usuário</label><br>
                <input type="text" name="usuario" id="usuario"><br><br>
                <label>Senha</label><br>
                <input type="password" name="senha" id="senha"><br><br>
                </fieldset>
                <br>
                <button type="submit">Login</button>
            </form>
        </html>'''

        self.wfile.write(form.encode('utf-8'))

    def do_POST(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            id = None
            lea_user = None
            lea_password = None
            lea_email = None
            cpf = None
            date = None
            self.user = form.getvalue("usuario")
            self.password = form.getvalue("senha")
            self.log.debug("Server::do_POST: user: " + str(self.user) + " password: " + str(self.password))
            if(self.user and self.password):
                auth = self.auth()
                if(not auth):
                    self.log.debug("Server::do_POST: Not authorized! , user: " + str(user) + " and password: " + str(passowrd))
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write('Not authorized!'.encode('utf-8'))
                    return

                parsed_path = (parse.urlparse(self.path)).path
                self.log.debug("Server::do_POST: " + str(parsed_path))
                if(parsed_path == '/register'):
                    self.register_li()
                elif(parsed_path == '/unregister'):
                    self.unregister_li()
                else:
                    self.log.debug("Server::do_POST: atributtes: " + str(id) + ", " + str(lea_user) + ", " + str(lea_password) + ", " + str(lea_password) + ", " + str(cpf) + ", " + str(date))
                    if(id):
                        adm.inactivate_interception(int(id))
                    elif(lea_user and lea_password and lea_email and cpf and date):
                        adm.add_interception(lea_user, lea_password, lea_email, cpf, date)
            else:
                self.login()
        except Exception as error:
            self.log.warning("Server::do_GET: Alert: " + str(error))
            self.user = None
            self.password = None
            self.login()

    def do_GET(self):
        self.user = None
        self.password = None
        cpf = None
        file = None
        query_string = parse.urlparse(self.path).query
        fields = parse.parse_qs(query_string)
        self.log.info("Server::do_GET: fields: " + str(fields))
        try:
            cpf = fields.get('target')[0]
            file = fields.get('file')[0]
            self.user = fields.get('username')[0]
            self.password = fields.get('password')[0]
            if(self.user and self.password):
                auth = self.auth()
                if(not auth):
                    self.log.debug("Server::do_GET: Not authorized! , user: " + str(user) + " and password: " + str(passowrd))
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write('Not authorized!'.encode('utf-8'))
                    return

                path = join(uri_evidences.path + '/' + str(cpf), file)
                self.log.debug("Server::do_GET: mode: " + str(uri_evidences.mode)
                if(uri_evidences.mode == 'abnt'):
                    self.get_file(path)
                else:
                    mime_type = MimeType.TEXT
                    is_pcap = file.split(".")
                    if(is_pcap[0] == "wav"):
                        mime_type = MimeType.AUDIO
                    self.get_file(path,mime_type,file)
            else:
                self.login(cpf,file)
        except Exception as error:
            self.log.warning("Server::do_GET: Alert: " + str(error))
            self.login(cpf,file)

    def auth(self):
        auth = False
        database.connect()
        query = "SELECT id from lea where user=\'" + self.user + "\' and password=\'" + self.password + "\'"
        (cursor,conn) = database.execute_query(query)
        lea_exists = cursor.fetchone()
        database.disconnect()
        if(lea_exists):
            auth = True
        
        return auth
    
    def setup_sftp(self):
        self.log.debug("Server::setup_sftp")
        transport = None
        try:
            transport = paramiko.Transport((uri_evidences.host_sftp,uri_evidences.user_sftp))
            transport.connect(None,uri_evidences.user_sftp,uri_evidences.password_sftp)
        except Exception as error:
            self.log.error("Server::do_GET: Alert: " + str(error))
        
        return transport
        
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

    def get_file(self,path:str):
        self.log.debug("Server::get_file: Trying get file: " + str(path))
        transport = None
        local_path = None
        try:
            if(exists(path)):
                transport = self.setup_sftp()
                self.log.debug("Server::get_file: setup sftp: " + str(transport))
                sftp = paramiko.SFTPClient.from_transport(transport)
                self.log.debug("Server::get_file: Trying download file")
                local_path = os.getcwd()
                self.log.debug("Server::get_file: local path: " + str(local_path))
                sftp.get(path,local_path)
                #close
                    if(sftp): 
                        sftp.close()
                    if(transport): 
                        transport.close()
        except Exception as error:
            self.log.error("Server::get_file: Error: " + str(error))

class Server(Server):
    def __init__(self, address, port, db_name, path, host_asterisk, port_asterisk, user_asterisk, password_asterisk, timeout, host_sftp, user_sftp, password_sftp, mode, log):
        self.log = log
        adm.set_attributes(host_asterisk, port_asterisk, user_asterisk, password_asterisk, timeout, db_name, log)
        uri_evidences.set(path, host_sftp, user_sftp, password_sftp, mode)
        database.set_attributes(db_name,log)
        super().__init__(address,port,Handler,log)

    def run(self):
        try:
            super().run()
        except Exception as error:
            self.log.error("IriServer::run: " + str(error))
        