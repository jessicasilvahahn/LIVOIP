#!/usr/bin/python3

import requests
from requests.exceptions import HTTPError
from requests.exceptions import Timeout

class Http():
	"""Requests https in python"""
	def __init__(self, recourse, user, password, timeout):

		self.timeout = timeout

		self.server_parameters = {
			"host": recourse.host,
			"port": recourse.port,
			"user": user,
			"password": password

		}

	def get(self, uri):
		response = None
		json = None
		code = None
		try:
			response = requests.get(uri, auth=(self.server_parameters["user"], self.server_parameters["password"]), timeout=self.timeout)
			json = response.json()
			code = response.status_code
				
		except Timeout:
			json = None
			raise Exception("Timeout from request")
		except HTTPError as http_err:
			json = None
			raise Exception("Error from request: " + str(http_err))
		finally:
			return (code, json)
		
		

