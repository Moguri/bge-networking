from networking import NetworkManager
import sys
import time

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == "server":
		print("Creating server...")
		nm = NetworkManager.create_server(9999)
	else:
		print("Creating client...")
		nm = NetworkManager.create_client(b"localhost", 9999)

	# Run for 10 seconds
	start = time.time()

	while time.time() - start < 10:
		nm.run()
