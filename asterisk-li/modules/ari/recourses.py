#!/usr/bin/python3
import os

class Recourses():
	"""URI to ARI"""
	def __init__(self, host, port, protocol):
		self.host = host
		self.port = port
		self.path = protocol + "://" + host + ":" + port
		self.uri = {}

	def update_uri(self, name, uri):
		self.uri.update({name:uri})
	
	def build_uri(self):
		channels = "ari/channels"
		channels = os.path.join(self.path, channels)
		self.update_uri("channels", channels)
		self.update_uri("create_channels", os.path.join(channels, "/create"))



