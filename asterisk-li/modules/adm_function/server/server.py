#!/opt/li-asterisk/tools/Python-3.6.7
from modules.adm_function.adm_function import Adm
from urllib import parse
from library.ari.server import Server
from library.ari.server import MimeType
from http.server import BaseHTTPRequestHandler
from os.path import exists
from os.path import join
from library.database.database import Database
import base64
import cgi
import os

database = Database()
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
            <form action="" method="get">
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
                <form action="" method="get">
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


    def login(self):
        self.HEADER(MimeType.HTML)
        form = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "https://www.w3.org/TR/html4/strict.dtd">
        <html>
            <form action="" method="get">
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

    def do_GET(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'GET'}
            )
            id = None
            lea_user = None
            lea_password = None
            lea_email = None
            cpf = None
            date = None
            self.user = form.getvalue("usuario")
            self.password = form.getvalue("senha")
            self.log.debug("Server::do_GET: user: " + str(self.user) + " password: " + str(self.password))
            if(self.user and self.password):
                auth = self.auth()
                if(not auth):
                    self.log.debug("Server::do_GET: Not authorized! , user: " + str(user) + " and password: " + str(passowrd))
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write('Not authorized!'.encode('utf-8'))
                    return

                parsed_path = (parse.urlparse(self.path)).path
                self.log.debug("Server::do_GET: " + str(parsed_path))
                if(parsed_path == '/register'):
                    self.register_li()
                elif(parsed_path == '/unregister'):
                    self.unregister_li()
                else:
                    self.log.debug("Server::do_GET: atributtes: " + str(id) + ", " + str(lea_user) + ", " + str(lea_password) + ", " + str(lea_password) + ", " + str(cpf) + ", " + str(date))
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

class Server(Server):
    def __init__(self, address, port, db_name, host_asterisk, port_asterisk, user_asterisk, password_asterisk, timeout, log):
        self.log = log
        adm.set_attributes(host_asterisk, port_asterisk, user_asterisk, password_asterisk, timeout, db_name, log)
        database.set_attributes(db_name,log)
        super().__init__(address,port,Handler,log)

    def run(self):
        try:
            super().run()
        except Exception as error:
            self.log.error("IriServer::run: " + str(error))
        