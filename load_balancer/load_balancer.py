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
        self.check_interval = 5  # seconds
        self.lock = asyncio.Lock()

    # Methods to update connection counts
    def increment_connection(self, server):
        self.connections[server] += 1

    async def decrement_connection(self, server):
        async with self.lock:
                self.connections[server] -= 1

    # Static approaches
    def round_robin(self, servers):
        server = servers[self.index]
        self.index = (self.index + 1) % len(self.servers)

        return server

    def random_choice(self, servers):
        return random.choice(servers)
    
    # Dynamic approach
    def least_connections(self, servers):
        connections = {server: self.connections.get(server) for server in servers}
        
        return min(connections, key=connections.get)
    
    # The method to get the server based on the chosen algorithm
    async def get_server(self):
        # You can switch between different algorithms here
        async with self.lock: 
            healthy_servers = [s for s in self.servers if self.healthy.get(s, False)]

            if not healthy_servers:
                logging.error("No healthy servers available!")
        
            server = self.round_robin(healthy_servers)

            self.increment_connection(server)

            return server
    
    # Periodic health check
    async def health_check(self):
        while True:
            for host, port in self.servers:
                try:
                    reader, writer = await asyncio.open_connection(host, port)
                    self.healthy[(host, port)] = True
                    writer.close()
                    logging.info(f"{host}:{port} is HEALTHY 😀")

                    await writer.wait_closed()
                except Exception:
                    self.healthy[(host, port)] = False
                    logging.warning(f"{host}:{port} is UNHEALTHY 😵")
                    
            await asyncio.sleep(self.check_interval)
