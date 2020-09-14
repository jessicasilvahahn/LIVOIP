#!/opt/li-asterisk/tools/Python-3.6.7

import requests
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
from enum import Enum

class Method(Enum):

	GET = 1
	POST = 2
	DELETE = 3

class Http():
	"""Requests http in python"""
	def __init__(self, host, port, user, password, timeout):

		self.timeout = timeout
		self.server_parameters = {
			"host": host,
			"port": port,
			"user": user,
			"password": password

		}

	def http_request(self, http_method:Method, uri, is_stream, headers, data = None):
		code = None
		response = None
		json = None

		try:
			if(http_method == Method.GET):
				if(self.server_parameters["user"] and self.server_parameters["password"]):
					response = requests.get(uri, auth=(self.server_parameters["user"], 
						self.server_parameters["password"]), timeout=self.timeout, headers=headers, stream=is_stream)
				else:
					response = requests.get(uri, timeout=self.timeout, headers=headers, stream=is_stream)

			elif(http_method == Method.POST):
				if(self.server_parameters["user"] and self.server_parameters["password"]):
					response = requests.post(uri, auth=(self.server_parameters["user"], 
						self.server_parameters["password"]), headers=headers, timeout=self.timeout, data=data, stream=is_stream, verify=False)

				else:
					response = requests.post(uri, headers=headers, timeout=self.timeout, data=data, stream=is_stream, verify=False)

			elif(http_method == Method.DELETE):
				response = requests.delete(uri, auth=(self.server_parameters["user"], 
					self.server_parameters["password"]), timeout=self.timeout)
			else:
				raise Exception("Http method invalid")

	
		except Timeout:
			json = None
			raise Exception("Timeout from request")
		except HTTPError as http_err:
			json = None
			raise Exception("Error from request: " + str(http_err))

		finally:
			if(response):
				if(response.headers['Content-Type'] == "application/json" and
					len(response.headers['Content-Length']) !=0 and not is_stream):
					json = response.json()
				code = response.status_code

			return (code, json, response)

		

