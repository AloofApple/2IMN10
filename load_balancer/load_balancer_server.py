import asyncio
import logging
from load_balancer import LoadBalancer

############################################################################################################
# Setup
#

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

LOAD_BALANCER_HOST = "0.0.0.0"
LOAD_BALANCER_PORT = 1200

SERVERS = [
    ("server1", 5000),
    ("server2", 5000),
    ("server3", 5000)
]

lb = LoadBalancer(SERVERS)

############################################################################################################
# Load Balancer Service
#

async def forward(reader, writer):
        try:
            while data := await reader.read(4096): # we read data and forward it
                writer.write(data)
                await writer.drain()
        except Exception as e:
            logging.error(f"forwarding error: {e}") # Here, we can maybe assume that the server is down in the future (for example)
        finally:
            writer.close()

async def connect_to_server(server):
    server_host, server_port = server

    try:
        reader, writer = await asyncio.open_connection(server_host, server_port)
        return reader, writer
    
    except Exception as e:
        logging.error(f"could not connect to ({server_host}:{server_port}): {e}")
        await lb.set_health((server_host, server_port), False)
        return None, None

async def handle_client(reader, writer):
    client_addr = writer.get_extra_info("peername")

    # First attempt to get server from load balancer.
    server = await lb.get_server()
    if not server:
        logging.error(f"No healthy servers available for client {client_addr}")
        writer.close()
        await writer.wait_closed()
        return

    # Try to connect to that server, and if it fails try another one 
    server_reader, server_writer = await connect_to_server(server)
    if server_reader is None:
        fallback_server = await lb.get_server()
        if not fallback_server:
            logging.error(f"No fallback servers available for client {client_addr}")
            writer.close()
            await writer.wait_closed()
            return

        logging.info(f"retrying client {client_addr} with fallback {fallback_server}")
        server_reader, server_writer = await connect_to_server(fallback_server)
        server = fallback_server

        if server_reader is None:
            logging.error(f"Fallback server also failed for client {client_addr}")
            writer.close()
            await writer.wait_closed()
            return

    # Forward traffic
    logging.info(f"redirecting client {client_addr} to {server}")
    try:
        await asyncio.gather(
            forward(reader, server_writer),
            forward(server_reader, writer)
        )
    finally:
        await lb.decrement_connection(server)


async def main():
    server = await asyncio.start_server(handle_client, LOAD_BALANCER_HOST, LOAD_BALANCER_PORT)
    logging.info(f"load balancer running on {LOAD_BALANCER_HOST}:{LOAD_BALANCER_PORT}")

    await asyncio.gather(
        server.serve_forever(),
        lb.health_check()
    )


if __name__ == "__main__":
    asyncio.run(main())