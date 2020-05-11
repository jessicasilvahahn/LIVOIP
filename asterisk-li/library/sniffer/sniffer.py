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
        self.sip_state = {}
        self.sip = None

    def complete(self):
        self.log.info("Sniffer::complete")
        for packet_dict in self.__sip_dict.items():
            
            packets = (packet_dict[1])['packets']
            call_id = (packet_dict[1])['Call-ID']

            for packet in packets:
                load = packet.load
                packet_string = load.decode()
                
                trying = self.sip.trying(packet_string)
                if(trying):
                    (self.sip_state[call_id])['trying'] =  trying
                
                ringing = self.sip.ringing(packet_string)
                if(ringing):
                    (self.sip_state[call_id])['ringing'] =  ringing

                ack = self.sip.ack(packet_string)
                if(ack):
                    (self.sip_state[call_id])['ack'] = ack
                
                bye = self.sip.bye(packet_string)
                if(bye):
                    (self.sip_state[call_id])['bye'] =  bye

                cancel = self.sip.cancel(packet_string)
                if(cancel):
                    (self.sip_state[call_id])['cancel'] =  cancel

            self.log.info("Sniffer::complete: sip state:" + str(self.sip_state))

            if((self.sip_state[call_id])['ringing'] == Message.RINGING.value and (self.sip_state[call_id])['ack'] == Message.ACK.value and (self.sip_state[call_id])['bye'] == Message.BYE.value):
                self.log.info("Sniffer::complete: Call is finished!: " + str(call_id))
                self.packets.put(self.__sip_dict.pop(call_id))
                self.sip_state.pop(call_id)
            
            elif((self.sip_state[call_id])['cancel'] == Message.CANCEL.value):
                self.log.info("Sniffer::complete: Call is canceled!: " + str(call_id))
                self.sip_state.pop(call_id)
                self.__sip_dict.pop(call_id)

        return

    def callback(self, packet):
        self.log.info("Sniffer::callback")
        sip = {}
        proxy = None
        try:
            load = packet.load
            packet_string = load.decode()
            message = self.sip.invite(packet_string)
            call_id = self.sip.get_call_id(packet_string)
            asterisk_call_id = self.sip.get_asterisk_call_id(packet_string)
            self.log.info("Sniffer::callback: Call-ID: " + str(call_id))
            if(not call_id):
                return
            if(message == Message.INVITE.value):
                self.log.info("Sniffer::callback: INVITE")
                (uri_from, uri_to) = self.sip.get_uris(packet_string)
                self.interception_list = self.interception_queue.get()
                self.log.info("Sniffer::callback: interceptions " + str(self.interception_list))
                if(self.interception_list):
                    if(asterisk_call_id):
                        proxy = asterisk_call_id
                    
                    if(uri_from in self.interception_list):
                        self.log.info("Sniffer::callback: target " + str(uri_from))
                        sip = {call_id: {'URI': uri_from, 'proxy': proxy, 'Call-ID': call_id, 'packets': [packet]}}
                    elif(uri_to in self.interception_list):
                        self.log.info("Sniffer::callback: target " + str(uri_to))
                        sip = {call_id: {'URI': uri_to, 'proxy': proxy, 'Call-ID': call_id, 'packets': [packet]}}
                        
                    self.__sip_dict.update(sip)
                    self.sip_state.update({call_id: {
                        'trying': None,
                        'ringing': None,
                        'ack': None,
                        'bye': None,
                        'cancel': None
                    }})
                    self.log.info("Sniffer::callback: Sip packets: " + str(self.__sip_dict))
            else:
                message = self.sip.options(packet_string)
                if(message == Message.OPTIONS.value):
                    return
                
                self.log.info("Sniffer::callback: It's not INVITE")
                self.log.info("Sniffer::callback: Sip packets save: " + str(self.__sip_dict))
                if(self.__sip_dict):
                    if(call_id in self.__sip_dict):
                        ((self.__sip_dict[call_id])['packets']).append(packet)
                    
                    self.complete()
    
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