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


async def handle_client(reader, writer):
    # here, we decide which server to forward the request to
    client_addr = writer.get_extra_info("peername")
    server_host, server_port = lb.get_server()

    logging.info(f"redirecting client {client_addr} to ({server_host}:{server_port})")

    # try to connect to the server
    try:
        server_reader, server_writer = await asyncio.open_connection(server_host, server_port)
    except Exception as e:
        logging.error(f"could not connect to ({server_host}:{server_port}): {e}")
        writer.close()
        await writer.wait_closed()
        return
    
    lb.increment_connection((server_host, server_port))

    # Actually forward data between client and server
    try:
        await asyncio.gather(
            forward(reader, server_writer),
            forward(server_reader, writer)
        )
    finally:
        # ALways decrement connection count when done
        lb.decrement_connection((server_host, server_port))

async def main():
    server = await asyncio.start_server(handle_client, LOAD_BALANCER_HOST, LOAD_BALANCER_PORT)
    logging.info(f"load balancer running on {LOAD_BALANCER_HOST}:{LOAD_BALANCER_PORT}")

    await asyncio.gather(
        server.serve_forever(),
        lb.health_check()
    )


if __name__ == "__main__":
    asyncio.run(main())