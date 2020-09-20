import requests
import certifi
import json

headers = {'content-type': 'application/json'}

#requests.get("https://localhost:8080",verify=False)

response = requests.get("https://172.17.0.1:8089/ari/channels",auth=('asterisk','123'),verify=False)

print(str(response))
