#!/opt/li-asterisk/tools/Python-3.6.7
import pickle
import socket

class Client():
    def __init__(self, host, port, log):
        self.log = log
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connected = False
    
    def connect(self):
        self.log.info("Trying connect to server: " + self.host + ":" + str(self.port))
        try:
            if(not self.__connected):
                self.client.connect((self.host, self.port))
                self.__connected = True
        except Exception as error:
            self.log.error(str(error))

    def send_message(self, msg):
        try:
            self.connect()
            data = pickle.dumps(msg)
            self.log.info("Client::send_message: Trying send: " + str(data))
            self.client.sendall(data)
        except Exception as error:
            self.log.error(str(error))
    
    def close(self):
        self.log.info("Trying close socket")
        try:
            self.client.close()
        except Exception as error:
            self.log.error(str(error))

class Server():
    def __init__(self, host, port, buffer_size, log):
        self.log = log
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer_size = buffer_size
    
    def start(self):
        self.log.info("Trying bind socket: " + str(self.host) + " " + str(self.port))
        try:
            self.server.bind((self.host,self.port))
            self.server.listen(1)
        except Exception as error:
            self.log.error(str(error))
    
    
    def receive_msg(self):
        self.log.info("Server::receive_msg: Waiting message...")
        current_msg = ""
        msg = None
        try:
            (conn, client) = self.server.accept()
            self.log.info("Server::receive_msg: client " + str(client) + " connected")
            while(True):
                current_msg = conn.recv(self.buffer_size)
                if(current_msg):
                    current_msg = pickle.loads(current_msg)
                    self.log.info("Server::receive_msg: client " + str(client) + " msg " + str(current_msg))
                if(current_msg == "ACK"):
                    self.log.info("Server::receive_msg: client " + str(client) + " send ACK")
                    break
                elif(current_msg):
                    msg = current_msg
                else:
                    break
            self.log.info("Server::receive_msg: Connection wiht client " + str(client) + " finished")
            conn.close()
            return msg
        except Exception as error:
            self.log.error(str(error))
        

        

    