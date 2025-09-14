import random
import rpyc

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.index = 0

    def round_robin(self):
        server = self.servers[self.index]
        self.index = (self.index + 1) % len(self.servers)
        return server

    def random_choice(self):
        return random.choice(self.servers)
    
    def least_connections(self):
        min_load = None
        selected_server = 0

        for host, port in self.servers:
            try:
                conn = rpyc.connect(host, port)
                active_clients = conn.root.get_active_clients()
                conn.close()

                if min_load is None or active_clients < min_load:
                    min_load = active_clients
                    selected_server = (host, port)

            except Exception as e:
                continue  # If we can't connect, skip this server

        return selected_server
    
    def get_server(self):
        # You can switch between different algorithms here
        return self.least_connections()
