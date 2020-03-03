#!/opt/li-asterisk/tools/Python-3.6.7
from modules.database.li_cadastro import LiCadastro
from modules.database import Database
class Interface():
    def __init__(self, log, database_name):
        self.log = log
        self.db_name = database_name

    def li_register(self):
        print("######## Lawful Interception #########\n")
        print("******* Register LI **********\n")
        print("------- Oficio ------\n")
        number = input("Número do oficio\n")
        autority = input("Autoridade\n")
        date = input("Data da Interceptação\n")
        print("------- Alvo ------\n")
        target = input("CPF do alvo\n")
        #calcular hash por em quanto
        liid = hash(target)
        database = Database(self.db_name, self.log)
        li_cadastro = LiCadastro(liid, target, number, autority, date, database, self.log)
        return li_cadastro
    