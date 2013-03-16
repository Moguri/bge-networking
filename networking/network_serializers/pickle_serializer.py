import pickle


class PickleNetworkSerializer():
	def to_network(self, msg):
		return pickle.dumps(msg)

	def from_network(self, msg):
		return pickle.loads(msg)
