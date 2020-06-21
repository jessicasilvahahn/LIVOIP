#!/opt/li-asterisk/tools/Python-3.6.7
from library.ari.http import Http
from library.ari.http import Method
from library.ari.uris import GET_PCAP
from library.ari.uris import GET_RECORD
from library.smtp.smtp import SmtpGmail
from library.smtp.smtp import MimeType
from scapy.utils import PcapReader
from scapy.all import wrpcap
from scapy.all import rdpcap
from os.path import split
from os import rename
from os.path import join
from os import remove
from queue import Queue
from os.path import exists
from os import makedirs
import threading
import time
from os.path import split
from heapq import merge
import subprocess

class Evidences():
    def __init__(self, iri:dict, cc:dict, email:dict, host:str, log, database, mode:str, path:str):
        self.mode = mode
        self.log = log
        self.path_iri = iri['path_iri']
        if(not exists(self.path_iri)):
            makedirs(self.path_iri)
        self.path_cc = cc['path_cc']
        if(not exists(self.path_cc)):
            makedirs(self.path_cc)
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
        self.path = path

    def create_dir(self, path, dir):
        path_dir = join(path,dir)
        self.log.info("Evidences::create_dir: dir: " + str(path_dir))
        if(not exists(path_dir)):
            makedirs(path_dir)
        return path_dir
    
    def get_iri(self, name:str, new_path:str):
        state = False
        self.log.info("Evidences::get_iri: file: " + str(name))
        host = self.iri_client.server_parameters['host'] + ':' + self.iri_client.server_parameters['port']
        url = GET_PCAP.format(host) + "?file=" + str(name)
        (code, json, response) = self.iri_client.http_request(Method.GET,url,True)
        self.log.info("Evidences::get_iri: Status code: " + str(code))
        if(code == 200):
            name_new_pcap = name
            path_new_pcap = new_path
            name = name + '.A'
            self.log.info("Evidences::get_iri: Trying save file: " + str(name))
            new_path = join(new_path,name)
            pcap_a = new_path
            file = open(new_path, 'wb')
            for chunk in response.iter_content(self.iri_buffer):
                file.write(chunk)
            file.close()
            proxy = name_new_pcap + '.B'
            new_path = join((split(new_path))[0], proxy)
            pcap_b = new_path
            state = self.get_iri_proxy(proxy,new_path)
            if(state):
                state = self.join_pcap(pcap_a, pcap_b, path_new_pcap, name_new_pcap)
        
        self.log.info("Evidences::get_iri: state: " + str(state))
        return state

    def get_iri_proxy(self, name:str,new_path:str):
        state = False
        try:
            self.log.info("Evidences::get_iri_proxy: " + str(name))
            host = self.iri_client.server_parameters['host'] + ':' + self.iri_client.server_parameters['port']
            url = GET_PCAP.format(host) + "?file=" + str(name)
            (code, json, response) = self.iri_client.http_request(Method.GET,url,True)
            self.log.info("Evidences::get_iri_proxy: Status code: " + str(code))
            if(code == 200):
                self.log.info("Evidences::get_iri_proxy: Trying save file: " + str(name))
                file = open(new_path, 'wb')
                for chunk in response.iter_content(self.iri_buffer):
                    file.write(chunk)
                file.close()
                state = True
            
            self.log.info("Evidences::get_iri_proxy: state: " + str(state))
        except Exception as error:
            self.log.error("Evidences::get_iri_proxy: Error: " + str(error))
        
        return state

    
    def join_pcap(self, pcap_a, pcap_b, path, name):
        try:
            self.log.info("Evidences::join_pcap: files: " + str(pcap_a) + ', ' + str(pcap_b))
            pcap_a = self.reader_pcap(pcap_a)
            pcap_b = self.reader_pcap(pcap_b)
            join_pcaps = merge(pcap_a,pcap_b)
            new_pcap = sorted(join_pcaps, key=lambda timestamp: timestamp.time)
            new_path = join(path,name)
            self.log.info("Evidences::join_pcap: Trying save pcap: " + str(new_path))
            wrpcap(new_path, new_pcap, append=True)
            return True

        except Exception as error:
            self.log.error("Evidences::join_pcap: Error: " + str(error))
            return False
        
    def reader_pcap(self, name:str):
        self.log.info("Evidences::reader_pcap: file: " + name)
        packets = rdpcap(name)  
        return packets

    def get_cc(self,name:str,new_path:str):
        state = False
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
            state = True
        
        self.log.info("Evidences::get_cc: state: " + str(state))
        return state

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
                        
                        self.alerted_targets.append(id)
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
                    new_path_cc = self.create_dir(self.path_cc,targets[0])
                    new_path_cc = join(new_path_cc,cc)
                    state_iri = self.get_cc(cc,new_path_cc)
                    state_cc = self.get_iri(iri,new_path_iri)
                    self.log.debug("Evidences::get_evidences: states: " + str(state_iri) + ' ' + str(state_cc))
                    if(state_iri and state_cc):
                        self.log.debug("Evidences::get_evidences: evidences (iri and cc) founded!")
                        urls = {'url_iri': url_iri + '?file=' + str(iri) + "&target=" + str(targets[0]),'url_cc': url_cc + '?file=' + str(cc) + "&target=" + str(targets[0]), 'cpf': targets[0]}
                        self.alert_lea((targets[1])['lea'],urls,(targets[1])['cdr_targets_id'],iri,cc)
                    else:
                        self.alerted_targets.remove((targets[1])['cdr_targets_id'])
                        self.log.warning("Evidences::get_evidences: evidences (iri and cc) not found")
            self.log.info("Evidences::get_evidences: Sleeping ... ")
            time.sleep(3)

    def abnt(self,lea:int, iri:str, cc:str, target:str):
        self.log.info("Evidences::abnt")
        user = None
        password = None
        stdout = None
        stderr = None
        #criar diretorio
        lea_dir = join(self.path_iri,str(lea))
        self.log.info("Evidences::abnt: Trying create lea dir: " + str(lea_dir))
        if(not exists(lea_dir)):
            makedirs(lea_dir)
        
            query = "SELECT user,password from lea where id=" + str(lea)
            (cursor,conn) = self.database.execute_query(query)
            (user,password) = cursor.fetchone()
            self.log.debug("Evidences::abnt: user, password: " + str(user) + "," + str(password))
            if(user and password):
                self.log.info("Evidences::abnt: Trying create user: " + str(user))
                #criar usuário
                cmd = "useradd -G group_sftp -d " + str(lea_dir) + " " + str(user)
                process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (stdout, stderr) = process.communicate()
                if(stderr):
                    self.log.error("Evidences::abnt: error to create lea user: " + str(stderr))
                    return False
                
                self.log.info("Evidences::abnt: stdout: " + str(stdout))
                self.log.debug("Evidences::abnt: Trying change password: " + str(password))
                cmd = "echo \"" + str(user) + ":" + str(password) + "\" | chpasswd"
                process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                (stdout, stderr) = process.communicate()
                if(stderr):
                    self.log.error("Evidences::abnt: error to update password: " + str(stderr))
                    return False

        #mover arquivos para o diretorio
        self.log.debug("Evidences::abnt: Trying move files")
        iri_file = join(self.path_iri + '/' + target, iri)
        cc_file = join(self.path_cc + '/' + target,cc)
        cmd = "cp -p " + str(iri_file) + " " + str(cc_file) + " " + str(lea_dir)
        process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        if(stderr):
            self.log.error("Evidences::abnt: error: " + str(stderr))
            return False

        return True


    def alert_lea(self, leas:list, urls:dict,cdr_targets_id:int,iri,cc):
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
                content = "<p>Prezado (a) Vossa Excelencia, foi constatado em nosso sistema que o investigado abaixo fez uma ligacao. </p> <br> <p> Alvo: " + urls['cpf'] + "<p><br> <p> Pcap: <a href=\"" + urls['url_iri'] + "\">" + urls['cpf'] + ".pcap" + "</a> <p> <br> <p>Audio: <a href=\"" + urls['url_cc'] + "\">" + urls['cpf'] + ".wav" + "</a><p>"
                if(self.mode == "abnt"):
                    if(not self.abnt(lea,iri,cc,urls['cpf'])):
                        return

                    host = self.host.split(':')
                    self.host = host[0]         
                    content = "<p>Prezado (a) Vossa Excelencia, foi constatado em nosso sistema que o investigado abaixo fez uma ligacao. </p> <br> <p> Alvo: " + urls['cpf'] + "<p><br> <p> Pcap: " + str(iri) + "<p> <br> <p>Audio: " + str(cc) + "<p> <br> Para ter acesso a essas evidencias acesse o servidor " + str(self.host) + " por sftp atraves da porta 2222"
                
                subject = "[Investigacao] ALERT: Novas evidencias do alvo " + str(urls['cpf'])
                self.log.info("Evidences::alert_lea: Content: " + str(content) + " ,subject: " + str(subject))
                self.email.send(email,subject,content)
                self.change_state(lea,urls['cpf'],cdr_targets_id)

            self.log.info("Evidences::alert_lea: Trying remove files") 
            iri_file = join(self.path_iri + '/' + urls['cpf'], iri)
            cc_file = join(self.path_cc + '/' + urls['cpf'],cc)
            cmd = "rm " + str(iri_file) + " " + str(cc_file)
            process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdout, stderr) = process.communicate()
            if(stderr):
                self.log.error("Evidences::alert_lea: error: " + str(stderr))
            
            self.log.info("Evidences::alert_lea: Trying chmod dir: " + str(self.path)) 
            cmd = "chmod 755 -R " + str(self.path)
            process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdout, stderr) = process.communicate()
            if(stderr):
                self.log.error("Evidences::alert_lea: error: " + str(stderr))
        
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
        self.alerted_targets.remove(cdr_targets_id)
        self.log.info("Evidences::change_state: alerted_targets: " + str(self.alerted_targets))



    def run(self):
        self.log.info("Evidences::run")
        self.targets_thread = threading.Thread(target=self.get_targets)
        self.evidences = threading.Thread(target=self.get_evidences)
        self.targets_thread.start()
        self.evidences.start()

        self.targets_thread.join()
        self.evidences.join()


