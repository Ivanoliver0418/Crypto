import asyncio
from textwrap import dedent  # Helps create clean multi-line strings

class ConnectionPool:
    def __init__(self):
        # A set that stores all connected users (writer)
        # Using sets to avoid duplicates
        self.connection_pool = set()

    def send_welcome_message(self, writer):
        """
        Sends a welcome message to a newly connected client
        """
        # Build a formatted welcome message using the user's nickname
        message = dedent(f"""
        ===
        Welcome {writer.nickname}!
        There are {len(self.connection_pool) - 1} users beside you
        Help:
        - Type anything to chat
        - /list will list all the connected users
        - /quit will disconnect you
        ===
        """)
        # Send the message to this single user
        writer.write(f"{message}\n".encode())

    def broadcast(self, writer, message):
        """
        Broadcasts a general message to the entire pool
        """
        # Send message to all other connected users except the sender
        for user in self.connection_pool:
            if user != writer:
                # We don't need to also broadcast to the user sending the message
                user.write(f"{message}\n".encode())

    def broadcast_user_join(self, writer):
        """ 
        Calls the broadcast method with "user joining" message
        """
        self.broadcast(writer, f"{writer.nickname} just joined")

    def broadcast_user_quit(self, writer):
        """
        Calls the broadcast method with "user quitting" message
        """
        self.broadcast(writer, f"{writer.nickname} just quit")

    def broadcast_new_message(self, writer, message):
        """
        Calls the broadcast method with a user's chat message
        """
        self.broadcast(writer, f"[{writer.nickname}] {message}")

    def list_users(self, writer):
        """
        Lists all the users in the pool
        """
        # Build a list of all connected nicknames
        message = "===\nCurrently connected users: "
        for user in self.connection_pool:
            message += f"\n - {user.nickname}"
        message += "\n===\n"
        # Send the list back to the requesting user
        writer.write(f"{message}\n".encode())

    def add_new_user_to_pool(self, writer):
        """
        Adds a new user to our existing poool
        """
        self.connection_pool.add(writer)

    def remove_user_from_pool(self, writer):
        """
        Removes an existing user from our pool
        """
        self.connection_pool.remove(writer)

# A single shared connection pool for all users
connection_pool = ConnectionPool()

async def handle_connection(reader, writer):
    # Step 1: Ask the client for their nickname
    writer.write("> Choose your nickname: ".encode())  
    response = await reader.readuntil(b"\n")  # Wait for input
    writer.nickname = response.decode().strip()  # Save nickname on writer
                                                 # object
    
    # Step 2: Add the user to the pool and send welcome message
    connection_pool.add_new_user_to_pool(writer)
    connection_pool.send_welcome_message(writer)

    # Step 3: Notify all other users that someone joined
    connection_pool.broadcast_user_join(writer)

    # Step 4: Main chat loop - keep processing messages until user quits
    while True:
        try:
            # Wait for the next line the user types (enter)
            data = await reader.readuntil(b"\n")
        except asyncio.IncompleteReadError:
            # Happens when a client force-closes terminal
            connection_pool.broadcast_user_quit(writer)
            connection_pool.remove_user_from_pool(writer)
            break

        # Decode message into a clean string
        message = data.decode().strip()

        # Handle commands
        if message == "/quit":
            writer.write(b"Goodbye!\n")
            await writer.drain()

            connection_pool.broadcast_user_quit(writer)
            connection_pool.remove_user_from_pool(writer)

            break

        elif message == "/list":
            connection_pool.list_users(writer)
        
        else:       
            # Regular message -> broadcast to everyone
            connection_pool.broadcast_new_message(writer, message)

        await writer.drain()
        
    # Close the connection and clean up
    writer.close()
    await writer.wait_closed()

async def main():
    # Create a TCP server on 0.0.0.0 port 8888
    server = await asyncio.start_server(handle_connection, "0.0.0.0", 8888)
    # Keep server running forever
    async with server:
        await server.serve_forever()

# Start the entire program
asyncio.run(main())
