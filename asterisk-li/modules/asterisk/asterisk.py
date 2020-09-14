#!/opt/li-asterisk/tools/Python-3.6.7
from library.database.database import Database
from library.socket.tcp import Client
import time
from library.interception.interception import Status

class Asterisk(Database):
    def __init__(self, db_name, sleep_time, log):
        self.log = log
        super().__init__(db_name, log)
        self.client_iri = None
        self.client_cc = None
        self.stop = False
        self.sleep_time = sleep_time
        self.__iri_host = None
        self.__iri_port = None
        self.__cc_host = None
        self.__cc_port = None
        self.db_name = db_name

    def get_targets(self):
        self.log.info("Asterisk::get_targets: Trying get targets from database")
        query = "SELECT id,target from interception where flag=\'" + str(Status.ATIVO.value) + "\'"
        interceptions = []
        self.connect()
        (cursor,conn) = self.execute_query(query)
        targets = cursor.fetchall()
        if(targets):
            for interception_id, target in targets:
                query = "SELECT target from target where id=" + str(target)
                (cursor,conn) = self.execute_query(query)
                targets_tuple = cursor.fetchall()
                for target_tuple in targets_tuple:
                    for target in target_tuple:
                        query = "SELECT uri from uri where id=" + str(target)
                        (cursor,conn) = self.execute_query(query)
                        uri = cursor.fetchone()
                        self.log.debug("Asterisk::get_targets: uri: " + str(uri))
                        uri = uri[0]
                        self.log.debug("Asterisk::get_targets: uri and interception_id: " + str(interceptions_dict))
                        interceptions.append((interception_id, uri))
        self.disconnect()
        self.debug("Asterisk::get_targets: interceptions list: " + str(interceptions))
        return interceptions

    def setup(self):
        self.log.info("Asterisk::setup: Trying create iri client: host " + str(self.__iri_host) + " port " + str(self.__iri_port))
        self.client_iri = Client(self.__iri_host, self.__iri_port, self.db_name, self.log)
        self.client_cc = Client(self.__cc_host, self.__cc_port, self.db_name, self.log)

    def stop(self):
        self.log.info("Asterisk::setup: Trying stop service")
        self.stop = True
    
    def get_interceptions(self):
        interceptions = None
        cursor = None
        conn = None
        data = None
        while(not self.stop):
            try:
                self.log.info("Asterisk::get_interceptions")
                interceptions = self.get_targets()
                self.log.info("Asterisk::get_interceptions: Interceptions list: " + str(interceptions))
                if(interceptions):
                    self.setup()
                    self.log.info("Asterisk::get_interceptions: Trying send interceptions to iri: " + str(interceptions))
                    self.client_iri.send_message(interceptions)
                    self.client_iri.send_message("ACK")
                    self.log.info("Asterisk::get_interceptions: Trying send interceptions to record")
                    self.client_cc.connect()
                    self.client_cc.send_message(interceptions)
                    self.client_cc.send_message("ACK")
                    self.client_iri.close()
                    self.client_cc.close()
            
                self.log.info("Asterisk::get_interceptions: Sleeping ...")
                time.sleep(self.sleep_time)
            
            except Exception as error:
                self.log.error("Asterisk::get_interceptions: error: " + str(error))
                continue
        
        self.log.info("Asterisk::get_interceptions: Service stopped")

    def start(self, iri_host, iri_port, cc_host, cc_port):
        self.log.info("Asterisk::start")
        self.__iri_host = iri_host
        self.__iri_port = iri_port
        self.__cc_host = cc_host
        self.__cc_port = cc_port
        self.get_interceptions()

