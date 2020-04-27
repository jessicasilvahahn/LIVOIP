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
from modules.asterisk.ali import Ali
from modules.asterisk.iri.iri import Iri
from modules.asterisk.cc.cc import Record
class System():
    
    def __init__(self):
        self.config = None
        self.service_args = None
        self.log_handler = None
        self.stop = False
        self.mode = None
        self.iri = None
        self.cc = None
        self.hi1 = None
        self.ali = None
        self.parameters = {}

    def run(self):
        if(self.mode == 'ali'):
            self.ali = Ali(self.parameters['database'], self.parameters['sleep'], self.log)
            self.ali.start(self.parameters['iri_host'],self.parameters['iri_port'], self.parameters['cc_host'],self.parameters['cc_port'])
        
        elif(self.mode == 'iri'):
            self.iri = Iri(self.parameters['interface'],self.parameters['protocol'],self.parameters['sip'], self.parameters['pcap'], self.parameters['host'], self.parameters['port'], self.parameters['buffer'], self.parameters['sleep'], self.log)
            self.iri.start()

        elif(self.mode == 'cc'):
            self.cc = Record(self.parameters['host'], self.parameters['port'], self.parameters['buffer'], self.parameters['ami_server'], self.parameters['ami_user'], self.parameters['ami_password'], self.parameters['sleep'], self.log)
            self.cc.start()
        
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
        iri_host = self.config.get('iri','host')
        iri_port = self.config.getint('iri','port')

        cc_host = self.config.get('cc','host')
        cc_port = self.config.getint('cc','port')
        log_name = None

        if(self.mode == 'ali'):
            log_name = self.config.get('ali','log_name')
            self.parameters = {'sleep': self.config.getint('ali','sleep_interval'), 
            'log': self.config.get('ali','log_name'), 
            'database': self.config.get('ali','database'),
            'iri_host': self.config.get('ali','host'),
            'iri_port': iri_port,
            'cc_host': self.config.get('ali','host'),
            'cc_port': cc_port} 
        
        elif(self.mode == 'iri'):
            log_name = self.config.get('iri','log_name')
            self.parameters = {'host':iri_host,
            'port': iri_port,
            'interface': self.config.get('iri','interface'),
            'protocol': self.config.get('iri','protocol'),
            'sip' : self.config.getint('iri','sip_port'),
            'pcap': self.config.get('iri','path_pcap'),
            'buffer': self.config.getint('iri','buffer_size'),
            'sleep': self.config.getint('iri','sleep_interval')}

        elif(self.mode == 'cc'):
            log_name = self.config.get('cc','log_name')
            self.parameters = {'host':cc_host,
            'port': cc_port,
            'buffer': self.config.getint('cc','buffer_size'),
            'ami_server': self.config.get('cc','ami_server'),
            'ami_user': self.config.get('cc','ami_user'),
            'ami_password': self.config.get('cc','ami_password'),
            'sleep': self.config.getint('cc','sleep_interval')}

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
