from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
from urllib import parse
class CustomHandler(BaseHTTPRequestHandler):
    ''' Main class to present webpages and authentication. '''
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Access to the staging site", charset="UTF-8"\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        ''' Present frontpage with user authentication. '''
        if self.headers['Authorization'] == None:
            self.do_AUTHHEAD()
            self.wfile.write(bytes('no auth header received', 'UTF-8'))
        else:
           parsed_path = parse.urlparse(self.path)
           print(self.path)
           for key,value in dict(parse.parse_qsl(self.path.split("?")[1], True)).items():
                print(str(key) + str(value))
           teste = self.headers.get('Authorization')
           t = teste.split(" ")
           x = base64.b64decode(t[1])
           print(x.decode())
           user,p = (x.decode()).split(":")
           print(user,p)
        '''elif self.headers['Authorization'] == 'Basic YW5vdGhlcjptZQ==':
            self.do_HEAD()
            self.wfile.write(bytes(self.headers['Authorization'], 'UTF-8'))
            self.wfile.write(bytes(' authenticated!', 'UTF-8'))
            pass'''
        

def main():
   try:
      httpd = HTTPServer(('', 8080), CustomHandler)
      print ('started httpd...')
      httpd.serve_forever()
   except KeyboardInterrupt:
      print ('^C received, shutting down server')
      httpd.socket.close()

if __name__ == '__main__':
    main()




