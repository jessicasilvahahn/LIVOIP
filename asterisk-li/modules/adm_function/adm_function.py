#!/opt/li-asterisk/tools/Python-3.6.7
from modules.adm_function.user_interface.simple.interface import Interface
from library.database.database import Database
from library.ari.http import Http
from library.ari.http import Method
from library.ari import uris
import json
from enum import Enum
import urllib3


class Action(Enum):
    INSERT = 0
    UPDATE = 1

class Adm(Database):
    def __init__(self, host, port, user, password, timeout, db_name, log):
        self.log = log
        self.interface = Interface()
        super().__init__(db_name,log)
        self.client = Http(host, port, user, password, timeout)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def add_interception(self):
        self.log.info("Adm::add_interception")
        try:
            (lea_user,lea_password,lea_email,sftp_ip,sftp_pah,target,date,lea_port) = self.interface.li_register()
            url = uris.ADD_INTERCEPTION.format(self.client.server_parameters['host'] + ':' + self.client.server_parameters['port'])
            self.log.info("Adm::add_interception: Url: " + url)
            target = {"target":target}
            (code, json_response, response) = self.client.http_request(Method.POST,url,False,{'content-type': 'application/json'},json.dumps(target))
            self.log.info("Adm::add_interception: code: " + str(code) + " json: " + str(json_response))
            if(code == 200):
                interception_id = int(json_response['id'])
                cpf = json_response['cpf']
                self.log.info("Adm::add_interception: interception_id: " + str(interception_id) + " cpf: " + str(cpf))
                self.target(cpf,target['target'])
                lea_id = self.lea(lea_user,lea_password,lea_email,sftp_ip,sftp_pah,lea_port)
                oficio_id = self.oficio(lea_id,date)
                self.li(interception_id,cpf,oficio_id,Action.INSERT,'A')
                self.log.info("Adm::add_interception: interception added")
            else:
                self.log.info("Adm::add_interception: Error to add interception")

        except Exception as error:
            self.log.error("Adm::add_interception: error: " + str(error))

    def inactivate_interception(self):
        self.log.info("Adm::inactivate_interception")
        interceptions = []
        try:
            oficio_id = self.interface.li_unregister()
            url = uris.INACTIVE_INTERCEPTION.format(self.client.server_parameters['host'] + ':' + self.client.server_parameters['port'])
            self.log.debug("Adm::inactivate_interception: url: " + str(url))
            interceptions = self.get_ids_interceptions(oficio_id)
            if(interceptions):
                for id in interceptions:
                    id_interception = {"id_interception":id[0]}
                    self.log.debug("Adm::inactivate_interception: id interception: " + str(id_interception))
                    (code, json_response, response) = self.client.http_request(Method.POST,url,False,{'content-type': 'application/json'},json.dumps(id_interception))
                    self.log.debug("Adm::inactivate_interception: code: " + str(code))
                    if(code == 200):
                        self.li(id[0],None,None,Action.UPDATE,'I')
                    else:
                        self.log.info("Adm::inactivate_interception: Error to inactivate interception")
        except Exception as error:
            self.log.error("Adm::inactivate_interception: error: " + str(error))
    
    def get_uri(self, cpf:str):
        uri = None
        self.log.info("Adm::get_uri")
        self.connect()
        query = "SELECT uri from target where cpf=\'" + cpf + "\'"
        (cursor,conn) = self.execute_query(query)
        if(cursor):
            uri = cursor.fetchone()
            if(uri):
                uri = uri[0]
        self.log.info("Adm::get_uri: uri: " + str(uri))
        self.disconnect()
        return uri

    def target(self, cpf:str, uri:str):
        new_uri = uri
        self.log.info("Adm::target")
        uri = self.get_uri(cpf)
        if(uri):
            self.log.info("Adm::target: cpf is already registered with uri: " + str(uri))
            return
        query = "INSERT INTO target VALUES(?,?)"
        values = [cpf,new_uri]
        self.log.info("Adm::target: values: " + str(values))
        self.connect()
        (cursor,conn) = self.execute_query(query, values)
        conn.commit()
        self.disconnect()
        return

    def lea(self, user, password, email,sftp_ip,sftp_pah,sftp_port):
        self.log.info("Adm::lea")
        query = "INSERT INTO lea VALUES(?,?,?,?,?,?,?)"
        values = [None,user,password,email,sftp_ip,sftp_port,sftp_pah]
        self.connect()
        (cursor,conn) = self.execute_query(query, values)
        conn.commit()
        query = "SELECT MAX(id) from lea"
        (cursor,conn) = self.execute_query(query)
        lea_id = (cursor.fetchone())[0]
        self.disconnect()
        return lea_id

    def oficio(self, lea, date):
        self.log.info("Adm::oficio")
        query = "INSERT INTO oficio VALUES(?,?,?)"
        values = [None,lea,date]
        self.connect()
        (cursor,conn) = self.execute_query(query, values)
        conn.commit()
        query = "SELECT MAX(id) from oficio"
        (cursor,conn) = self.execute_query(query)
        oficio_id = (cursor.fetchone())[0]
        self.disconnect()
        return oficio_id

    def li(self, li_id, cpf, oficio, action, flag):
        self.log.info("Adm::li")
        query = None
        if(action == Action.INSERT):
            query = "INSERT INTO li VALUES(?,?,?,?)"
            values = [li_id, cpf, oficio, flag]
        elif(action == Action.UPDATE):
            query = "UPDATE li SET flag=\'" + flag + "\' where id=" + str(li_id)
            values = None
        self.log.info("Adm::li: query: " + str(query))
        self.connect()
        (cursor,conn) = self.execute_query(query, values)
        conn.commit()
        self.disconnect()

    def get_ids_interceptions(self,oficio_id):
        interceptions = []
        self.log.info("Adm::get_ids_interceptions: Try get interceptions when oficio ids: " + str(oficio_id))
        query = "SELECT id from li where oficio=" + str(oficio_id)
        self.connect()
        (cursor,conn) = self.execute_query(query)
        interceptions = cursor.fetchall()
        self.disconnect()
        return interceptions







    
