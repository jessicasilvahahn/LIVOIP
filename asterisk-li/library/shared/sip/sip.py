#!/opt/li-asterisk/tools/Python-3.6.7
import re
from enum import Enum

class Message(Enum):
    INVITE = 0
    TRYING = 1
    RINGING = 2
    OK_INVITE = 3
    ACK = 4
    BYE = 5
    CANCEL = 6
    OK_BYE = 7
    OPTIONS = 8
    
class Sip():
    def __init__(self, log):
        self.log = log

    def invite(self, packet:str):
        self.log.info("Sip::invite")
        match = re.findall("^INVITE", packet)
        if(match):
            self.log.info("Sip::invite: It's INVITE")
            return Message.INVITE.value

    def bye(self, packet:str):
        self.log.info("Sip::bye")
        match = re.findall("^BYE", packet)
        if(match):
            self.log.info("Sip::bye: It's BYE")
            return Message.BYE.value
        return None
    
    def cancel(self, packet:str):
        self.log.info("Sip::cancel")
        message = None
        match = re.findall("^CANCEL", packet)
        if(match):
            self.log.info("Sip::cancel: It's CANCEL")
            message = Message.CANCEL.value

        return message

    def options(self, packet:str):
        match = re.findall("^OPTIONS", packet)
        if(match):
            return Message.OPTIONS.value
        
    def trying(self, packet:str):
        self.log.info("Sip::trying: packet: " + str(packet))
        message = None
        match = re.findall("^SIP/2.0 100 Trying", packet)
        if(match):
            self.log.info("Sip::trying: It's Trying")
            message = Message.TRYING.value
        
        return message

    def ringing(self, packet:str):
        self.log.info("Sip::ringing: packet: " + str(packet))
        message = None
        match = re.findall("^SIP/2.0 180 Ringing", packet)
        if(match):
            self.log.info("Sip::trying: It's Ringing")
            message = Message.RINGING.value
        
        return message

    def ack(self,packet:str):
        self.log.info("Sip::ack: packet: " + str(packet))
        message = None
        ack = re.findall("^ACK", packet)
        if(ack):
            self.log.info("Sip::ack: It's ACK")
            message = Message.ACK.value
        
        return message

    def ok_invite(self, packet:str):
        self.log.info("Sip::ok_invite: packet: " + str(packet))
        match = re.findall("^SIP/2.0 200 OK", packet)
        message = None
        if(match):
            invite = re.findall("INVITE", packet)
            if(len(invite) == 2):
                self.log.info("Sip::ok: It's 200 OK to INVITE")
                message = Message.OK_INVITE.value
        return message
    
    def ok_bye(self, packet:str):
        self.log.info("Sip::ok_bye: packet: " + str(packet))
        message = None
        match = re.findall("^SIP/2.0 200 OK", packet)
        if(match):
            self.log.info("Sip::ok_bye: It's 200 OK")
            bye = re.findall("BYE", packet)
            if(len(bye) == 1):
                self.log.info("Sip::ok_bye: It's 200 OK to BYE")
                message = Message.OK_BYE.value
        return message

    def get_asterisk_call_id(self, packet:str):
        self.log.info("Sip::get_asterisk_call_id")
        call_id = None
        match = re.search("X-Asterisk-Source-Call-ID:", packet)
        if(match):
            span = match.span()
            aux = packet[span[1]:]
            split = re.split('\n',aux)
            call_id = split[0]
            self.log.info("Sip::get_asterisk_call_id: Call-ID: " + str(call_id))
        return call_id
        
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
        
        


    



