#!/opt/li-asterisk/tools/Python-3.6.7
from library.database.database import Database
from library.interception.interception import Status

class Register(Database):

    def __init__(self, log=None, db_name=None):
        pass

    def set(self, log, db_name):
        super().__init__(db_name,log)
        self.log = log

    def search_cpf(self, uri:str):
        cpf = None
        id = None
        result = None
        self.log.info("Register::search_uri: target: " + uri)
        try:
            query = "SELECT id,cpf from uri where uri=\'" + uri + '\''
            (cursor,conn) = self.execute_query(query)
            if(cursor):
                result = cursor.fetchone()
                self.log.debug("Register::search_uri: result: " + str(result))
                if(result):
                    id = result[0]
                    cpf = result[1]
        except Exception as error:
            self.log.error("Register::search_uri: error: " + str(error))
        
        self.disconnect()
        return (id,cpf)

    def search_target(self, uri_id):
        id = None
        self.log.info("Register::search_target: uri id: " + uri_id)
        try:
            query = "SELECT id from target where target=\'" + uri_id + '\''
            (cursor,conn) = self.execute_query(query)
            if(cursor):
                id = cursor.fetchone()
                if(id):
                    id = id[0]
        except Exception as error:
            self.log.error("Register::search_uri: error: " + str(error))
        
        self.disconnect()
        return id

    def add_interception(self, uri:str):
        self.log.info("Register::add_interception: target: " + uri)
        target_id = None
        (uri_id,cpf) = self.search_cpf(uri)
        id_interception = None
        if(cpf):
            flag = Status.ATIVO.value
            if(uri_id):
                target_id = self.search_target(str(uri_id))
                if(not target_id):
                    query = "INSERT INTO target VALUES(?,?)"
                    values = [None,uri_id]
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
            self.log.info("Register::add_interception: target: " + uri + " not found!")
        
        return (id_interception,cpf)

    def inactive_interception(self, id_interception:int):
        self.log.info("Register::inactive_interception: id: " + str(id_interception))
        try:
            self.connect()
            query = "UPDATE interception SET flag=\'" + Status.INATIVO.value + "\' where id=" + str(id_interception)
            (cursor,conn) = self.execute_query(query)
            conn.commit()
            self.disconnect()
            return True
        except Exception as error:
            self.log.error("Register::inactive_interception: error: " + str(error))
            

