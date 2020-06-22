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
from modules.adm_function.adm_function import Adm

class System():
    
    def __init__(self):
        self.config = None
        self.service_args = None
        self.log_handler = None
        self.stop = False
        self.mode = None
        self.parameters = {}

    def run(self):
        stop = False
        adm = Adm(self.parameters['host'],self.parameters['port'],self.parameters['user'],self.parameters['password'],self.parameters['timeout'],self.parameters['database'],self.log)
        while(not stop):
            if(self.mode == 'add'):
                adm.add_interception()
            elif(self.mode == 'rm'):
                adm.inactivate_interception()

            stop = input("Continuar cadastro (y or n) \n")
            if(stop == 'y'):
                stop = False
            elif(stop == 'n'):
                stop = True
            else:
                stop = input("Digite a opcao correta: Continuar cadastro (y or n) \n")    

    def start(self, preserved_file = None):
        if self.service_args.daemon:
            with daemon.DaemonContext(pidfile=PIDLockFile(self.service_args.daemon),files_preserve=[self.log_handler.stream, preserved_file]):
                self.run()
        else:
            self.run()

    def stop(self):
        if(self.ali):
            self.ali.stop()

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

        self.mode = self.config.get('mode','type')
        log_name = self.config.get('log', 'name')

        self.parameters = {'host': self.config.get('general','host'),
                            'port': self.config.get('general','port'),
                            'user': self.config.get('general','user'),
                            'password': self.config.get('general','password'),
                            'timeout': self.config.getint('general','timeout'),
                            'database': self.config.get('general','database')}
        
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
