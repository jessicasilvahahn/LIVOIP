#!/opt/li-asterisk/tools/Python-3.6.7
import asyncio
from panoramisk import Manager
from panoramisk.message import Message
import time
from functools import partial
from os import rename
from os.path import join
from modules.asterisk.cc.events.asterisk import Record
from modules.asterisk.cc.events.asterisk import Status
from queue import Queue


class Events():
    """Communication with AMI Asterisk"""
    def __init__(self, server:str, user:str, password:str, interceptions:Queue, log):
        self.__manager = Manager(loop=asyncio.get_event_loop(),host=server,username=user,secret=password)
        self.log = log
        #fila de itcs
        self.interceptions = interceptions
        self.targets_recording = []
    
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
    
    def start_record_call(self, manager, event):
        self.log.info("Events::start_record_call")
        try:
            target = None
            target_id_source = None
            target_id_detination = None
            channel = None
            file_name = ""
            if(event):
                self.log.info("Event: " + str(event) + "\n")
                #lista de alvos vindos da fila
                if(not self.interceptions.empty()):
                    targets = self.interceptions.get()
                    target_id_source = event['CallerIDNum']
                    target_id_destination = event['DestCallerIDNum']
                    status = event['DialStatus']
                    self.log.info("Target source: " + str(target_id_source) + "\n")
                    self.log.info("Target destination: " + str(target_id_destination) + "\n")
                    self.log.info("Status: " + status)
                    if(status == Status.ANSWER.value):
                        if(target_id_source in targets):
                            channel = event['Channel']
                            target = target_id_source
                        elif(target_id_destination in targets):
                            channel = event['DestChannel']
                            target = target_id_destination

                        self.log.info("Events::start_record_call: Saving target: " + str(target) + " on the list to stop record")
                        self.targets_recording.append(target)
                        self.log.info("Events::start_record_call: Targets: " + str(self.targets_recording))
                        self.log.info("Events::start_record_call: target " + str(target) + " answered from channel " + str(channel))
                        timestamp = time.time()
                        file_name = target + '.' + str(timestamp)
                        path_file = join(Record.PATH.value,file_name + Record.FORMAT.value)
                        self.log.info("Events::start_record_call: Trying record call with name file " + str(path_file))
                        future = manager.send_action({'Action': 'MixMonitor', 'Channel': channel, 'File': path_file})
                        future.add_done_callback(partial(self.callback_action_record_call))
                return
        
        except Exception as error:
            self.log.error("start_record_call:" + str(error))
 
    def stop_record_call(self, manager, event):
        self.log.info("Events::stop_record_call")
        self.log.info("Event: " + str(event) + "\n")
        try:
            target_id = None
            channel = None
            if(event):
                target = event['CallerIDNum']
                channel = event['Channel']
                if(self.targets_recording):
                    if(target in self.targets_recording):
                        self.targets_recording.remove(target)
                        self.log.info("Events:: target " + str(target) + " hangup from channel " + str(channel))
                        future = manager.send_action({'Action': 'StopMixMonitor', 'Channel': channel})
                        future.add_done_callback(partial(self.callback_action_stop_record_call))
        
        except Exception as error:
            self.log.error("Events::stop_record_call:" + str(error))

    def event_stop_record(self):
        self.log.info("Events::event_stop_record")
        callback = partial(self.stop_record_call)
        self.__manager.register_event('Hangup',callback)

    def event_start_call(self):
        self.log.info("Events::event_start_call")
        callback = self.start_record_call
        self.__manager.register_event('DialEnd',callback)

    def setup(self):
        self.log.info("Events::setup")
        self.__manager.connect()
    
    def run(self):
        self.log.info("Events::run")
        try:
            self.__manager.loop.run_forever()
        except KeyboardInterrupt:
            self.__manager.loop.close()



