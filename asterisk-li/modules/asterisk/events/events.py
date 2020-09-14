#!/opt/li-asterisk/tools/Python-3.6.7
import time
from functools import partial
from os import rename
from os.path import join
from asterisk import Record
from asterisk import Status
from library.ami.ami import Ami
from queue import Queue
from  itertools import chain
from library.interception import interception
from library.database.database import Database


class Events(Ami):
    """Communication with AMI Asterisk"""
    def __init__(self, server:str, user:str, password:str, interceptions:Queue, db_name:str, log):
        super().__init__(server,user,password,log)
        self.log = log
        #fila de itcs
        self.interceptions = interceptions
        self.targets_recording = []
        self.database = Database(db_name=db_name,log=log)
    
    def callback_action_record_call(self, future, call_id, file_name, target, targets):
        self.log.info("Events::callback_action_record_call: Result: " + str(future.result()))
        response = (future.result())['Response']
        if(response == 'Success'):
            self.log.info("Events::callback_action_record_call: Record save with sucess")

            self.save_cc_name(file_name, call_id, target, targets)             
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
            call_id = ""
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
                        if(target_id_source in chain(*targets)):
                            channel = event['Channel']
                            target = target_id_source
                        elif(target_id_destination in chain(*targets)):
                            channel = event['DestChannel']
                            target = target_id_destination

                        self.log.info("Events::start_record_call: Saving target: " + str(target) + " on the list to stop record")
                        self.targets_recording.append(target)
                        self.log.info("Events::start_record_call: Targets: " + str(self.targets_recording))
                        self.log.info("Events::start_record_call: target " + str(target) + " answered from channel " + str(channel))
                        #call-ID do sip
                        call_id = (event['AccountCode'])[0:20]
                        file_name = interception.get_cc_name(target)
                        path_file = join(Record.PATH.value,file_name + Record.FORMAT.value)
                        self.log.info("Events::start_record_call: Trying record call with name file " + str(path_file))
                        future = manager.send_action({'Action': 'MixMonitor', 'Channel': channel, 'File': path_file})
                        future.add_done_callback(partial(self.callback_action_record_call, call_id, file_name, target, targets))
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
        self.register_event('Hangup',callback)

    def event_start_call(self):
        self.log.info("Events::event_start_call")
        callback = self.start_record_call
        self.register_event('DialEnd',callback)

    def save_cc_name(self, cc, call_id, target, targets):
        self.log.info("Events::save_cc_name: Trying save file " + cc + " with call id " + call_id + " and uri " + uri)
        interceptions_ids = []
        for item in self.targets:
            if(item[1] == target):
                interceptions_ids.append(item[0])

        self.log.info("Events::save_cc_name: interceptions id list " + str(interceptions_ids))
        self.database.connect()
        for interception_id in interceptions_ids:
            query = "INSERT INTO cc VALUES(?,?,?,?)"
            values = [None,name_file,call_id,interception_id]
            (cursor,conn) = self.execute_query(query,values)
            conn.commit()
        self.database.disconnect()



