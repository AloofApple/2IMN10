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
        self.check_interval = 3  # seconds
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
    
    # Set a server healthy or unhealthy with a lock
    async def set_health(self, server, status: bool):
        async with self.lock:
            self.healthy[server] = status

    # Check if the server is healthy or not
    async def is_healthy(self, server):
        async with self.lock:
            return self.healthy.get(server, False)
    
    # Periodic health check
    async def health_check(self):
        while True:
            for host, port in self.servers:
                try:
                    # Check the server health and set it to True
                    reader, writer = await asyncio.open_connection(host, port)
                    await self.set_health((host, port), True)
                    logging.info(f"{host}:{port} is HEALTHY 😀")
                    
                    # Wait until writer is fully closed.
                    writer.close()
                    await writer.wait_closed()

                except Exception:
                    # Set the server health to False
                    await self.set_health((host, port), False)
                    logging.warning(f"{host}:{port} is UNHEALTHY 😵")
                    
            await asyncio.sleep(self.check_interval)

    # The method to get the server based on the chosen algorithm
    async def get_server(self):
        # You can switch between different algorithms here
        async with self.lock: 
            healthy_servers = [s for s in self.servers if self.healthy.get(s, False)]

            if not healthy_servers:
                logging.error("No healthy servers available!")
                return None
        
            server = self.round_robin(healthy_servers)

            self.increment_connection(server)

            return server
        

async def get_server_with_algorithm(lb: LoadBalancer, algorithm):
    async with lb.lock:
        healthy_servers = [s for s in lb.servers if lb.healthy.get(s, False)]

        if not healthy_servers:
            logging.error("No healthy servers available!")
            return None

        server = algorithm(healthy_servers)
        lb.increment_connection(server)

        return server