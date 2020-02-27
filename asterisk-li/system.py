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
from li_asterisk import RegisterLawfulInterception
import time
import threading

class System():
    
    def __init__(self):
        self.config = None
        self.service_args = None
        self.log_handler = None
        self.thread_count = None
        self.stop = False
        self.sleep = 30
        self.li_queue = queue.Queue()
    
    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_put = executor.submit(self.put_li)
            future_get = executor.submit(self.get_li)
        
    def put_li(self):
        #pegar do banco
        while(not self.stop):
            li_database = []
            if(lis_database):
                for li in li_database:
                    self.li_queue.put(li)
            time.sleep(self.sleep)

    def get_li(self):
        while(not self.stop):
            li = None
            li_thread = None
            li = self.li_queue.get()
            li_thread = threading.Thread(target=li.run)
            li_thread.start()


    def start(self, preserved_file = None):
        if self.service_args.daemon:
            with daemon.DaemonContext(pidfile= PIDLockFile(self.service_args.daemon),files_preserve=[self.log_handler.stream, preserved_file]):
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

        self.log_handler = logging.handlers.RotatingFileHandler(file, maxBytes=self.config.getint('log', 'size'),
                                                       backupCount=self.config.getint('log', 'backups'))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: '\
                                      '%(message)s')
        self.log_handler.setFormatter(formatter)
        li_asterisk = logging.getLogger('li_asterisk')
        li_asterisk.setLevel(LEVELS.get(self.config.get('log', 'level'), logging.NOTSET))
        li_asterisk.addHandler(self.log_handler)

