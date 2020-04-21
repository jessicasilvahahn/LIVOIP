#!/opt/li-asterisk/tools/Python-3.6.7
class Oficio():
    def __init__(self, number, autority, date, database, log):
        self.number = number
        self.autority = autority
        self.date = date
        self.db = database
        self.log = log

    def register(self):
        self.log.info("Oficio::register: Trying register oficio")
        sql = '''INSERT INTO oficio(numero_oficio,autoridade,date_li)
            VALUES(?,?,?);'''
        
        self.db.connect()

        parameters = (self.number,self.autority,self.date)
        self.log.info("Oficio::register: Parameters: " + str(parameters))
        (cursor,conn) = self.db.execute_query(sql,parameters)
        conn.commit()
        self.log.info("Oficio::register: Oficio registered")

    def get_oficios(self):
        self.log.info("Oficio::get_oficios: Trying get all oficios")
        oficios = []
        sql = '''select * from oficio;'''
        self.db.connect()
        (cursor,conn) = self.db.execute_query(sql,None)
        oficios = cursor.fetchall()
        self.log.info("Oficio::get_oficios: Oficios: " + str(oficios))
        return oficios

    def get_oficio(self, oficio):
        self.log.debug("Oficio::get_oficio: Trying get oficio: " + str(oficio))
        number = None
        sql = '''select numero_oficio from oficio where numero_oficio = ?'''
        self.db.connect()
        parameters = [oficio]
        (cursor,conn) = self.db.execute_query(sql, parameters)
        number = cursor.fetchone()
        self.log.info("Oficio::get_oficio: Oficio: " + str(number))
        return number


