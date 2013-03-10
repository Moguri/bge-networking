from .network_handlers.enet_network_handler import ENetNetworkHandler


def replicatable_class(cls):
	def nm_setattr(self, name, value):
		if name in self.replication_vars and hasattr(self, NetworkManager._var("dirty_set")):
			getattr(self, NetworkManager._var("dirty_set")).add(name)
		getattr(self, NetworkManager._var("__setattr__"))(name, value)

	# Make sure this is set to cls.__init__ has something to play with
	setattr(cls, NetworkManager._var("dirty_set"), set())

	# Store the existing __setattr__
	setattr(cls, NetworkManager._var("__setattr__"), cls.__setattr__)

	# Now override the classes __setattr__ with our own
	cls.__setattr__ = nm_setattr

	return cls


class NetworkManager:

	ROLES = {"CLIENT", "SERVER"}
	HANDLER_CLASS = ENetNetworkHandler

	_VAR_PREFIX = "_NM__"

	def __init__(self, role, host, port):
		if role not in self.ROLES:
			raise TypeError("Supplied role (%s) is not valid. Expected a role in %s." % (role, self.ROLES))

		self.role = role

		if role == "SERVER":
			self.handler = self.HANDLER_CLASS.create_server(host, port)
		elif role == "CLIENT":
			self.handler = self.HANDLER_CLASS.create_client(host, port)

		self._actors = set()

	@classmethod
	def _var(cls, var):
		return cls._VAR_PREFIX+var

	@classmethod
	def create_server(cls, port):
		return cls("SERVER", None, 9999)

	@classmethod
	def create_client(cls, host, port):
		return cls("CLIENT", host, port)

	@property
	def connected(self):
		return self.handler.connected

	def register_actor(self, actor):
		if actor not in self._actors:
			self._actors.add(actor)
		else:
			print("Warning, actor already added")

	def unregister_actor(self, actor):
		if actor in self._actors:
			self._actors.remove(actor)
		else:
			print("Warning, actor not registered")

	def run(self):
		# Process any events on the handler
		self.handler.process_events()

		# Find any dirty attributes that we need to replicate
		if self.connected:
			for actor in self._actors:
				for var in getattr(actor, self._var("dirty_set")):
					print(actor.__class__.__name__, "dirty var", var, "value:", getattr(actor, var))

				setattr(actor, self._var("dirty_set"), set())
