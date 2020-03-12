#!/opt/li-asterisk/tools/Python-3.6.7
from modules.database.li_cadastro import LiCadastro
class Interface():
    def __init__(self, log, database):
        self.log = log
        self.database = database

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
        li_cadastro = LiCadastro(liid, target, number, autority, date, self.database, self.log)
        return li_cadastro
    
