#!/opt/li-asterisk/tools/Python-3.6.7
from modules.ari.http import Http
from modules.ari.http import Method
from modules.ari.uris import GET_RECORD
from modules.ari.uris import LIST_RECORDS


class Fault(dict):
    def __missing__(self, key):
    return key

class RegisterLawfulInterception():
    def __init__(self):
        pass

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
        

        
        
