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
import concurrent.futures
import queue
import time
import threading
from li_asterisk import RegisterLawfulInterception
from li_asterisk import RegisterNetworkOperator
from modules.database.database import Database
from modules.events.events import Events

class System():
    
    def __init__(self):
        self.config = None
        self.service_args = None
        self.log_handler = None
        self.thread_count = None
        self.stop = False
        self.sleep = 30
        self.li_queue = queue.Queue()
        self.log = None
        self.server = None
        self.user = None
        self.passwd = None
        self.protocol = None
        self.port = None
        self.db_name = None
        self.mode = None
        self.interface_type = None

    def run(self):
        li_asterisk = None
        database = Database(self.db_name, self.log)
        leave = 'n'
        if(self.mode == "register_li"):
            #nao pode rodar como daemon
            #instanciar db
            #instanciar cadastro via interface
            while(leave == 'n'):
                li_asterisk = RegisterLawfulInterception(self.log, self.server, self.user, self.passwd, self.protocol, self.port, "", database)
                leave = li_asterisk.call_register_interface(self.interface_type)
        elif(self.mode == "start_li"):
            '''with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_put = executor.submit(self.put_li)
                future_get = executor.submit(self.get_li)'''
            self.put_li()
        elif(self.mode == "get_iri_cc"):
            pass
        elif(self.mode == "network_operator"):
            while(leave == 'n'):
                li_net_op = RegisterNetworkOperator(self.log, database)
                leave = li_net_op.register()
        else:
            print("DEBUG03")
            return
    def put_li(self):
        #pegar do banco
        '''while(not self.stop):
            li_database = []
            if(lis_database):
                for li in li_database:
                    self.li_queue.put(li)
            time.sleep(self.sleep)'''
        #teste simples
        event = Events('192.168.25.104','li','li123',self.log)
        event.setup()
        #registrando eventos
        event.event_start_call('alice')
        event.event_stop_record('alice')
        event.run()

    def get_li(self):
        while(not self.stop):
            li = None
            li_thread = None
            li = self.li_queue.get()
            li_thread = threading.Thread(target=li.run)
            li_thread.start()


    def start(self, preserved_file = None):
        if self.service_args.daemon:
            with daemon.DaemonContext(pidfile=PIDLockFile(self.service_args.daemon),files_preserve=[self.log_handler.stream, preserved_file]):
                self.run()
        else:
            self.run()

    def stop(self):
        pass

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

        self.log_handler = logging.handlers.RotatingFileHandler(self.config.get('log', 'name'), maxBytes=self.config.getint('log', 'size'),
                                                       backupCount=self.config.getint('log', 'backups'))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: '\
                                      '%(message)s')
        self.log_handler.setFormatter(formatter)
        self.log = logging.getLogger('li_asterisk')
        self.log.setLevel(LEVELS.get(self.config.get('log', 'level'), logging.NOTSET))
        self.log.addHandler(self.log_handler)

        self.server = self.config.get("asterisk", "ip")
        self.user = self.config.get("asterisk", "user")
        self.passwd = self.server = self.config.get("asterisk", "password")
        self.port = self.server = self.config.getint("li", "port")
        self.protocol = self.server = self.config.get("li", "protocol")
        self.mode = self.config.get("li", "mode")
        self.interface_type = self.server = self.config.get("li", "interface")
        self.db_name = self.server = self.config.get("database", "name")

if __name__ == "__main__":
    manager = System()
    manager.setup()
    manager.start()
