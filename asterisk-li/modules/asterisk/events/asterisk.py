from enum import Enum

class Status(Enum):
    ANSWER = 'ANSWER'

class Record(Enum):
    PATH = "/var/spool/asterisk/recording"
    FORMAT = ".wav"