#!/opt/li-asterisk/tools/Python-3.6.7
from modules.asterisk.events.events import Events
from library.socket.tcp import Server
from library.database.database import Database
import threading
from queue import Queue
import time

class Record(Events):

    def __init__(self, host, port, buffer_size, ami_server, ami_user, ami_password, sleep, db_name, log):
        self.log = log
        self.sleep = sleep
        self.interceptions = Queue()
        super().__init__(ami_server, ami_user, ami_password, self.interceptions, db_name, log)
        self.server = Server(host, port, buffer_size, log)
        self.socket = None
        self.record = None


    def run(self):
        self.log.info("Record::start_event")
        super().setup()
        #registrando eventos
        self.event_start_call()
        self.event_stop_record()
        super().run()
    
    def get_interceptions(self):
        self.server.start()
        #lista de uris
        interceptions = []
        while(True):
            self.log.info("Record::get_interceptions")
            interceptions = self.server.receive_msg()
            self.log.info("Record::get_interceptions: Uris from interceptions: " + str(interceptions))
            if(interceptions):
                self.interceptions.put(interceptions)

            self.log.info("Record::get_interceptions: Sleeping ...")
            time.sleep(self.sleep)

    def start(self):
        self.log.info("Record::start")
        #criando threads
        self.record = threading.Thread(target=self.run)
        self.socket = threading.Thread(target=self.get_interceptions)

        #iniciando as threads
        self.record.start()
        self.socket.start()

        self.record.join()
        self.socket.join()


