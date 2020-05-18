#!/opt/li-asterisk/tools/Python-3.6.7
class Interface():
    def __init__(self):
        pass

    def li_register(self):
        print("######## Lawful Interception #########\n")
        print("******* Register LI **********\n")
        print("------- Autoridade ------\n")
        lea_user = input("Usuario\n")
        lea_password = input("Senha\n")
        lea_email = input("E-mail\n")
        print("------- Oficio ------\n")
        target = input("CPF do alvo\n")
        day = input("Dia da Interceptacao\n")
        month = input("Mes da Interceptacao\n")
        year = input("Ano da Interceptacao\n")
        date = year + '-' + month + '-' + day
        return (lea_user,lea_password,lea_email,target,date)
        
    def li_unregister(self):
        print("######## Lawful Interception #########\n")
        print("******* Unregister LI **********\n")
        id = input("Id da interceptacao\n")
        return int(id)

