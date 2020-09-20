from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
from ssl import SSLContext
from io import BytesIO
import json
import base64

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        credentials = self.headers.get('Authorization')
        credentials_split = credentials.split(" ")
        credentials_decode = (base64.b64decode(credentials_split[1])).decode()
        print(str(credentials_decode))
        content_length = int(self.headers['Content-Length'])
        print(self.headers['Content-Type'])
        body = self.rfile.read(content_length)
        print(body)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        print(json.loads(body.decode())['target'])
        response.write(body)
        self.wfile.write(response.getvalue())


httpd = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
print(httpd)
context = SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("certificados/teste.pem",password="2604")
httpd.socket = context.wrap_socket(httpd.socket,server_side=True)
httpd.serve_forever()