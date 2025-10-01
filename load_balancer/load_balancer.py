import random
import logging
import asyncio

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
        self.healthy = {server: True for server in servers}
        self.index = 0
        self.conn_lock = asyncio.Lock()

    # Methods to update connection counts
    def increment_connection(self, server):
       self.connections[server] += 1

    async def decrement_connection(self, server):
        async with self.conn_lock:
            self.connections[server] -= 1

    # Static approaches
    def round_robin(self, servers):
        self.index = (self.index + 1) % len(servers)
        server = servers[self.index]

        return server

    def random_choice(self, servers):
        return random.choice(servers)
    
    # Dynamic approach
    def least_connections(self, servers):
        return min(servers, key=lambda s: self.connections.get(s, 0))
    
    # The method to get the server based on the chosen algorithm
    async def get_server(self):
        async with self.conn_lock:
            server = self.least_connections(self.servers)
            self.increment_connection(server)

        return server