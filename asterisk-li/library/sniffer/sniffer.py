#!/opt/li-asterisk/tools/Python-3.6.7
from scapy.all import sniff
import threading
from library.shared.sip.sip import Sip
from library.shared.sip.sip import Message
from queue import Queue

class Sniffer():
    def __init__(self, interface, protocol, port, log):
        self.interface = interface
        self.protocol = protocol
        self.port = port
        self.filter = None
        self.log = log
        #fila de lista de pacotes, vai ser usado pela classe filha
        self.packets = Queue()
        self.interception_list = []
        self.interception_queue = Queue()
        self.__sip_dict = {}
        self.sip = None

    def callback(self, packet):
        self.log.info("Sniffer::callback")
        sip = {}
        try:
            load = packet.load
            packet_string = load.decode()
            message = self.sip.invite(packet_string)
            call_id = self.sip.get_call_id(packet_string)
            self.log.info("Sniffer::callback: Call-ID: " + str(call_id))
            if(not call_id):
                return
            if(message == Message.INVITE):
                self.log.info("Sniffer::callback: INVITE")
                (uri_from, uri_to) = self.sip.get_uris(packet_string)
                self.interception_list = self.interception_queue.get()
                self.log.info("Sniffer::callback: interceptions " + str(self.interception_list))
                if(self.interception_list):
                    if(uri_from in self.interception_list):
                        self.log.info("Sniffer::callback: target " + str(uri_from))
                        sip = {call_id: {'URI': uri_from, 'Call-ID': call_id, 'packets': [packet]}}
                    elif(uri_to in self.interception_list):
                        self.log.info("Sniffer::callback: target " + str(uri_to))
                        sip = {call_id: {'URI': uri_to, 'Call-ID': call_id, 'packets': [packet]}}
                        
                    self.__sip_dict.update(sip)
                    self.log.info("Sniffer::callback: Sip packets: " + str(self.__sip_dict))
            else:
                message = self.sip.options(packet_string)
                if(message == Message.OPTIONS):
                    return
                
                self.log.info("Sniffer::callback: It's not INVITE")
                self.log.info("Sniffer::callback: Sip packets save: " + str(self.__sip_dict))
                if(self.__sip_dict):
                    if(call_id in self.__sip_dict):
                        ((self.__sip_dict[call_id])['packets']).append(packet)
                    
                    message = self.sip.ok(packet_string)
                    self.log.info("Sniffer::callback: message: " + str(message))
                    if(message == Message.OK_BYE):
                        self.log.info("Sniffer::callback: 200 OK BYE")
                        self.packets.put(self.__sip_dict)
                        self.__sip_dict = {}
                        
                    else:
                        message = self.sip.cancel(packet_string)
                        if(message == Message.CANCEL):
                            self.log.info("Sniffer::callback: It's a CANCEL")
                            self.packets.put(self.__sip_dict)
                            self.__sip_dict = {}

                    
                    
        except Exception as error:
            self.log.error(str(error))
        
        return

    def setup(self):
        self.log.info("Sniffer::setup")
        self.filter = str(self.protocol) + " and port " + str(self.port)
        self.sip = Sip(self.log)

    def start(self):
        try:
            self.log.info("Sniffer::start: Start Sniffer with interface " + self.interface + " and filter " + self.filter)
            sniff(iface=self.interface,filter=self.filter, prn=self.callback)
        except Exception as error:
            self.log.error(str(error))