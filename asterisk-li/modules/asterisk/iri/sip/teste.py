import re

txt = '''INVITE sip:bob@192.168.25.116:5060 SIP/2.0
Via: SIP/2.0/UDP 192.168.25.3:59579;branch=z9hG4bK.0FnzE-nBz;rport
From: <sip:alice@192.168.25.116>;tag=f3wEV1LzB
To: sip:bob@192.168.25.116
CSeq: 20 INVITE
Call-ID: CNKVBJgNGj
Max-Forwards: 70
Supported: replaces, outbound, gruu
Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, NOTIFY, MESSAGE, SUBSCRIBE, INFO, UPDATE
Content-Type: application/sdp
Content-Length: 519
Contact: <sip:alice@192.168.25.3:59579;transport=udp>;expires=3600;+sip.instance="<urn:uuid:c23fe19c-6a47-004e-be0c-d1ec5af55c75>"
User-Agent: LinphoneAndroid/4.2 (Moto G Play) LinphoneSDK/4.3 (tags/4.3^0)

v=0
o=alice 2053 3360 IN IP4 192.168.25.3
s=Talk
c=IN IP4 192.168.25.3
t=0 0
a=rtcp-xr:rcvr-rtt=all:10000 stat-summary=loss,dup,jitt,TTL voip-metrics
m=audio 7078 RTP/AVP 96 97 98 0 8 18 101 99 100
a=rtpmap:96 opus/48000/2
a=fmtp:96 useinbandfec=1
a=rtpmap:97 speex/16000
a=fmtp:97 vbr=on
a=rtpmap:98 speex/8000
a=fmtp:98 vbr=on
a=fmtp:18 annexb=yes
a=rtpmap:101 telephone-event/48000
a=rtpmap:99 telephone-event/16000
a=rtpmap:100 telephone-event/8000
a=rtcp-fb:* trr-int 1000
a=rtcp-fb:* ccm tmmbr'''

#Check if the string starts with 'hello':

x = re.search("From:", txt)
if (x):
  #x = re.search("Call-ID:", txt)
  s = x.string
  print(x)
  #print(x.span())
  span = x.span()
  uri_from = s[span[1]:]
  split = re.split('\n',uri_from)
  split2 = re.split(';',split[0])
  print(split2[0])
  split3 = re.split(':',split2[0])
  print(split3)
  uri = re.split('@',split3[1])
  print(uri[0]) 
  
else:
  print("No match")
  
  
x = re.search("To:", txt)
if (x):
  #x = re.search("Call-ID:", txt)
  s = x.string
  print(x)
  #print(x.span())
  span = x.span()
  uri_from = s[span[1]:]
  split = re.split('\n',uri_from)
  split2 = re.split(';',split[0])
  print(split2[0])
  split3 = re.split(':',split2[0])
  print(split3)
  uri = re.split('@',split3[1])
  print(uri[0]) 
  
else:
  print("No match")
