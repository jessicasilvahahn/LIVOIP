#!/opt/li-asterisk/tools/Python-3.6.7

from modules.asterisk.sniffer.sniffer import Sniffer
from library.socket.tcp import Server
import time
from os.path import join
from scapy.all import wrpcap
import threading
from os.path import exists
from os import makedirs
from library.database.database import Database
from library.interception import interception

class Iri(Sniffer):
    def __init__(self, interface, protocol, sip_port, path_pcap, host, port, buffer_size, sleep, db_name, log):
        super().__init__(interface, protocol, sip_port,log)
        self.server = Server(host, port, buffer_size, log)
        self.log = log
        if(not exists(path_pcap)):
            makedirs(path_pcap)
        self.path = path_pcap
        self.sniffer = None
        self.socket = None
        self.reader = None
        self.sleep = sleep
        self.database = Database(db_name,log)
    
    def start_sniffer(self):
        #depois passar id pra outras classes
        self.log.info("Iri::start_sniffer: id: " + str(threading.currentThread().getName()))
        self.setup()
        super().start()

    def file_iri_exists(self, call_id, interception_id):
        self.log.info("file_iri_exists: call id: " + str(call_id) + " interception id: " + str(interception_id))
        id = None
        query = "SELECT id from iri where call_id=\'" + str(call_id) + "\' and interception_id=" + str(interception_id)
        (cursor,conn) = self.database.execute_query(query)
        id = cursor.fetchone()
        self.log.info("file_iri_exists: id: " + str(id))
        if(not id):
            self.log.info("file_iri_exists: iri not exists: " + str(id))
            return False
        
        return True

    def save_iri_file(self, iri, call_id, interceptions_ids, proxy=False):
        self.log.info("Iri::save_files: Trying save file: " + iri + " call id " + call_id + " ids " + str(interceptions_ids) + " in the database")
        try:
            iri_exists = False
            proxy = []
            self.database.connect()
            for interception_id in interceptions_ids:
                iri_exists = self.file_iri_exists(call_id,interception_id)
                if(not proxy):
                    if(not iri_exists):
                        query = "INSERT INTO iri VALUES(?,?,?,?,?)"
                        values = [None, iri, None, interception_id, call_id]
                    else:
                        query = "UPDATE iri SET iri=\'" + str(iri) + "\' where interception_id=" + str(interception_id) + " and call_id=\'" + str(call_id) + "\'"
                        values = None
                else:
                    if(not iri_exists):
                        query = "INSERT INTO iri VALUES(?,?,?,?,?)"
                        values = [None, None, iri, interception_id, call_id]
                    else:
                        query = "UPDATE iri SET proxy=\'" + iri + "\' where interception_id=" + str(interception_id)
                        values = None
                
                self.log.info("Iri::save_files: query :" + str(query)) 
                (cursor,conn) = self.database.execute_query(query,values)
                conn.commit()
            self.database.disconnect()
        except Exception as error:
            self.log.error(str(error))
        
        return

    def write_pcap(self, packets):
        self.log.info("Iri::write_pcap")
        self.log.info("Iri::write_pcap: Packets: " + str(packets))
        self.log.info("Iri::write_pcap: proxy: " + str((packets['proxy'])))
        call_id = ((((packets['Call-ID']).strip())[0:20]).replace("\r","")).replace(" ","")
        name_pcap = interception.get_iri_name(packets['URI'])
        new_path = None
        proxy = False
        interceptions_id = packets['interceptions_id']
        if(packets['proxy']):
            call_id = ((((packets['proxy']).strip())[0:20]).replace("\r","")).replace(" ","")
            self.log.info("Iri::write_pcap: call id proxy :" + str(call_id)) 
            name_pcap = name_pcap + ".pcap.B"
            proxy = True
        else:
            name_pcap = name_pcap + ".pcap"
       
        new_path = join(self.path, name_pcap)
        packet_list = packets['packets']
        self.log.info("Iri::write_pcap: Trying save pcap: " + name_pcap)
        wrpcap(new_path, packet_list, append=True)
        self.log.info("Iri::write_pcap: Pcap: " + new_path + " is terminated")
        self.save_iri_file(name_pcap, call_id, interceptions_id, proxy)
        return

    
    def read_packets(self):
        self.log.info("Iri::read_packets: thread id: " + str(threading.currentThread().getName()))
        name_pcap = ""
        packets_dict = None
        while(True):
            self.log.info("Iri::read_packets")
            try:
                if(not self.packets.empty()):
                    self.log.info("Iri::read_packets: Sip packets: " + str(self.packets))
                    packets_dict = self.packets.get()
                    pcap = threading.Thread(target=self.write_pcap, args=(packets_dict,))
                    pcap.start()
                    pcap.join()
                    packets_dict = None

                self.log.info("Iri::read_packets: Sleeping ...")
                self.log.info("Iri::read_packets: Packets: " + str(packets_dict))
                time.sleep(self.sleep)

            except Exception as error:
                self.log.error(str(error))

    def get_interceptions(self):
        self.log.info("Iri::get_interceptions: thread id: " + str(threading.currentThread().getName()))
        self.server.start()
        #lista de uris
        interceptions = []
        while(True):
            interceptions = self.server.receive_msg()
            self.log.info("Iri::get_interceptions: Uris from interceptions: " + str(interceptions))
            self.interception_queue.put(interceptions)
            self.log.info("Iri::get_interceptions: Sleeping ...")
            time.sleep(self.sleep)

    def start(self):
        self.log.info("Iri::start")
        #criando threads
        sniffer_thread_id = hash(1)
        socket_thread_id = hash(2)
        reader_thread_id = hash(3)

        self.sniffer = threading.Thread(name=sniffer_thread_id,target=self.start_sniffer)
        self.socket = threading.Thread(name=socket_thread_id,target=self.get_interceptions)
        self.reader = threading.Thread(name=reader_thread_id,target=self.read_packets)

        #iniciando as threads
        self.socket.start()
        self.sniffer.start()
        self.reader.start()
        
        self.socket.join()
        self.sniffer.join()
        self.reader.join()






