#!/opt/li-asterisk/tools/Python-3.6.7

class Interface():
    def __init__(self):
        self.li_cadastro = None

    def li_register(self):
        print("######## Lawful Interception #########\n")
        print("******* Register LI **********\n")
        print("------- Oficio ------\n")
        number = input("Número do oficio\n")
        autority = input("Autoridade\n")
        date = input("Data da Interceptação\n")
        print("------- Alvo ------\n")
        target = input("CPF do alvo\n")
    