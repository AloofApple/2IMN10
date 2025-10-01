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
        self.index = 0
        self.lock = asyncio.Lock()

    # Methods to update connection counts
    def increment_connection(self, server):
        self.connections[server] += 1

    async def decrement_connection(self, server):
        async with self.lock:
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
        # filter the active server counts based on the servers given.
        connections = {server: self.connections.get(server) for server in servers}
        least_connected = None
        min_connections = float('inf')

        # find the server with the least active connections.
        for server, count in connections.items():
            if count < min_connections:
                min_connections = count
                least_connected = server

        return least_connected

    # The method to get the server based on the chosen algorithm
    async def get_server(self):
        # You can switch between different algorithms here
        async with self.lock: 
            server = self.round_robin(self.servers)

            self.increment_connection(server)

            return server