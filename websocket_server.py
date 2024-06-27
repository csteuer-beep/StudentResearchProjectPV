import asyncio
import websockets

# Lists to keep track of connected clients
alerts_clients = set()
test_clients = set()
command_clients = set()

async def alerts_handler(websocket, path):
    alerts_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received on /alerts: {message}")
            await broadcast(message, alerts_clients)
    finally:
        alerts_clients.remove(websocket)

async def test_handler(websocket, path):
    test_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received on /test: {message}")
            await broadcast(message, test_clients)
    finally:
        test_clients.remove(websocket)

async def command_handler(websocket, path):
    command_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received on /command: {message}")
            await broadcast(message, command_clients)
    finally:
        command_clients.remove(websocket)

async def broadcast(message, clients):
    for client in clients:
        if client.open:
            await client.send(message)

async def main_handler(websocket, path):
    if path == "/alerts":
        await alerts_handler(websocket, path)
    elif path == "/test":
        await test_handler(websocket, path)
    elif path == "/command":
        await command_handler(websocket, path)
    else:
        await websocket.send("Unknown path")

start_server = websockets.serve(main_handler, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
