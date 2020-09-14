#!/opt/li-asterisk/tools/Python-3.6.7

class Cdr():
    def __init__(self,call_id,answer_time, call_duration, end_call_time, call_start_time, source_uri, destination_uri, database,log):
        self.log = log
        self.call_id = call_id
        self.answer_time = answer_time
        self.call_duration = call_duration
        self.end_call_time = end_call_time
        self.call_start_time = call_start_time
        self.source_uri = source_uri
        self.destination_uri = destination_uri
        self.database = database

    def cdr(self):
        self.log.info("Cdr::cdr: Trying insert values to cdr table")
        query = '''INSERT INTO cdr VALUES(?,?,?,?,?,?,?,?)'''
        values = [None,self.answer_time,self.call_duration,self.end_call_time,self.call_start_time,self.source_uri,self.destination_uri,self.call_id]
        self.database.connect()
        (cursor,conn) = self.database.execute_query(query,values)
        conn.commit()
        #pegar ultimo id
        query = "SELECT MAX(id) from cdr;"
        (cursor,conn) = self.database.execute_query(query)
        cdr_id = cursor.fetchone()
        self.log.info("Cdr::cdr: Cdr id: " + str(cdr_id))
        if(cdr_id):
            cdr_id = cdr_id[0]
        
        self.database.disconnect()
        return cdr_id
    
    def cdr_targets(self, target, cdr):
        self.log.info("Cdr::cdr_targets: Trying insert values to cdr_targets table")
        query = '''INSERT INTO cdr_targets VALUES(?,?,?,?)'''
        values = [None,target,cdr,0]
        (cursor,conn) = self.database.execute_query(query,values)
        conn.commit()
        return

    def save(self):
        self.log.info("Cdr::save: Trying save Cdr")
        target_source_uri = None
        target_dest_uri = None
        cdr_id = None
        #salvar apenas o cdr que tem target (uri)
        #primeiro verifico source
        query = "SELECT cpf from target where uri=\'" + str(self.source_uri) + '\''
        self.database.connect()
        (cursor,conn) = self.database.execute_query(query)
        target_source_uri = cursor.fetchone()
        if(target_source_uri):
            cdr_id = self.cdr()
            target_source_uri = target_source_uri[0]
            self.cdr_targets(target_source_uri,cdr_id)
        #verifico destination
        query = "SELECT cpf from target where uri=\'" + str(self.destination_uri) + '\''
        (cursor,conn) = self.database.execute_query(query)
        target_dest_uri = cursor.fetchone()
        if(not cdr_id):
            cdr_id = self.cdr()
        if(target_dest_uri):
            target_dest_uri = target_dest_uri[0]
            self.cdr_targets(target_dest_uri,cdr_id)

        if(not target_source_uri and not target_dest_uri):
            return False
        
        self.database.disconnect()
        return True