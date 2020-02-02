#!/opt/li-asterisk/tools/Python-3.6.7
import asyncio
from panoramisk import Manager
from panoramisk.message import Message
from scapy.all import sniff
import time

class Events():
    """Communication with AMI Asterisk"""
	def __init__(self, server:str, user:str, password:str):
        self.__manager = Manager(loop=asyncio.get_event_loop(),
            host='server',
            username='user',
            secret='password')
    
    def callback_action_record_call(self, future):
        #colocar no log depois
        print(future.result())
    
    def start_write_pcap(self, manager, event, target , protocol, port, pcap_path):
        target_id = None
        sip = None
        try:
            if (event):
                target_id = event['CallerIDNum']
                if(target_id == target):
                    sip = protocol + " and " + port
                    sniff(offline=pcap_path, filter=sip)    
            return
        except Exception as error:
            print("start_write_pcap": str(error))

    def start_record_call(self, manager, event, target):
        target_id = None
        channel = None
        file_name = ""
        try:
            if (event):
            target_id = event['CallerIDNum']
            channel = event['Channel']
            timestamp = time.time()
            file_name = target + '.' + str(timestamp)
            if(target_id == target):
                future = self.__manager.send_action({'Action': 'Monitor', 'Channel': channel, 'File': file_name})
                future.add_done_callback(self.callback_action_record_call)
            return
        except Exception as error:
            print("call_callback_ami": str(error))

    def event_save_iri(self, target, protocol, port, pcap_path):
        event = 'DialBegin'
        self.__manager.register_event(event, self.start_write_pcap, target, protocol, port, pcap_path)

    def event_save_call(self, target):
        event = 'DialEnd'
        self.__manager.register_event(event, self.start_record_call,target)

    def run(self):
        self.__manager.connect()
        try:
            self.__manager.loop.run_forever()
        except KeyboardInterrupt:
            manager.loop.close()

    

