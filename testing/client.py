import asyncio
import websockets

async def client(message):
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send(message)

if __name__ == "__main__":
    asyncio.run(client("sup dawg"))
