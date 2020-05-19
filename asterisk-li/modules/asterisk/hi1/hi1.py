#!/opt/li-asterisk/tools/Python-3.6.7
from library.shared.database.database import Database
from library.shared.interception.status import Status

class Hi1(Database):

    def __init__(self, log=None, db_name=None):
        pass

    def set(self, log, db_name):
        super().__init__(db_name,log)
        self.log = log

    def search_target(self, cpf:str):
        uri = None
        self.log.info("Hi1::search_target: target: " + cpf)
        try:
            query = "SELECT uri from operadora where cpf=\'" + cpf + '\''
            self.connect()
            (cursor,conn) = self.execute_query(query)
            uri = cursor.fetchone()
            uri = uri[0]
        except Exception as error:
            self.log.error("Hi1::search_target: error: " + str(error))
        
        self.disconnect()
        return uri

    def add_interception(self, cpf:str):
        self.log.info("Hi1::add_interception: target: " + cpf)
        uri = self.search_target(cpf)
        id_interception = None
        if(uri):
            flag = '\'' + Status.ATIVO.value + '\''
            query = "INSERT INTO target VALUES(?,?)"
            values = [None,uri]
            self.connect()
            (cursor,conn) = self.execute_query(query,values)
            conn.commit()
            query = "SELECT MAX(id) from target;"
            (cursor,conn) = self.database.execute_query(query)
            target_id = cursor.fetchone()
            target_id = target_id[0]
            query = "INSERT INTO interception VALUES(?,?,?)"
            values = [None,target_id,flag]
            (cursor,conn) = self.execute_query(query,values)
            conn.commit()
            query = "SELECT MAX(id) from interception;"
            (cursor,conn) = self.database.execute_query(query)
            id_interception = (cursor.fetchone())[0]
            self.disconnect()
        else:
            self.log.info("Hi1::add_interception: target: " + cpf + " not found!")
        
        return (id_interception,uri)

    def inactive_interception(self, id_interception:int):
        self.log.info("Hi1::inactive_interception: id: " + str(id_interception))
        try:
            self.connect()
            query = "UPDATE interception SET flag=\'" + Status.INATIVO.value + "\' where id=" + str(id_interception)
            (cursor,conn) = self.database.execute_query(query)
            conn.commit()
            self.disconnect()
            return True
        except Exception as error:
            self.log.error("Hi1::inactive_interception: error: " + str(error))
            

