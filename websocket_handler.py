import asyncio
import websockets

class WebSocketClient:

    def __init__(self, uri):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        #self.websocket = await websockets.connect(self.uri)
        #print("WebSocket connection established.")
        try:
            self.websocket = await websockets.connect(self.uri)
            print("WebSocket connection established.")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket connection closed unexpectedly during connection: {e}")
            await self.connect()  # Retry connecting

    async def send_message(self, message):
        try:
            if self.websocket:
                await self.websocket.send(message)
                print(f"Message sent: {message}")
            else:
                print("WebSocket connection not established.")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket connection closed unexpectedly: {e}")
            await self.connect()  # Reconnect on unexpected closure
            await self.send_message(message)  # Retry sending message

    async def close_websocket(self):
        if self.websocket:
            await self.websocket.close()
            print("WebSocket connection closed.")
        else:
            print("WebSocket connection not established.")

''' Example usage
uri = "ws://your.websocket.server"
client = WebSocketClient(uri)
asyncio.get_event_loop().run_until_complete(client.connect())

# Send messages whenever needed
message1 = "Hello, WebSocket!"
asyncio.get_event_loop().run_until_complete(client.send_message(message1))

# Close the connection at the end of the program
asyncio.get_event_loop().run_until_complete(client.close())
'''
