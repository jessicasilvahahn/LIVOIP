#!/usr/bin/python3
from modules.ari.recourses import Recourses
from modules.ari.http import Http
from modules.ari.http import Method

r = Recourses("172.17.0.1", "8088", "http")
r.build_uri()
uris = r.uri
print("URIs: ", uris)

http = Http(r, "asterisk", "2604", 120)
code, response = http.http_request(Method.GET, uris["channels"])
print(code, response)