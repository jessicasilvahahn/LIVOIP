#!/opt/li-asterisk/tools/Python-3.6.7
from panoramisk import Manager
from panoramisk.message import Message
import asyncio

class Ami():
    def __init__(self, server:str, user:str, password:str, log):
        self.log = log
        self.__manager = Manager(loop=asyncio.get_event_loop(),host=server,username=user,secret=password)

    def register_event(self, event_name, callback):
        self.log.info("Ami::register_event: Event: " + event_name + " with callback: " + str(callback))
        self.__manager.register_event(event_name,callback)

    def setup(self):
        self.log.info("Ami::setup")
        self.__manager.connect()
    
    def run(self):
        self.log.info("Ami::run")
        try:
            self.__manager.loop.run_forever()
        except KeyboardInterrupt:
            self.__manager.loop.close()