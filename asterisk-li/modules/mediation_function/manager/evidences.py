#!/opt/li-asterisk/tools/Python-3.6.7
from library.shared.ari.http import Http
from library.shared.ari.http import Method
from library.shared.ari.uris import GET_PCAP
from library.shared.ari.uris import GET_RECORD
from library.smtp.smtp import SmtpGmail
from library.smtp.smtp import MimeType
from scapy.utils import PcapReader
from scapy.all import wrpcap
from os.path import split
from os import rename
from os.path import join
from os import remove
from queue import Queue
from os.path import exists
from os import makedirs
import threading
import time

class Evidences():
    def __init__(self, iri:dict, cc:dict, email:dict, host:str, log, database):
        self.log = log
        self.path_iri = iri['path_iri']
        self.path_cc = cc['path_cc']
        self.database = database
        self.iri_buffer = iri['buffer']
        self.cc_buffer = cc['buffer']
        self.iri_client = Http(iri['host'],iri['port'],iri['user'],iri['password'],iri['timeout'])
        self.cc_client = Http(cc['host'],cc['port'],cc['user'],cc['password'],cc['timeout'])
        self.targets = Queue()
        self.email = SmtpGmail(self.log)
        self.email.setup(email['address'],email['passwd'],MimeType.HTML.value)
        #host:port, do server que vai receber as requisicoes da autoridade
        self.host = host
        self.targets_thread = None
        self.evidences = None
        self.alerted_targets = []

    def create_dir(self, path, dir):
        path_dir = join(path,dir)
        self.log.info("Evidences::create_dir: dir: " + str(path_dir))
        if(not exists(path_dir)):
            makedirs(path_dir)
        return path_dir
    
    def get_iri(self, name:str, new_path:str):
        self.log.info("Evidences::get_iri: file: " + str(name))
        host = self.iri_client.server_parameters['host'] + ':' + self.iri_client.server_parameters['port']
        url = GET_PCAP.format(host) + "?file=" + str(name)
        (code, json, response) = self.iri_client.http_request(Method.GET,url,True)
        self.log.info("Evidences::get_iri: Status code: " + str(code))
        if(code == 200):
            self.log.info("Evidences::get_iri: Trying save file: " + str(name))
            file = open(new_path, 'wb')
            for chunk in response.iter_content(self.iri_buffer):
                file.write(chunk)
            file.close()
            return True

        return False

    def filter_pcap(self, pcap, filter):
        #filtrar pcap de acordo com o call-id se precisar
        call_id = filter
        self.log.info("Evidences::filter_pcap: file: " + str(pcap))
        split_path = split(pcap)
        name_pcap = split_path[1] + ".old"
        new_name = join(split_path[0],name_pcap)
        self.log.info("Evidences::filter_pcap: Trying rename file: " + str(pcap))
        rename(pcap,new_name)
        self.log.info("Evidences::filter_pcap: file renamed: " + str(new_name))
        for packet in PcapReader(new_name):
            load = packet.load
            packet_str = load.decode()
            if(call_id in packet_str):
                wrpcap(pcap, packet, append=True)
        
        self.log.info("Evidences::filter_pcap: Trying remove old file: " + str(new_name))
        remove(new_name)
        return

    def get_cc(self,name:str,new_path:str):
        self.log.info("Evidences::get_cc: file: " + str(name))
        host = self.cc_client.server_parameters['host'] + ':' + self.cc_client.server_parameters['port']
        self.log.info("Evidences::get_cc: host: " + str(host))
        url = GET_RECORD.format(host,name)
        self.log.info("Evidences::get_cc: url: " + str(url))
        (code, json, response) = self.cc_client.http_request(Method.GET,url,True)
        self.log.info("Evidences::get_cc: Status code: " + str(code))
        if(code == 200):
            self.log.info("Evidences::get_cc: Trying save file: " + str(name))
            file = open(new_path, 'wb')
            for chunk in response.iter_content(self.cc_buffer):
                file.write(chunk)
            file.close()
            return True
        
        return False

    def get_targets(self):
        while(True):
            #pegar do banco pela cdr e associar o target e a autoridade
            self.log.info("Evidences::get_targets")
            leas_list = []
            targets_dict = {}
            oficios = None
            cpf = ""
            id = None
            targets = None

            query = "SELECT target_id,id from cdr_targets where alert=0;"
            self.database.connect()
            (cursor,conn) = self.database.execute_query(query)
            if(cursor):
                targets = cursor.fetchall()
                self.log.info("Evidences::get_targets: targets: " + str(targets))
                
            if(targets):
                for cpf,id in targets:
                    if(not cpf in self.alerted_targets):
                        
                        self.alerted_targets.append(cpf)
                        self.log.info("Evidences::get_targets: alerted_targets: " + str(self.alerted_targets))
                        query = "SELECT oficio from li where target_id=\'" + str(cpf) + "\' and flag=\'A\'"
                        (cursor,conn) = self.database.execute_query(query)
                        oficios = cursor.fetchall()
                        self.log.info("Evidences::get_targets: oficios: " + str(oficios))
                        if(oficios):
                            for oficio in oficios:
                                query = "SELECT lea from oficio where id=" + str(oficio[0])
                                (cursor,conn) = self.database.execute_query(query)
                                lea = cursor.fetchone()
                                if(lea):
                                    lea = lea[0]
                                    leas_list.append(lea)
                        
                            self.log.info("Evidences::get_targets: leas: " + str(leas_list))
                            query = "SELECT iri,cc from cdr where id=" + str(id)
                            (cursor,conn) = self.database.execute_query(query)
                            evidences = cursor.fetchall()
                            self.log.info("Evidences::get_targets: evidences: " + str(evidences))
                            if(evidences):
                                for iri,cc in evidences:
                                    targets_dict = {cpf: {'cdr_targets_id': id, 'lea': leas_list, 'iri': iri, 'cc': cc}}
                                    self.log.info("Evidences::get_targets: targets: " + str(targets))
                                    self.targets.put(targets_dict)

            self.database.disconnect()
            self.log.info("Evidences::get_targets: Sleeping ... ")
            time.sleep(4)

    def get_evidences(self):
        while(True):
            new_path_iri = None
            new_path_cc = None
            urls = None
            url_iri = "http://" + self.host + '/iri'
            url_cc = "http://" + self.host + '/cc'
            self.log.info("Evidences::get_evidences")
            if(not self.targets.empty()):
                targets = self.targets.get()
                for targets in targets.items():
                    iri = (targets[1])['iri']
                    cc = (targets[1])['cc']
                    new_path_iri = self.create_dir(self.path_iri,targets[0])
                    new_path_iri = join(new_path_iri,iri)
                    new_path_cc = self.create_dir(self.path_cc,targets[0])
                    new_path_cc = join(new_path_cc,cc)
                    if(self.get_cc(cc,new_path_cc) and self.get_iri(iri,new_path_iri)):
                        urls = {'url_iri': url_iri + '?file=' + str(iri) + "&target=" + str(targets[0]), 'url_cc': url_cc + '?file=' + str(cc) + "&target=" + str(targets[0]), 'cpf': targets[0]}
                        self.alert_lea((targets[1])['lea'],urls,(targets[1])['cdr_targets_id'])
                    else:
                        self.log.error("Evidences::get_evidences: Error to get evidences (iri and cc)")
            self.log.info("Evidences::get_evidences: Sleeping ... ")
            time.sleep(3)

    def alert_lea(self, leas:list, urls:dict,cdr_targets_id:int):
        self.log.info("Evidences::alert_lea")
        try:
            self.database.connect()
            for lea in leas:
                query = "SELECT email from lea where id=" + str(lea)
                (cursor,conn) = self.database.execute_query(query)
                email = cursor.fetchone()
                self.database.disconnect()
                email = email[0]
                self.log.info("Evidences::alert_lea: Lea: " + str(email))
                content = "<p>Prezado (a) Vossa Excelencia, foi constatado em nosso sistema que o investigado abaixo fez uma ligacao. </p> <br> <p> Alvo: " + urls['cpf'] + "<p><br> <p> Pcap: <a href=\"" + urls['url_iri'] + "\">" + urls['cpf'] + ".pcap" + "</a> <p> <br><p>Audio: <a href=\"" + urls['url_cc'] + "\">" + urls['cpf'] + ".wav" + "</a><p>"
                subject = "[Investigacao] ALERT: Novas evidencias do alvo " + str(urls['cpf'])
                self.log.info("Evidences::alert_lea: Content: " + str(content) + " ,subject: " + str(subject))
                self.email.send(email,subject,content)
                self.change_state(lea,urls['cpf'],cdr_targets_id)
        
        except Exception as error:
            self.log.error("Evidences::alert_lea: Error: " + str(error))
       
        return

    def change_state(self,lea,target_id,cdr_targets_id:int):
        self.log.info("Evidences::change_state")
        self.database.connect()
        query = "UPDATE cdr_targets SET alert=1 where id=" + str(cdr_targets_id)
        (cursor,conn) = self.database.execute_query(query)
        conn.commit()
        self.database.disconnect()
        self.alerted_targets.remove(target_id)
        self.log.info("Evidences::change_state: alerted_targets: " + str(self.alerted_targets))



    def run(self):
        self.log.info("Evidences::run")
        self.targets_thread = threading.Thread(target=self.get_targets)
        self.evidences = threading.Thread(target=self.get_evidences)
        self.targets_thread.start()
        self.evidences.start()

        self.targets_thread.join()
        self.evidences.join()


