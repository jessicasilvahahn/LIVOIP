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
        number = input("Numero do oficio\n")
        autority = input("Autoridade\n")
        date = input("Data da Interceptacao\n")
        print("------- Alvo ------\n")
        target = input("CPF do alvo\n")
        #calcular hash por em quanto
        liid = hash(target)
        li_cadastro = LiCadastro(liid, target, number, autority, date, self.database, self.log)
        print("Deseja sair da interface de registro? (y/n)\n")
        leave = input("")
        return (li_cadastro,leave)
    
