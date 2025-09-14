import asyncio
import random

LOAD_BALANCER_HOST = "0.0.0.0"
LOAD_BALANCER_PORT = 1200


SERVERS = [
    ("server1", 5000),
    ("server2", 5000),
    ("server3", 5000)
]

server_to_redirect = 0

# Routing algorithms
def RoundRobin(current_server: int, total_servers: int) -> int:
    return (current_server + 1) % (total_servers)

def RandomSelection(total_servers: int) -> int:
    return random.randint(0, total_servers - 1)

# function that forwards data between client and working server
async def forward(reader, writer):
        try:
            while data := await reader.read(4096): # we read data and forward it
                writer.write(data)
                await writer.drain()
        except ConnectionError:
            print("There was a connection error") # Here, we can maybe assume that the server is down in the future (for example)
        finally:
            writer.close()

async def handle_client(reader, writer):
    # here, we decide which server to forward the request to
    global server_to_redirect 
    server_to_redirect = RoundRobin(server_to_redirect, len(SERVERS))
    server_host, server_port = SERVERS[server_to_redirect]

    print(f"Redirecting client to server {server_to_redirect + 1} ({server_host}:{server_port})")

    # forward the request to server
    try:
        server_reader, server_writer = await asyncio.open_connection(server_host, server_port)
    except ConnectionError:
        print(f"Could not connect to server {server_to_redirect + 1} ({server_host}:{server_port})")
        writer.close()
        await writer.wait_closed()
        return
    
    # actually add as a task the forwarding
    await asyncio.gather(
        forward(reader, server_writer),
        forward(server_reader, writer)
    )

async def main():
    server = await asyncio.start_server(handle_client, LOAD_BALANCER_HOST, LOAD_BALANCER_PORT)
    print(f"Load balancer running on {LOAD_BALANCER_HOST}:{LOAD_BALANCER_PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())