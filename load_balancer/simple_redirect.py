import asyncio
from http import server

LOAD_BALANCER_HOST = ""
LOAD_BALANCER_PORT = 1200



SERVERS = [5000, 5001, 5002]


async def handle_client(reader, writer):

    # here, we decide which server to forward the request to -> LB ALGORITHM!!

    server_to_redirect = 0

    print(f"Redirecting to server {server_to_redirect + 1}")

    # forward the request to server
    try:
        server_reader, server_writer = await asyncio.open_connection("127.0.0.1", SERVERS[server_to_redirect])
    except ConnectionError:
        writer.close()
        return
    
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
    
    
    # actually add as a task the forwarding
    await asyncio.gather(
        forward(reader, server_writer),
        forward(server_reader, writer)
    )






async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8888)
    print(f"Load balancer running on {LOAD_BALANCER_HOST}:{LOAD_BALANCER_PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())