#!/opt/li-asterisk/tools/Python-3.6.7

class Database():
    def __init__(self, db_name, log):
        self.database_name = db_name
        self.log = log
        self.conn = None

    def connect(self):
        try:
            self.log.info("Database::connect: Trying connect to database: " + str(self.database_name))
            self.conn = sqlite3.connect(self.database_name)
        except Exception as error:
            self.log.error("Database::connect: Error: " + str(error))

    def disconnect(self):
        try:
            self.log.info("Database::disconnect: Trying disconnect to database: " + str(self.database_name))
            self.conn.close()
        except Exception as error:
            self.log.error("Database::disconnect: Error: " + str(error))

    def execute_query(self, query, parameters = None):
        try:
            cursor = None
            executed = None
            self.log.info("Database::execute_query: Trying execute query: " + str(query))
            self.connect()
            cursor = self.conn.cursor()
            if(parameters):
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
        except Exception as error:
            self.log.error("Database::execute_query: Error: " + str(error))
        finally:
            return (cursor,self.conn)



