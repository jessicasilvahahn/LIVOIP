#!/usr/bin/python3
import os

class Recourses():
	"""URI to ARI"""
	def __init__(self, host, port, protocol):
		self.uri = {}
		self.host = host
		self.port = port
		self.path = protocol + "://" + host + ":" + port

	def update_uri(self,name,uri):
		self.uri.update({name:uri})

	def build_uri(self):
		get_channel = "ari/channels"
		get_channel = os.path.join(self.path, get_channel)
		self.update_uri("get_channel", get_channel)


