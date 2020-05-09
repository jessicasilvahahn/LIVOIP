#!/opt/li-asterisk/tools/Python-3.6.7
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

class MimeType(Enum):
    
    TEXT = 'plain'
    HTML = 'html'

class SmtpGmail():
    def __init__(self, log):
        self.log = log
        self.mime_type = None
        self.server_address = None
        self.server_passwd = None

    def setup(self,server_address:str, server_passwd:str, mime_type:MimeType):
        self.mime_type = mime_type
        self.server_address = server_address
        self.server_passwd = server_passwd
    
    def send(self, address:str, subject:str, content:str):
        self.log.info("Smtp::send: Trying send e-mail: " + content)
        try:
            message = MIMEMultipart()
            message.attach(MIMEText(content, self.mime_type))
            message['From'] = self.server_address
            message['To'] = address
            message['Subject'] = subject
            #porta do gmail usando ttls
            session = smtplib.SMTP('smtp.gmail.com', 587) 
            session.starttls()
            session.login(self.server_address, self.server_passwd)
            text = message.as_string()
            session.sendmail(self.server_address, address, text)
            session.quit()
        except Exception as error:
            self.log.error("Smtp::send: Error: " + error)
        




    