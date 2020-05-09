#!/opt/li-asterisk/tools/Python-3.6.7
import re
from enum import Enum

class Message(Enum):
    INVITE = 0
    BYE = 1
    CANCEL = 2
    OK_BYE = 3
    OK_CANCEL = 4
    OPTIONS = 5

class Sip():
    def __init__(self, log):
        self.log = log

    def invite(self, packet:str):
        self.log.info("Sip::invite")
        match = re.findall("^INVITE", packet)
        if(match):
            self.log.info("Sip::invite: It's INVITE")
            return Message.INVITE

    def bye(self, packet:str):
        self.log.info("Sip::bye")
        match = re.findall("^BYE", packet)
        if(match):
            self.log.info("Sip::bye: It's BYE")
            return Message.BYE
    
    def cancel(self, packet:str):
        self.log.info("Sip::cancel")
        match = re.findall("^CANCEL", packet)
        if(match):
            self.log.info("Sip::cancel: It's CANCEL")
            return Message.CANCEL

    def options(self, packet:str):
        match = re.findall("^OPTIONS", packet)
        if(match):
            return Message.OPTIONS
        

    def ok(self, packet:str):
        self.log.info("Sip::ok: packet: " + str(packet))
        match = re.findall("^SIP/2.0 200 Ok", packet)
        if(match):
            self.log.info("Sip::ok: It's 200 OK")
            bye = re.findall("BYE", packet)
            if(bye):
                self.log.info("Sip::ok: It's 200 OK to BYE")
                return Message.OK_BYE
            cancel = re.findall("CANCEL", packet)
            if(cancel):
                self.log.info("Sip::ok: It's 200 OK to CANCEL")
                return Message.OK_CANCEL

    def get_call_id(self, packet:str):
        self.log.info("Sip::get_call_id")
        call_id = None
        match = re.search("Call-ID:", packet)
        if(match):
            span = match.span()
            aux = packet[span[1]:]
            split = re.split('\n',aux)
            call_id = split[0]
            self.log.info("Sip::get_call_id: Call-ID: " + str(call_id))
        return call_id
    
    def get_uri(self, packet, filter):
        self.log.info("Sip::get_uri")
        uri = ""
        match = re.search(filter, packet)
        if(match):
            span = match.span()
            aux = packet[span[1]:]
            split = re.split('\n',aux)
            split_2 = re.split(';',split[0])
            split_3 = re.split(':',split_2[0])
            uri = re.split('@',split_3[1])
            uri = uri[0]
            self.log.info("Sip::get_uris: URI: " + str(uri) + " FILTER: " + filter)
            return uri
    
    def get_uris(self, packet:str):
        self.log.info("Sip::get_uris")
        uri_from = ""
        uri_to = ""
        uri_from = self.get_uri(packet,"From:")
        uri_to = self.get_uri(packet,"To:")
        return (uri_from, uri_to)
        
        


    



