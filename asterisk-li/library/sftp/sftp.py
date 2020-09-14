#!/opt/li-asterisk/tools/Python-3.6.7

import paramiko

class Sftp():
    def __init__(self, log, ip, port, user, password):
        self.log = log
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.transport = None
        self.sftp = None

    def setup(self):
        self.log.info("Sftp::setup")
        try:
            self.transport = paramiko.Transport((self.ip, self.port))
        except Exception as error:
            self.log.error("Sftp::setup: Error: " + str(error))
        

    def connect(self):
        self.log.debug("Sftp::connect: Trying connect " + str(self.ip) + ':' + str(self.port))
        try:
            self.transport.connect(username=self.user, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except Exception as error:
            self.log.error("Sftp::connect: Error: " + str(error))
        

    def send_file(self, src, dest):
        self.log.info("Sftp::send_file: Trying send file " + src + "to " + dest)
        try:
            self.sftp.put(src, dest)
        except Exception as error:
            self.log.error("Sftp::send_file: Error: " + str(error))
       
    def create_remote_dir(self, dir):
        self.log.info("Sftp::create_remote_dir: Trying create remote dir " + dir)
        try:
            self.sftp.chdir(dir)
        except IOError:
            self.sftp.mkdir(dir)
            self.sftp.chdir(dir)
    
    def close(self):
        self.log.info("Sftp::close")
        try:
            self.sftp.close()
            self.sftp.transport.close()
        except Exception as error:
            self.log.error("Sftp::close: Error: " + str(error))
        


    
        




    