#!/opt/li-asterisk/tools/Python-3.6.7
import logging
import argparse
import configparser
import logging
import logging.handlers
import sys
import signal
import daemon
from daemon.pidfile import PIDLockFile
from modules.adm_function.server.server import Server

class System():
    
    def __init__(self):
        self.config = None
        self.service_args = None
        self.log_handler = None
        self.stop = False
        self.mode = None
        self.parameters = {}
        self.server = None

    def run(self):
        self.server = Server(self.parameters['address'],int(self.parameters['port']),self.parameters['database'],self.parameters['host_asterisk'],self.parameters['port_asterisk'],self.parameters['user_asterisk'],self.parameters['password_asterisk'],self.parameters['timeout'],self.log)
        self.server.run() 

    def start(self, preserved_file = None):
        if self.service_args.daemon:
            with daemon.DaemonContext(pidfile=PIDLockFile(self.service_args.daemon),files_preserve=[self.log_handler.stream, preserved_file]):
                self.run()
        else:
            self.run()

    def setup(self):
        parser = argparse.ArgumentParser(description='Allowed options')
        parser.add_argument('-c', '--config',
                            help='path to configuration file',
                            required=True)
        parser.add_argument('-d', '--daemon',
                            help='path to pid file while running as a daemon',
                            required=False)

        self.service_args = parser.parse_args()
        self.config = configparser.ConfigParser()
        self.config.read(self.service_args.config)
        
        LEVELS = {'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}

        self.mode = self.config.get('general','mode')
        log_name = self.config.get('log', 'name')

        self.parameters = {'address': self.config.get('general','address'),
                            'port': self.config.get('general','port'),
                            'database': self.config.get('general','database'),
                            'host_asterisk': self.config.get('asterisk','host'),
                            'port_asterisk': self.config.getint('asterisk','port'),
                            'user_asterisk': self.config.get('asterisk','user'),
                            'password_asterisk': self.config.get('asterisk','password'),
                            'timeout': self.config.getint('asterisk','timeout')}
                            
        self.log_handler = logging.handlers.RotatingFileHandler(log_name, maxBytes=self.config.getint('log', 'size'),
                                                       backupCount=self.config.getint('log', 'backups'))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: '\
                                      '%(message)s')
        self.log_handler.setFormatter(formatter)
        self.log = logging.getLogger(log_name)
        self.log.setLevel(LEVELS.get(self.config.get('log', 'level'), logging.NOTSET))
        self.log.addHandler(self.log_handler)

        

if __name__ == "__main__":
    manager = System()
    manager.setup()
    manager.start()
