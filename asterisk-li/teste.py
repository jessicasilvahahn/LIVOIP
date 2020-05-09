import asyncio
from panoramisk import Manager
from panoramisk.message import Message
from scapy.all import sniff
from scapy.all import wrpcap
import re
#f = open("sip.txt", "a")

def function(packet):
    print("Packet")
    if(packet):
    #wrpcap("sip3.pcap", packet, append=True)
    #info = packet.show()
        load = packet.load
        print("layers: " + str(packet.layers()))
        try:
            string = load.decode()
            print(string)
            x = re.findall("^INVITE", string)
            print(x)
            if (x):
                print("YES! We have a INVITE!")
                print(string)
                x = re.search("Call-ID:", string)
                s = x.string
                #print(x.span())
                span = x.span()
                call_id = s[span[1]:]
                split = re.split('\n',call_id)
                print("CALL-ID:" + split[0])
            else:
                print("No match")

            x = re.findall("^BYE", string)
            print(x)
            if (x):
                print("YES! We have a BYE!") 
                print(string)
            else:
                print("No match")
            
            ok = re.findall("^SIP/2.0 200 Ok", string)
            print(ok)
            if(ok):
                x = re.search("Call-ID:", string)
                s = x.string
                #print(x.span())
                span = x.span()
                call_id = s[span[1]:]
                split = re.split('\n',call_id)
                print("200 OK")
                #print(string)
                bye = re.findall("BYE", string)
                if(bye):
                    print("200 OK TEM BYE")
                    print("CALL-ID:" + split[0])
                    print(string)

            x = re.findall("^CANCEL", string)
            print(x)
            if (x):
                print("YES! We have a CANCEL!")
                print(string)
            else:
                print("No match")
        except Exception as error:
            if(packet):
                load = packet.raw()
                print(load)
    
    

    #f.write(string)

	

manager = Manager(loop=asyncio.get_event_loop(),
                  host='192.168.25.24',
                  username='li',
                  secret='li123')
#event = Message({'Event': 'AgentConnect', 'Exten':'alice'})
#Cdr
@manager.register_event('Cdr')
def callback(manager, message):
    '''if "FullyBooted" not in message.event:
        """This will print every event, but the FullyBooted events as these
        will continuously spam your screen"""'''
    print("Cdr")
    print(message)

def main():
    manager.connect()
    try:
        manager.loop.run_forever()
    except KeyboardInterrupt:
        manager.loop.close()


if __name__ == '__main__':
    try:
        main()
        #SIP - porta 5060
        #sniff(iface="wlan0",filter="udp and port 5060", prn=function)
    except KeyboardInterrupt:
        pass
        #f.close()
