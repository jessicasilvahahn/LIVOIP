#!/opt/li-asterisk/tools/Python-3.6.7
from modules.ari.http import Http
from modules.ari.http import Method
from modules.ari.uris import GET_RECORD
from modules.ari.uris import LIST_RECORDS
from modules.events import Events
from modules.user_interface.simple.interface import Interface

class Fault(dict):
    def __missing__(self, key):
    return key

class RegisterLawfulInterception():
    def __init__(self, log, server, user, password, protocol, port, pcap_path, database):
        self.log = log
        self.server = server
        self.user = user
        self.password = password
        self.protocol = protocol
        self.port = port
        self.pcap_path = pcap_path
        self.event = None
        self.database = database
  
    def call_register_interface(self, mode):
        interface = None
        li_registered = None
        if(mode == "simple"):
            interface = Interface(self.log, self.database)
            li_registered = interface.li_register()
            return li_registered
        elif(mode == "web"):
            pass
        
        else:
            self.log.error("RegisterLawfulInterception::call_interface: mode " + str(mode) + " invalid\n")

    def register(self):
        self.log.info("RegisterLawfulInterception::register")
        """self.event = Events.Events(self.server, self.user, self.password, self.log)
        self.event.setup()
        #pegar essas informacoes do banco
        self.event.event_save_iri(self.target, self.protocol, self.port, self.pcap_path)
        self.event.event_save_call(self.target)"""

    def run(self):
        if(self.event):
            self.event.run()

class GetLawfulInterception(Http):
    
    def __init__(self, host, port, user , password, timeout, buffer_size):
        self.__main_uri = "http://" + str(host) + ':' + str(port)
        super().__init__(host, port, user , password, timeout)
        self.__buffer_size = buffer_size

    def find_target(self,json_response, target):
        #ver como vem a resposta e retornar apenas as gravacoes do alvo
        list_target_records = []

        return list_target_records
    
    def get_call_record(target, file_path):

        get_all_records = LIST_RECORDS.format_map(Fault(host=self.__main_uri))
        code = None
        json = None
        response = None        
        list_target_records = []
        get_record = ""
        try:
            (code, json, response) = super().http_request(Method.GET, get_all_records, False)
            if(json):
                list_target_records = self.find_target(json, target)
                code = None
                json = None
                response = None
                for record in list_target_records:
                    get_record = GET_RECORD.format_map(Fault(host=self.__main_uri))
                    get_record += get_record.format_map(Fault(recording_name=record))
                    (code, json, response) = super().http_request(Method.GET, get_record, True)
                    if(response):
                        file_name =  file_path + record
                        with open(file_name, "wb") as file:
                            for chunk in response.iter_content(self.__buffer_size):
                            file.write(chunk)
        except Exception as error:
            raise Exception(str(error))
        

        
        
