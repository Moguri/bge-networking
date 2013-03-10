from .network_handlers.enet_network_handler import ENetNetworkHandler


class NetworkManager:
	
	ROLES = {"CLIENT", "SERVER"}
	HANDLER_CLASS = ENetNetworkHandler
	
	def __init__(self, role, host, port):
		if role not in self.ROLES:
			raise TypeError("Supplied role (%s) is not valid. Expected a role in %s." % (role, self.ROLES))
		
		self.role = role
		
		if role == "SERVER":
			self.handler = self.HANDLER_CLASS.create_server(host, port)
		elif role == "CLIENT":
			self.handler = self.HANDLER_CLASS.create_client(host, port)
	
	@classmethod
	def create_server(cls, port):
		return cls("SERVER", None, 9999)
	
	@classmethod
	def create_client(cls, host, port):
		return cls("CLIENT", host, port)
	
	@property
	def connected(self):
		return self.handler.connected
	
	def run(self):
		self.handler.process_events()