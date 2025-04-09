import asyncio
import websockets

async def client(message):
    async with websockets.connect("ws://localhost:8766") as websocket:
        await websocket.send(message)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client("sup dawg"))
