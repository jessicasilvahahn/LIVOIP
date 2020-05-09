#!/opt/li-asterisk/tools/Python-3.6.7

from library.shared.ami.ami import Ami
from library.shared.database.database import Database
from modules.mediation_function.manager.cdr import Cdr
from modules.mediation_function.manager.evidences import Evidences
from queue import Queue
import threading
import time 

class Manager(Ami):
    
    def __init__(self, server:str, user:str, password:str, iri:dict, cc:dict, email:dict, host_evidences:str, sleep_time, db_name:str, log):
        super().__init__(server,user,password,log)
        self.log = log
        self.cdrs = Queue()
        self.db_name = db_name
        self.iri = iri
        self.cc = cc
        self.evidences = None
        self.cdr_event = None
        self.get_evidences = None
        self.dump_cdr = None
        self.sleep = sleep_time
        self.email = email
        self.host_evidences = host_evidences

    def setup(self):
        super().setup()
        super().register_event('Cdr',self.get_cdr)
        database = Database(self.db_name, self.log)
        self.evidences = Evidences(self.iri,self.cc,self.email,self.host_evidences, self.log,database)

    def get_cdr(self, manager, event):
        self.log.info("Manager::get_evidences: Event: " + str(event))
        disposition = event['Disposition']
        if(disposition == 'ANSWERED'):
            self.log.info("Manager::get_evidences: ANSWERED ")
            call_id = event['AccountCode']
            iri = call_id + '.pcap'
            cc = call_id + '.wav'
            answer_time = event['AnswerTime']
            call_duration = event['Duration']
            end_call_time = event['EndTime']
            call_start_time = event['StartTime']
            source_uri = event['Source']
            destination_uri = event['Destination']
            database = Database(self.db_name, self.log)
            cdr = Cdr(iri, cc, answer_time, call_duration, end_call_time, call_start_time, source_uri, destination_uri, database,self.log)
            self.cdrs.put(cdr)
        return
    def save_cdr(self):
        while (True):
            self.log.info("Manager::save_cdr")
            if(not self.cdrs.empty()):
                cdr = self.cdrs.get()
                #salvar no banco
                if(not cdr.save()):
                    self.log.info("Manager::save_cdr: Targets not found")
            self.log.info("Manager::save_cdr: Sleeping...")
            time.sleep(self.sleep)

    def run(self):
        try:
            #vou ter 3 threads, event cdr, save cdr, get evidences
            self.log.info("Record::start")
            #criando threads
            self.cdr_event = threading.Thread(target=super().run)
            self.get_evidences = threading.Thread(target=self.evidences.run)
            self.dump_cdr = threading.Thread(target=self.save_cdr)
            #iniciando as threads
            self.cdr_event.start()
            self.get_evidences.start()
            self.dump_cdr.start()

            self.cdr_event.join()
            self.get_evidences.join()
            self.dump_cdr.join()
            
        except Exception as error:
            self.log.error("Manager::run: Error: " + str(error))
        