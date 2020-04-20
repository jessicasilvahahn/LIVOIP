#!/opt/li-asterisk/tools/Python-3.6.7
import asyncio
from panoramisk import Manager
from panoramisk.message import Message
from scapy.all import sniff
import time
from functools import partial
from os import rename
from os.path import join
from modules.events.asterisk import Record
from modules.events.asterisk import Status


class Events():
    """Communication with AMI Asterisk"""
    def __init__(self, server:str, user:str, password:str, log):
        self.__manager = Manager(loop=asyncio.get_event_loop(),host=server,username=user,secret=password)
        self.log = log
    
    def callback_action_record_call(self, future):
        self.log.info("Events::callback_action_record_call: Result: " + str(future.result()))
        response = (future.result())['Response']
        if(response == 'Success'):
            self.log.info("Events::callback_action_record_call: Record save with sucess")               
        return
            
    
    def callback_action_stop_record_call(self, future):
        self.log.info("Events::callback_action_stop_record_call: Result: " + str(future.result()))
        response = (future.result())['Response']
        if(response == 'Success'):
            self.log.info("Events::callback_action_stop_record_call: Record stopped")               
        return
    

    def start_write_pcap(self, manager, event, target , protocol, port, pcap_path):
        self.log.info("Events::start_write_pcap")
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
            self.log.error("start_write_pcap:" + str(error))

    def start_record_call(self, target, manager, event):
        self.log.info("Events::start_record_call")
        try:
            target_id_source = None
            target_id_detination = None
            channel = None
            file_name = ""
            if(event):
                self.log.info("Event: " + str(event) + "\n")
                target_id_source = event['CallerIDNum']
                target_id_destination = event['DestCallerIDNum']
                status = event['DialStatus']
                self.log.info("Target source: " + str(target_id_source) + "\n")
                self.log.info("Target destination: " + str(target_id_destination) + "\n")
                self.log.info("Status: " + status)
                if(status == Status.ANSWER.value):
                    if(target_id_source == target):
                        channel = event['Channel']
                    elif(target_id_destination == target):
                        channel = event['DestChannel']
                    self.log.info("Events:: target " + str(target) + " answered from channel " + str(channel))
                    timestamp = time.time()
                    file_name = target + '.' + str(timestamp)
                    path_file = join(Record.PATH.value,file_name + Record.FORMAT.value)
                    self.log.info("Trying record call with name file " + str(path_file))
                    future = manager.send_action({'Action': 'MixMonitor', 'Channel': channel, 'File': path_file})
                    future.add_done_callback(partial(self.callback_action_record_call))
        except Exception as error:
            self.log.error("start_record_call:" + str(error))
 
    def stop_record_call(self, target, manager, event):
        self.log.info("Events::stop_record_call")
        self.log.info("Event: " + str(event) + "\n")
        record_name = "record.tmp"
        try:
            target_id = None
            channel = None
            if(event):
                target_id = event['CallerIDNum']
                channel = event['Channel']
                if(target_id == target):
                    self.log.info("Events:: target " + str(target) + " hangup from channel " + str(channel))
                    future = manager.send_action({'Action': 'StopMixMonitor', 'Channel': channel})
                    future.add_done_callback(partial(self.callback_action_stop_record_call))
        except Exception as error:
            self.log.error("Events::stop_record_call:" + str(error))

    def event_save_iri(self, target, protocol, port, pcap_path):
        self.log.info("Events::event_save_iri")
        event = 'DialBegin'
        self.__manager.register_event(event, self.start_write_pcap, target, protocol, port, pcap_path)

    def event_start_call(self, target):
        self.log.info("Events::event_start_call, target " + str(target))
        event = 'DialEnd'
        callback = partial(self.start_record_call, target)
        self.__manager.register_event(event,callback)

    def event_stop_record(self, target):
        self.log.info("Events::event_stop_record, target " + str(target))
        event = 'Hangup'
        callback = partial(self.stop_record_call,target)
        self.__manager.register_event(event,callback)

    def setup(self):
        self.log.info("Events::setup")
        self.__manager.connect()
    
    def run(self):
        self.log.info("Events::run")
        try:
            self.__manager.loop.run_forever()
        except KeyboardInterrupt:
            self.__manager.loop.close()



