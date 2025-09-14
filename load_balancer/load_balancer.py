import random
import rpyc
import logging

############################################################################################################
# Setup
#

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

############################################################################################################
# Load Balancer Logic
#

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.connections = {server: 0 for server in servers}
        self.index = 0

    def increment_connection(self, server):
        self.connections[server] += 1

    def decrement_connection(self, server):
        self.connections[server] -= 1

    # Static approaches
    def round_robin(self):
        server = self.servers[self.index]
        self.index = (self.index + 1) % len(self.servers)
        return server

    def random_choice(self):
        return random.choice(self.servers)
    
    # Dynamic approach
    def least_connections(self):
        return min(self.connections, key=self.connections.get)
    
    # The method to get the server based on the chosen algorithm
    def get_server(self):
        # You can switch between different algorithms here
        return self.least_connections()
