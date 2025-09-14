import asyncio
import random
from load_balancer import LoadBalancer

LOAD_BALANCER_HOST = "0.0.0.0"
LOAD_BALANCER_PORT = 1200

SERVERS = [
    ("server1", 5000),
    ("server2", 5000),
    ("server3", 5000)
]

# Initialize load balancer
lb = LoadBalancer(SERVERS)

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
    client_addr = writer.get_extra_info("peername")
    server_host, server_port = lb.get_server()

    print(f"Redirecting client {client_addr[1]} to ({server_host}:{server_port}) \n")

    # forward the request to server
    try:
        server_reader, server_writer = await asyncio.open_connection(server_host, server_port)
    except ConnectionError:
        print(f"Could not connect to ({server_host}:{server_port})")
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