import asyncio
from textwrap import dedent

class ConnectionPool:
    def __init__(self):
        self.connection_pool = set()

    def send_welcome_message(self, writer):
        """
        Sends a welcome message to a newly connected client
        """
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
        writer.write(f"{message}\n".encode())

    def broadcast(self, writer, message):
        """
        Broadcasts a general message to the entire pool
        """
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
        message = "===\nCurrently connected users: "
        for user in self.connection_pool:
            message += f"\n - {user.nickname}"
        message += "\n===\n"
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

connection_pool = ConnectionPool()

async def handle_connection(reader, writer):
    writer.write("> Choose your nickname: ".encode())
    response = await reader.readuntil(b"\n")
    writer.nickname = response.decode().strip()
    connection_pool.add_new_user_to_pool(writer)
    connection_pool.send_welcome_message(writer)
    # Anounce the arrival of this new user
    connection_pool.broadcast_user_join(writer)
    while True:
        try:
            data = await reader.readuntil(b"\n")
        except asyncio.IncompleteReadError:
            connection_pool.broadcast_user_quit(writer)
            connection_pool.remove_user_from_pool(writer)
            break

        message = data.decode().strip()

        if message == "/quit":
            writer.write(b"Goodbye!\n")
            await writer.drain()

            connection_pool.broadcast_user_quit(writer)
            connection_pool.remove_user_from_pool(writer)

            break

        elif message == "/list":
            connection_pool.list_users(writer)
        
        else:
            connection_pool.broadcast_new_message(writer, message)

        await writer.drain()
        
    # Close the connection and clean up
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_connection, "0.0.0.0", 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())
