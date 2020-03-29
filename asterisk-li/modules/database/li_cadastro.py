#!/opt/li-asterisk/tools/Python-3.6.7
from modules.database.oficio import Oficio

class LiCadastro(Oficio):
    def __init__(self, liid, target, number, autority, date, database, log):
        super().__init__(number, autority, date, database, log)
        self.liid = liid
        self.target = target
        self.db = database
        self.log = log
        self.number = number

    def register(self):
        self.log.info("LiCadastro::register: Trying register Lawful Interception")
        oficio = None
        super().register()
        oficio = super().get_oficio(self.number)
        uri = self.get_uri(self.target)
        sql = '''INSERT INTO li_cadastro(liid,target,uri,numero_oficio)
            VALUES(?,?,?,?) '''
        
        self.db.connect()

        parameters = [self.liid,self.target,uri,oficio[0]]
        self.log.info("LiCadastro::register: Parameters: " + str(parameters))
        (cursor,conn) = self.db.execute_query(sql,parameters)
        conn.commit()
        self.log.info("LiCadastro::register: Lawful Interception registered")

    def get_oficios(self):
        self.log.info("LiCadastro::register: Trying get all LI")
        li = []
        sql = '''select * from li_cadastro'''
        self.db.connect()
        (cursor,conn) = self.db.execute_query(sql)
        li = cursor.fetchall()
        self.log.info("LiCadastro::register: li: " + str(li))
        return oficios

    def get_uri(self, cpf):
        self.log.info("LiCadastro::get_uri: Trying get uri with cpf: " + str(cpf))
        uri = None
        sql = '''select uri from operadora where cpf = ?'''
        self.db.connect()
        parameters = [cpf]
        (cursor,conn) = self.db.execute_query(sql, parameters)
        uri = cursor.fetchone()
        self.log.info("LiCadastro::get_uri: URI: " + str(uri))
        return uri
