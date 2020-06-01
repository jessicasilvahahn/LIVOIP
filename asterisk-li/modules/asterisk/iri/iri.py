#!/opt/li-asterisk/tools/Python-3.6.7

from library.sniffer.sniffer import Sniffer
from library.socket.tcp import Server
import time
from os.path import join
from scapy.all import wrpcap
import threading
from os.path import exists
from os import makedirs

class Iri(Sniffer):
    def __init__(self, interface, protocol, sip_port, path_pcap, host, port, buffer_size, sleep, log):
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
    
    def start_sniffer(self):
        #depois passar id pra outras classes
        self.log.info("Iri::start_sniffer: id: " + str(threading.currentThread().getName()))
        self.setup()
        super().start()

    def write_pcap(self, packets):
        self.log.info("Iri::write_pcap")
        self.log.info("Iri::write_pcap: Packets: " + str(packets))
        self.log.info("Iri::write_pcap: proxy: " + str((packets['proxy'])))
        name_pcap = ((packets['Call-ID']).strip())[0:20] + ".pcap"
        if(packets['proxy']):
            name_pcap = ((packets['proxy']).strip())[0:20] + ".pcap.B"
       
        name_pcap = name_pcap.replace("\r","")
        name_pcap = name_pcap.replace(" ","")
        name_pcap = join(self.path, name_pcap)
        packet_list = packets['packets']
        self.log.info("Iri::write_pcap: Trying save pcap: " + name_pcap)
        wrpcap(name_pcap, packet_list, append=True)
        self.log.info("Iri::write_pcap: Pcap: " + name_pcap + " is terminated")
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
            if(interceptions):
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






