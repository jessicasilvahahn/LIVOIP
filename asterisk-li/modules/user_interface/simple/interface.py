#!/opt/li-asterisk/tools/Python-3.6.7
from modules.database.li_cadastro import LiCadastro
from modules.database.li_cadastro import CadastroOperadora
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
    
    def network_operator_register(self):
        print("######## Contrato #########\n")
        nome = input("Nome\n")
        cpf = input("CPF\n")
        print("URI = nome + -  + CPF")
        uri = str(nome) + '-' + str(cpf)
        contrato = input("numero do contrato\n")
        li_network_operator = CadastroOperadora(cpf, nome, uri, contrato, self.database, self.log)
        print("Deseja sair da interface de registro? (y/n)\n")
        leave = input("")
        return (li_network_operator,leave)
    

