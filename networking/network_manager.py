from .network_handlers.enet_network_handler import ENetNetworkHandler
from .network_serializers.pickle_serializer import PickleNetworkSerializer


def replicatable_class(cls):
	if not hasattr(cls, "replication_vars"):
		raise AttributeError("Replicatable class %s is missing a replication_vars attribute." % (cls))

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

	# Store the class on the NetworkManager
	NetworkManager.classes[cls.__name__] = cls

	return cls


class NetworkManager:

	ROLES = {"CLIENT", "SERVER"}
	HANDLER_CLASS = ENetNetworkHandler
	SERIALIZER_CLASS = PickleNetworkSerializer

	classes = {}

	_VAR_PREFIX = "_NM__"

	def __init__(self, role, host, port):
		if role not in self.ROLES:
			raise ValueError("Supplied role (%s) is not valid. Expected a role in %s." % (role, self.ROLES))

		self.role = role

		if role == "SERVER":
			self.handler = self.HANDLER_CLASS.create_server(self.SERIALIZER_CLASS, host, port)
		elif role == "CLIENT":
			self.handler = self.HANDLER_CLASS.create_client(self.SERIALIZER_CLASS, host, port)

		self._actors = {}

		# Internal counter for ids
		self.next_id = 0

	@classmethod
	def _var(cls, var):
		return cls._VAR_PREFIX + var

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
		if not hasattr(actor, self._var("id")):
			aid = '#' + str(self.next_id)
			self.next_id += 1

			setattr(actor, self._var("id"), aid)
			setattr(actor, self._var("own"), True)
			self._actors[aid] = actor
			self.handler.send(("REG", actor.__class__.__name__, aid))
		else:
			print("Warning, actor already added")

	def unregister_actor(self, actor):
		if actor in self._actors:
			self._actors.remove(actor)
		else:
			print("Warning, actor not registered")

	def run(self):
		# Process any events on the handler
		events = self.handler.process_events()
		for event in events:
			data = event[1]

			if self.role == "SERVER":
				if data[0] == "REG":
					aid = data[2][1:]
					while aid in self._actors:
						aid = str(int(aid) + 1)

					actor = self.classes[data[1]].network_new()
					setattr(actor, self._var("id"), aid)
					setattr(actor, self._var("own"), True)
					self._actors[aid] = actor

					self.handler.send(("REG", data[1], data[2], aid))
			else:
				if data[0] == "REG":
					if data[2] in self._actors:
						actor = self._actors[data[2]]
						del self._actors[data[2]]
					else:
						actor = self.classes[data[1]].network_new()
						setattr(actor, self._var("own"), False)

					setattr(actor, self._var("id"), data[3])
					self._actors[data[3]] = actor


		# Find any dirty attributes that we need to replicate
		if self.connected:
			for aid, actor in self._actors.items():
				if aid.startswith('#') or not getattr(actor, self._var("own")):
					# If the actor's id start's with '#', then it hasn't yet be registered, with the server,
					# so skip it. Otherwise, if we don't own it, we shouldn't be sending updates.
					continue

				for var in getattr(actor, self._var("dirty_set")):
					print(actor.__class__.__name__, "dirty var", var, "value:", getattr(actor, var))
					self.handler.send(("REP", aid, var, getattr(actor, var)))

				setattr(actor, self._var("dirty_set"), set())
