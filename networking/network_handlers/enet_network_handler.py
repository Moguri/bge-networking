import enet


class ENetClient:
	def __init__(self, peer, serializer):
		self.peer = peer
		self.serializer = serializer

	def send(self, msg):
		self.peer.send(0, enet.Packet(self.serializer.to_network(msg)))

class ENetNetworkHandler:

	def __init__(self, is_server, serializer, host, port):
		self.connected = False

		if is_server:
			self.host = enet.Host(enet.Address(host, port), 32, 2, 0, 0)
			self.peer = None
		else:
			self.host = enet.Host(None, 1, 2, 0, 0)
			self.peer = self.host.connect(enet.Address(host, port), 1)

		self.serializer = serializer()

	@classmethod
	def create_server(cls, serializer, host, port):
		return cls(True, serializer, host, port)

	@classmethod
	def create_client(cls, serializer, host, port):
		return cls(False, serializer, host, port)

	def process_events(self):
		retval = []
		event = self.host.service(0)

		while event.type != enet.EVENT_TYPE_NONE:
			if event.type == enet.EVENT_TYPE_CONNECT:
				self.connected = True
				print("Connected: %s" % event.peer.address)
			elif event.type == enet.EVENT_TYPE_DISCONNECT:
				self.connected = False
				print("Disconnected: %s" % event.peer.address)
			elif event.type == enet.EVENT_TYPE_RECEIVE:
				data = self.serializer.from_network(event.packet.data)
				print("Message from %s: %s" % (event.peer.address, data))
				retval.append((ENetClient(event.peer), data))

			event = self.host.service(0)

		return retval

	def send(self, msg):
		self.peer.send(0, enet.Packet(self.serializer.to_network(msg)))
