import random

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
    
    def get_server(self):
        # You can switch between different algorithms here
        return self.round_robin()
        # return self.random_choice()
