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
from modules.mediation_function.mediation_function import Mf
class System():
    
    def __init__(self):
        self.config = None
        self.service_args = None
        self.log_handler = None
        self.stop = False
        self.mf = None
        self.parameters = {}

    def run(self):
        self.mf = Mf((self.parameters['ami'])['server'],
            (self.parameters['ami'])['user'],
            (self.parameters['ami'])['password'],
            self.parameters['iri'],
            self.parameters['cc'],
            self.parameters['email'],
            self.parameters['host'],
            self.parameters['sleep'],
            self.parameters['db_name'],
            self.log)

        self.mf.setup()
        self.mf.run()

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

        log_name = self.config.get('general','log_name')

        iri = {'path_iri': self.config.get('iri','path'),
            'buffer': self.config.getint('iri','buffer'),
            'host': self.config.get('iri','host'),
            'port': self.config.get('iri','port'),
            'user': self.config.get('iri','user'),
            'password': self.config.get('iri','password'),
            'timeout': self.config.getint('iri','timeout')}

        
        cc = {'path_cc': self.config.get('cc','path'),
            'buffer': self.config.getint('cc','buffer'),
            'host': self.config.get('cc','host'),
            'port': self.config.get('cc','port'),
            'user': self.config.get('cc','user'),
            'password': self.config.get('cc','password'),
            'timeout': self.config.getint('cc','timeout')}

        email = {'address': self.config.get('general','email_address'),
            'passwd': self.config.get('general','email_password')}

        ami = {'server': self.config.get('general','ami_server'),
                'user': self.config.get('general','ami_user'),
                'password': self.config.get('general','ami_password')}
            
        self.parameters = {'host': self.config.get('server','external_address') + ':' + self.config.get('server','port'),
                        'sleep': self.config.getint('general','sleep_time'),
                        'db_name': self.config.get('general','database'),
                        'iri': iri,
                        'cc': cc,
                        'email': email,
                        'ami': ami}


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
