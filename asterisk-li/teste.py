#!/usr/bin/python3
from modules.ari.recourses import Recourses
from modules.ari.http import Http

r = Recourses("172.17.0.1", "8088", "http")
r.build_uri()
uris = r.uri
print("URIs: ", uris)

http = Http(r, "asterisk", "2604", 120)
code, response = http.get(uris["get_channel"])
print(code, response)