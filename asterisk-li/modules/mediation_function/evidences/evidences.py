#!/opt/li-asterisk/tools/Python-3.6.7
from library.ari.http import Http
from library.ari.http import Method
from library.ari.uris import GET_PCAP
from library.ari.uris import GET_RECORD
from library.ari.uris import GET_IRI
from library.ari.uris import GET_CC
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
import json
from library.sftp.sftp import Sftp
from modules.asterisk.events.asterisk import Record

class Evidences():
    def __init__(self, iri:dict, cc:dict, email:dict, host:str, log, database, path:str):
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
    
    def get_iri(self,call_id,interception_id,new_path_iri):
        state = False
        interception_id = str(interception_id)
        iri_name = None
        proxy_name = None
        self.log.info("Evidences::get_iri: call_id: " + str(call_id) + " interception_id: " + interception_id)
        iri_name = self.get_file_name(call_id,interception_id,"iri")
        new_pcap = None
        if(iri_name):
            proxy_name = iri_name['proxy']
            iri_name = iri_name['file']
            host = self.iri_client.server_parameters['host'] + ':' + self.iri_client.server_parameters['port']
            url = GET_PCAP.format(host) + "?file=" + str(iri_name)
            (code, json, response) = self.iri_client.http_request(Method.GET,url,True,None)
            self.log.info("Evidences::get_iri: Status code: " + str(code))
            self.log.info("Evidences::get_iri: Response: " + str(response))
            if(code == 200):
                self.log.info("Evidences::get_iri: Trying save file: " + str(iri_name))
                new_path = join(new_path_iri,iri_name + '.A')
                pcap_a = new_path
                file = open(pcap_a, 'wb')
                for chunk in response.iter_content(self.iri_buffer):
                    file.write(chunk)
                file.close()
                proxy = iri_name + '.B'
                new_path = join(new_path_iri, proxy)
                pcap_b = new_path
                state = self.get_iri_proxy(proxy_name,new_path)
                if(state):
                    new_pcap = join(new_path_iri,iri_name)
                    state = self.join_pcap(pcap_a, pcap_b, new_pcap)
        
        self.log.info("Evidences::get_iri: state: " + str(state))
        return (state,iri_name)

    def get_iri_proxy(self, name:str,new_path:str):
        state = False
        try:
            self.log.info("Evidences::get_iri_proxy: " + str(name))
            host = self.iri_client.server_parameters['host'] + ':' + self.iri_client.server_parameters['port']
            url = GET_PCAP.format(host) + "?file=" + str(name)
            (code, json, response) = self.iri_client.http_request(Method.GET,url,True,None)
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

    
    def join_pcap(self, pcap_a, pcap_b, path):
        try:
            self.log.info("Evidences::join_pcap: files: " + str(pcap_a) + ', ' + str(pcap_b))
            pcap_a = self.reader_pcap(pcap_a)
            pcap_b = self.reader_pcap(pcap_b)
            join_pcaps = merge(pcap_a,pcap_b)
            new_pcap = sorted(join_pcaps, key=lambda timestamp: timestamp.time)
            self.log.info("Evidences::join_pcap: Trying save pcap: " + str(path))
            wrpcap(path, new_pcap, append=True)
            return True

        except Exception as error:
            self.log.error("Evidences::join_pcap: Error: " + str(error))
            return False
        
    def reader_pcap(self, name:str):
        self.log.info("Evidences::reader_pcap: file: " + name)
        packets = rdpcap(name)  
        return packets

    def get_file_name(self, call_id, interception_id, type_file):
        self.log.info("Evidences::get_file_name")
        file_name = None
        data = json.dumps({"call_id":call_id, "interception_id":interception_id})
        url = GET_CC.format(self.cc_client.server_parameters['host'] + ':' + self.iri_client.server_parameters['port'])
        client = self.cc_client
        if(type_file == 'iri'):
            url = GET_IRI.format(self.iri_client.server_parameters['host'] + ':' + self.iri_client.server_parameters['port'])
            client = self.iri_client

        (code, response_json, response) = client.http_request(Method.POST,url,False,{'Content-Type':'application/json'},data)
        self.log.debug("Evidences::get_file_name: code response: " + str(code))
        if(code == 200):
            self.log.debug("Evidences::get_file_name: response_json: " + str(response_json))
            file_name = response_json
            self.log.info("Evidences::get_file_name: file: " + str(file_name))

        return file_name
    
    def get_cc(self,call_id,interception_id,new_path_cc):
        state = False
        interception_id = str(interception_id)
        cc_name = None
        self.log.info("Evidences::get_cc: call_id: " + str(call_id) + " interception_id: " + interception_id)
        cc_name = self.get_file_name(call_id,interception_id,"cc")
        self.log.debug("Evidences::get_cc: cc name: " + str(cc_name))
        if(cc_name):
            cc_name = cc_name["file"] + Record.FORMAT.value
            host = self.cc_client.server_parameters['host'] + ':' + self.cc_client.server_parameters['port']
            self.log.info("Evidences::get_cc: host: " + str(host))
            url = GET_RECORD.format(host,cc_name)
            self.log.info("Evidences::get_cc: url: " + str(url))
            (code, json, response) = self.cc_client.http_request(Method.GET,url,True,None)
            self.log.info("Evidences::get_cc: Status code: " + str(code))
            self.log.info("Evidences::get_cc: Response: " + str(response))
            if(code == 200):
                new_path = join(new_path_cc,cc_name)
                self.log.info("Evidences::get_cc: Trying save file: " + str(new_path))
                file = open(new_path, 'wb')
                for chunk in response.iter_content(self.cc_buffer):
                    file.write(chunk)
                file.close()
                state = True
        
        self.log.info("Evidences::get_cc: state: " + str(state))
        return (state,cc_name)

    def get_targets(self):
        while(True):
            #pegar do banco pela cdr e associar o target e a autoridade
            self.log.info("Evidences::get_targets")
            targets_dict = {}
            oficios = None
            cpf = ""
            id = None
            targets = None
            lea = None
            call_id = None
            query = "SELECT target_id,id,cdr_id from cdr_targets where alert=0;"
            self.database.connect()
            (cursor,conn) = self.database.execute_query(query)
            if(cursor):
                targets = cursor.fetchall()
                self.log.info("Evidences::get_targets: targets: " + str(targets))
                
            if(targets):
                for cpf,id,cdr_id in targets:
                    self.log.debug("Evidences::get_targets: " + str(cpf) + str(id) + str(cdr_id))
                    if(not id in self.alerted_targets):

                        self.alerted_targets.append(int(id))
                        self.log.info("Evidences::get_targets: alerted_targets: " + str(self.alerted_targets))
                        query = "SELECT id,oficio from li where target_id=\'" + str(cpf) + "\' and flag=\'A\'"
                        (cursor,conn) = self.database.execute_query(query)
                        oficios = cursor.fetchall()
                        self.log.info("Evidences::get_targets: oficios: " + str(oficios))
                        if(oficios):
                            for interception_id,oficio in oficios:
                                query = "SELECT lea from oficio where id=" + str(oficio)
                                (cursor,conn) = self.database.execute_query(query)
                                lea = cursor.fetchone()
                                if(lea):
                                    lea = lea[0]
                        
                                query = "SELECT call_id from cdr where id=" + str(cdr_id)
                                (cursor,conn) = self.database.execute_query(query)
                                call_id = cursor.fetchone()
                                self.log.info("Evidences::get_targets: call_id: " + str(call_id))
                                if(call_id):
                                    call_id = call_id[0].strip(" ")
                                    targets_dict = {cpf: {'cdr_targets_id': id, 'lea': lea, 'call_id':call_id,'interception_id':interception_id}}
                                    self.log.info("Evidences::get_targets: target: " + str(targets_dict))
                                    self.targets.put(targets_dict)

            self.database.disconnect()
            self.log.info("Evidences::get_targets: Sleeping ... ")
            time.sleep(4)

    def get_evidences(self):
        while(True):
            new_path_iri = None
            new_path_cc = None
            cpf = None
            call_id = None
            interception_id = None
            lea = None
            self.log.info("Evidences::get_evidences")
            if(not self.targets.empty()):
                targets = self.targets.get()
                for targets in targets.items():
                    cpf = targets[0]
                    call_id = (targets[1])['call_id']
                    interception_id = (targets[1])['interception_id']
                    lea = (targets[1])['lea']
                    cdr_targets_id = (targets[1])['cdr_targets_id']
                    new_path_iri = self.create_dir(self.path_iri,cpf)
                    new_path_cc = self.create_dir(self.path_cc,cpf)
                    (state_cc,cc_name) = self.get_cc(call_id,interception_id,new_path_cc)
                    (state_iri,iri_name) = self.get_iri(call_id,interception_id,new_path_iri)
                    self.log.debug("Evidences::get_evidences: states: " + str(state_iri) + ' ' + str(state_cc))
                    if(state_iri and state_cc):
                        self.log.debug("Evidences::get_evidences: evidences (iri and cc) founded!")
                        if(self.alert_lea(lea,cpf,iri_name,cc_name)):
                            self.change_state(int(cdr_targets_id))
                            continue

                        self.alerted_targets.remove(cdr_targets_id)
                    else:
                        self.alerted_targets.remove(cdr_targets_id)
                        self.log.warning("Evidences::get_evidences: evidences (iri and cc) not found")
            self.log.info("Evidences::get_evidences: Sleeping ... ")
            time.sleep(3)

    def create_user_sftp(self, lea, user, password, iri, cc, cpf):
        self.log.info("Evidences::create_user_sftp")
        stdout = None
        stderr = None
        #criar diretorio
        lea_dir = join(self.path,"sftp" + str(lea))
        self.log.info("Evidences::create_user_sftp: Trying create lea dir: " + str(lea_dir))
        if(not exists(lea_dir)):
            makedirs(lea_dir)
            self.log.debug("Evidences::create_user_sftp: user, password: " + str(user) + "," + str(password))
            if(user and password):
                self.log.info("Evidences::create_user_sftp: Trying create user: " + str(user))
                #criar usuário
                cmd = "useradd -G group_sftp -d " + str(lea_dir) + " " + str(user)
                process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (stdout, stderr) = process.communicate()
                if(stderr):
                    self.log.error("Evidences::create_user_sftp: error to create lea user: " + str(stderr))
                    return False
                
                self.log.info("Evidences::create_user_sftp: stdout: " + str(stdout))
                self.log.debug("Evidences::create_user_sftp: Trying change password: " + str(password))
                cmd = "echo \"" + str(user) + ":" + str(password) + "\" | chpasswd"
                process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                (stdout, stderr) = process.communicate()
                if(stderr):
                    self.log.error("Evidences::create_user_sftp: error to update password: " + str(stderr))
                    return False

        #mover arquivos para o diretorio
        self.log.debug("Evidences::create_user_sftp: Trying move files")
        iri_file = join(self.path_iri + '/' + cpf, iri)
        cc_file = join(self.path_cc + '/' + cpf,cc)
        cmd = "cp -p " + str(iri_file) + " " + str(cc_file) + " " + str(lea_dir)
        process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        if(stderr):
            self.log.error("Evidences::create_user_sftp: error: " + str(stderr))
            return False

        cmd = "rm " + str(iri_file) + " " + str(cc_file)
        process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        if(stderr):
            self.log.error("Evidences::create_user_sftp: error: " + str(stderr))
            return False
            
        self.log.info("Evidences::create_user_sftp: Trying chmod dir: " + str(self.path)) 
        cmd = "chmod 755 -R " + str(self.path)
        process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        if(stderr):
            self.log.error("Evidences::alert_lea: error: " + str(stderr))
            return False
        
        return True

    def sftp(self,lea,cpf,user,password,ip,port,path,iri,cc):
        self.log.info("Evidences::sftp")
        sftp_session = None
        state = True
        uri = None
        new_name = None
        self.database.connect()
        query = "SELECT uri from target where cpf=\'" + cpf + '\''
        (cursor,conn) = self.database.execute_query(query)
        uri = cursor.fetchone()
        self.database.disconnect()
        uri = uri[0]
        if(ip and path and port):
            sftp_session = Sftp(self.log,ip,int(port),user,password)
            sftp_session.setup()
            state = sftp_session.connect()
            remote_path = join(path,str(uri))
            new_name = join(remote_path,iri)
            if(not sftp_session.remote_dir_exists(path,str(uri))):
                state = sftp_session.create_remote_dir(remote_path)
                
            iri = join(self.path_iri + '/' + cpf, iri)
            self.log.info("Evidences::sftp: src iri: " + str(iri))
            self.log.info("Evidences::sftp: dest iri: " + str(new_name))
            state = sftp_session.send_file(iri,new_name)
            new_name = join(remote_path,cc)
            cc = join(self.path_cc + '/' + cpf, cc)
            self.log.info("Evidences::sftp: src cc: " + str(cc))
            self.log.info("Evidences::sftp: dest cc: " + str(new_name))
            state = sftp_session.send_file(cc,new_name)
            sftp_session.close()

        else:
            state = self.create_user_sftp(lea,user,password,iri,cc,cpf)
            if(not state):
                uri = None
        
        return (uri,state)

    def alert_lea(self,lea,cpf,iri_name,cc_name):
        self.log.info("Evidences::alert_lea")
        ip = None
        port = None
        path = None
        uri = None
        state = True
        try:
            self.database.connect()
            query = "SELECT user,password,email,ip,port,path_sftp from lea where id=" + str(lea)
            (cursor,conn) = self.database.execute_query(query)
            result = cursor.fetchone()
            self.log.debug("Evidences::alert_lea: Result select: " + str(result))
            self.database.disconnect()
            if(result):
                user = result[0]
                password = result[1]
                email = result[2]
                ip = result[3]
                port = result[4]
                path = result[5]
                (uri,state) = self.sftp(lea,cpf,user,password,ip,port,path,iri_name,cc_name)
                self.log.info("Evidences::alert_lea: Lea: " + str(email))
                if(uri and state):
                    host = self.host.split(':')
                    self.host = host[0]         
                    content = "<p>Prezado (a) Vossa Excelencia, foi constatado em nosso sistema que o investigado abaixo fez uma ligacao. </p> <br> <p> Alvo: " + uri + "<p><br> <p> Pcap: " + str(iri_name) + "<p> <br> <p>Audio: " + str(cc_name) + "<p> <br> Para ter acesso a essas evidencias acesse o servidor sftp cadastrado"
                    subject = "[Investigacao] ALERT: Novas evidencias do alvo " + str(uri)
                    self.log.info("Evidences::alert_lea: Content: " + str(content) + " ,subject: " + str(subject))
                    self.email.send(email,subject,content)
                    return True
                    

        except Exception as error:
            self.log.error("Evidences::alert_lea: Error: " + str(error))
            return False

    def change_state(self,cdr_targets_id:int):
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


