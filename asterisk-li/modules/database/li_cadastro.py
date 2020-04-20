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

    def register_li(self):
        self.log.info("LiCadastro::register_li: Trying register Lawful Interception")
        oficio = None
        super().register()
        oficio = super().get_oficio(self.number)
        uri = self.get_uri(self.target)
        if(not uri):
            self.log.warning("LiCadastro::register: URI for target " + str(self.target) + " not found")
            return
        sql = '''INSERT INTO li_cadastro(liid,target,uri,numero_oficio)
            VALUES(?,?,?,?) '''
        
        self.db.connect()

        parameters = [self.liid,self.target,uri[0],oficio[0]]
        self.log.info("LiCadastro::register: Parameters: " + str(parameters))
        (cursor,conn) = self.db.execute_query(sql,parameters)
        conn.commit()
        self.log.info("LiCadastro::register: Lawful Interception registered")

    def register_oficio(self):
        self.log.info("LiCadastro::register_oficio: Trying register Oficio")    
        sql = '''INSERT INTO oficio(numero_oficio,autoridade,date_li)
            VALUES(?,?,?) '''   
        self.db.connect()
        parameters = [super().number,super().autority,super().date]
        self.log.info("LiCadastro::register_oficio: Parameters: " + str(parameters))
        (cursor,conn) = self.db.execute_query(sql,parameters)
        conn.commit()
        self.log.info("LiCadastro::register_oficio: Oficio registered")

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


class CadastroOperadora():
   
    def  __init__(self, cpf, name, uri, contract, database, log):
       self.cpf = cpf
       self.name = name
       self.uri = uri
       self.contract = contract
       self.database = database
       self.log = log

    def register(self):
        self.log.info("LiCadastro::register: Trying register Network Operator")
        sql = '''INSERT INTO operadora(cpf,nome,uri,contrato)
            VALUES(?,?,?,?) '''
        parameters = [self.cpf,self.name, self.uri, self.contract]
        self.database.connect()
        (cursor,conn) = self.database.execute_query(sql,parameters)
        conn.commit()
        self.log.info("LiCadastro::register_oficio: Network Operator registered")


    