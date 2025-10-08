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
        self.success_counts = {server: 0 for server in servers}
        self.check_interval = 3  # seconds
        self.conn_lock = asyncio.Lock()
        self.health_lock = asyncio.Lock()

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
    
    # Set a server healthy or unhealthy with a lock
    async def set_health(self, server, status: bool):
        async with self.health_lock:
            self.healthy[server] = status

    # Check if the server is healthy or not
    async def is_healthy(self, server):
        async with self.health_lock:
            return self.healthy.get(server, False)
    
    # Periodic health check
    async def health_check(self):
        while True:
            for host, port in self.servers:
                server = (host, port)
                try:
                    # Check the server health and set it to True
                    reader, writer = await asyncio.open_connection(host, port) 
                    await self.set_health(server, True)
                    logging.info(f"Server {server} marked as HEALTHY.")

                    # Wait until writer is fully closed.
                    writer.close()
                    await writer.wait_closed()

                except Exception:
                    # Set the server health to False
                    await self.set_health(server, False)
                    logging.info(f"Server {server} marked as UNHEALTHY.")

            await asyncio.sleep(self.check_interval)

    # The method to get the server based on the chosen algorithm
    async def get_server(self, algorithm: function = round_robin):
        async with self.health_lock:
            healthy_servers = [s for s in self.servers if self.healthy.get(s, False)]

        if not healthy_servers:
            logging.error("No healthy servers available!")
            return None

        async with self.conn_lock:
            server = algorithm(healthy_servers)
            self.increment_connection(server)

        return server