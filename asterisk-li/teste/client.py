import requests
import certifi
import json

headers = {'content-type': 'application/json'}

#requests.get("https://localhost:8080",verify=False)

response = requests.post("https://localhost:8080",data=json.dumps({"target": "bob"}),headers=headers,auth=('user', 'pass'),verify=False)

print(str(response))