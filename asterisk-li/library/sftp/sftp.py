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
            return True
        except Exception as error:
            self.log.error("Sftp::connect: Error: " + str(error))
            return False
        

    def send_file(self, src, dest):
        self.log.info("Sftp::send_file: Trying send file " + src + " to " + dest)
        try:
            self.sftp.put(src, dest)
            return True
        except Exception as error:
            self.log.error("Sftp::send_file: Error: " + str(error))
            return False
    
    def remote_dir_exists(self, remote_path, new_dir):
        self.log.info("Sftp::remote_dir_exists: " + str(remote_path) + ", " + str(new_dir))
        remote_dirs = self.sftp.listdir(remote_path)
        self.log.debug("Sftp::remote_dir_exists: remote dirs: " + str(remote_dirs))
        if new_dir in remote_dirs:
            return True
        
        return False
    
    def create_remote_dir(self, dir):
        self.log.info("Sftp::create_remote_dir: Trying create remote dir " + dir)
        try:
            self.log.debug("Sftp::create_remote_dir: The directory " + str(dir) + " not exists!")
            self.sftp.mkdir(dir)
            return True
        except Exception as error:
            self.log.error("Sftp::create_remote_dir: Error: " + str(error))
            return False
    
    def close(self):
        self.log.info("Sftp::close")
        try:
            self.sftp.close()
        except Exception as error:
            self.log.error("Sftp::close: Error: " + str(error))
        


    
        




    