from enum import Enum
from datetime import datetime

class Status(Enum):
    ATIVO = 'A'
    INATIVO = 'I'
    FINALIZADO = 'F'

def get_datetime():
    now = datetime.now()
    date_time_format = now.strftime("%Y%m%d%H%M%S")
    return date_time_format

def get_iri_name(id):
    date_time_format = get_datetime()
    iri_name = str(id) + '-' + date_time_format + "-sip"
    return iri_name

def get_cc_name(id):
    date_time_format = get_datetime()
    cc_name = str(id) + '-' + date_time_format + "-rtp"
    return cc_name

