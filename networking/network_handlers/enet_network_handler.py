import enet


class ENetNetworkHandler:

	def __init__(self, is_server, host, port):
		self.connected = False

		if is_server:
			self.host = enet.Host(enet.Address(host, port), 32, 2, 0, 0)
			self.peer = None
		else:
			self.host = enet.Host(None, 1, 2, 0, 0)
			self.peer = self.host.connect(enet.Address(host, port), 1)

	@classmethod
	def create_server(cls, host, port):
		return cls(True, host, port)

	@classmethod
	def create_client(cls, host, port):
		return cls(False, host, port)

	def process_events(self):
		event = self.host.service(0)

		while event.type != enet.EVENT_TYPE_NONE:
			if event.type == enet.EVENT_TYPE_CONNECT:
				self.connected = True
				print("Connected: %s" % event.peer.address)
			elif event.type == enet.EVENT_TYPE_DISCONNECT:
				self.connected = False
				print("Disconnected: %s" % event.peer.address)
			elif event.type == enet.EVENT_TYPE_RECEIVE:
				print("Message from %s: %s" % (event.peer.address, event.packet.data))

			event = self.host.service(0)
