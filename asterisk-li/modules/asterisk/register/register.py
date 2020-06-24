#!/opt/li-asterisk/tools/Python-3.6.7
from library.database.database import Database
from library.interception.status import Status

class Register(Database):

    def __init__(self, log=None, db_name=None):
        pass

    def set(self, log, db_name):
        super().__init__(db_name,log)
        self.log = log

    def search_uri(self, cpf:str):
        uri = None
        self.log.info("Register::search_uri: target: " + cpf)
        try:
            query = "SELECT uri from uri where cpf=\'" + cpf + '\''
            (cursor,conn) = self.execute_query(query)
            if(cursor):
                uri = cursor.fetchone()
                if(uri):
                    uri = uri[0]
        except Exception as error:
            self.log.error("Register::search_uri: error: " + str(error))
        
        self.disconnect()
        return uri

    def search_target(self, uri:str):
        id = None
        self.log.info("Register::search_target: uri: " + uri)
        try:
            query = "SELECT id from target where target=\'" + uri + '\''
            (cursor,conn) = self.execute_query(query)
            if(cursor):
                id = cursor.fetchone()
                if(id):
                    id = id[0]
        except Exception as error:
            self.log.error("Register::search_uri: error: " + str(error))
        
        self.disconnect()
        return id

    def add_interception(self, cpf:str):
        self.log.info("Register::add_interception: target: " + cpf)
        target_id = None
        uri = self.search_uri(cpf)
        id_interception = None
        if(uri):
            flag = Status.ATIVO.value
            target_id = self.search_target(uri)
            if(not target_id):
                query = "INSERT INTO target VALUES(?,?)"
                values = [None,uri]
                self.connect()
                (cursor,conn) = self.execute_query(query,values)
                conn.commit()
                query = "SELECT MAX(id) from target;"
                (cursor,conn) = self.execute_query(query)
                target_id = cursor.fetchone()
                target_id = target_id[0]
            
            query = "INSERT INTO interception VALUES(?,?,?)"
            values = [None,target_id,flag]
            (cursor,conn) = self.execute_query(query,values)
            conn.commit()
            query = "SELECT MAX(id) from interception;"
            (cursor,conn) = self.execute_query(query)
            id_interception = (cursor.fetchone())[0]
            self.disconnect()
        else:
            self.log.info("Register::add_interception: target: " + cpf + " not found!")
        
        return (id_interception,uri)

    def inactive_interception(self, id_interception:int):
        self.log.info("Register::inactive_interception: id: " + str(id_interception))
        try:
            self.connect()
            query = "UPDATE interception SET flag=\'" + Status.INATIVO.value + "\' where id=" + str(id_interception)
            (cursor,conn) = self.database.execute_query(query)
            conn.commit()
            self.disconnect()
            return True
        except Exception as error:
            self.log.error("Register::inactive_interception: error: " + str(error))
            

