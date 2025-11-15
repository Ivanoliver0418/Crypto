import asyncio 

# This function handles a single client connection
async def handle_connection(reader, writer):

    # writer.write() sends data to the client (must be bytes) 
    writer.write("Hello new user, type something...\n".encode())
    
    """reader.readuntil(): waits until a newline is recieved, then returns all
    the data"""  
    data = await reader.readuntil(b"\n")

    # Echo the received data back to the client
    writer.write("You sent: ".encode() + data)

    # writer.drain(): waits until all outgoing data is actually sent
    await writer.drain()
    
    # Close the connection on server side
    writer.close()

    # Wait until the connection is fully closed 
    # (forces a clean shutdown of the client socket)
    await writer.wait_closed()

# The main function that starts the server
async def main():
    """
    - asyncio.start_server(): creates a TCP server
    - handle_connection: function to run for each new client 
    - "0.0.0.0": bind to all network interfaces
    - 8888: port number
    """
    server = await asyncio.start_server(handle_connection, "0.0.0.0", 8888)

    async with server:
    # serve_forever(): keep the server running endlessly
    # listens for new clients and calls handle_connection for each one
        await server.serve_forever()

# Start the asyncio event loop and run the main coroutine
asyncio.run(main())
