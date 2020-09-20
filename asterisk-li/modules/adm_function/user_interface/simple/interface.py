#!/opt/li-asterisk/tools/Python-3.6.7
class Interface():
    def __init__(self):
        pass

    def lea(self):
        ip = None
        path = None
        print("------- LEA ------\n")
        lea_user = input("Usuario\n")
        lea_password = input("Senha\n")
        lea_email = input("E-mail\n")
        lea_port = input("SFTP port server\n")
        print("Entrega por SFTP?\n")
        sftp = input("Y or N\n")
        if(sftp == 'Y' or sftp == 'y'):
            print("****SFTP*****\n")
            ip = input("IP\n")
            path = input("Path\n")
        
        return (lea_user,lea_password,lea_email,ip,path,int(lea_port))

    def oficio(self):
        print("------- Oficio ------\n")
        target = input("Identificador do alvo\n")
        day = input("Dia da Interceptacao\n")
        month = input("Mes da Interceptacao\n")
        year = input("Ano da Interceptacao\n")
        date = year + '-' + month + '-' + day

        return (target,date)


    def li_register(self):
        target = None
        date = None
        lea_user = None
        lea_password = None
        lea_email = None
        lea_port = None
        print("######## Asterisk Lawful Interception (ALI) #########\n")
        print("******* Register LI **********\n")
        
        (target,date) = self.oficio()
        (lea_user,lea_password,lea_email,ip,path,lea_port) = self.lea()
        
        return (lea_user,lea_password,lea_email,ip,path,target,date,lea_port)
        
    def li_unregister(self):
        print("######## Lawful Interception #########\n")
        print("******* Unregister LI **********\n")
        id = input("Id do oficio\n")
        return int(id)

