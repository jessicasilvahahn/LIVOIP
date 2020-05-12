#!/opt/li-asterisk/tools/Python-3.6.7

class Operadora():
    def __init__(self, cpf, name, uri, contract, database, log):
        self.cpf = cpf
        self.name = name
        self.uri = uri
        self.contract = contract
        self.db = database
        self.log = log

    def register(self):
        self.log.info("Operadora::register: Trying register operadora")
        sql = '''INSERT INTO operadora(cpf,uri,nome,contrato)
            VALUES(?,?,?,?) '''
        
        self.db.connect()

        parameters = (self.cpf,self.uri, self.nome,self.contrato)
        self.log.info("Oficio::register: Parameters: " + str(parameters))
        (cursor,conn) = self.db.execute_query(sql,parameters)
        conn.commit()
        self.log.info("Operadora::register: Operadora registered")

    def get_users(self):
        self.log.info("Operadora::get_users: Trying get all users")
        users = []
        sql = '''select * from operadora'''
        self.db.connect()
        (cursor,conn) = self.db.execute_query(sql)
        users = cursor.fetchall()
        self.log.info("Operadora::get_users: Users: " + str(users))
        return users