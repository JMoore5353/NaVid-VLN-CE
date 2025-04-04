import asyncio
import websockets

# async def handler(websocket):
#     async for message in websocket:
#         print(f"Received: {message}")
#
# async def main():
#     async with websockets.serve(handler, "localhost", 8765):
#         print('test')
#         await asyncio.Future()  # Run forever
#
# if __name__ == "__main__":
#     asyncio.run(main())
#
#     while True:
#       print('testing async stuff')

# import asyncio
# import websockets
#
# async def handler(websocket):
#     message = await websocket.recv()  # Wait for a message
#     print(f"Received: {message}")
#     await websocket.send(f"Echo: {message}")  # Respond to the message
#
# async def main():
#     async with websockets.serve(handler, "localhost", 8765):
#         await asyncio.sleep(0)  # Allows other tasks to run
#
# # Running the event loop
# if __name__ == "__main__":
#     asyncio.run(main())

# import asyncio
# import websockets
#
# async def handler(websocket):
#     message = await websocket.recv()
#     print(f"Received: {message}")
#
# async def websocket_server():
#     async with websockets.serve(handler, "localhost", 8765):
#         await asyncio.Future()  # Keeps the server running
#
# async def background_task():
#     while True:
#         print("Processing other things...")
#         await asyncio.sleep(5)  # Simulate work
#
# async def main():
#     server_task = asyncio.create_task(websocket_server())
#     work_task = asyncio.create_task(background_task())
#
#     await asyncio.gather(server_task, work_task)
#
# if __name__ == "__main__":
#     asyncio.run(main())


#
# # Event to signal when a message is received
# stop_event = asyncio.Event()
#
# async def handler(websocket):
#     message = await websocket.recv()  # Wait for one message
#     print(f"Received: {message}")
#     stop_event.set()  # Signal to stop the server
#
# async def websocket_server():
#     async with websockets.serve(handler, "localhost", 8765):
#         await stop_event.wait()  # Wait until a message is received
#
# async def main():
#     server_task = asyncio.create_task(websocket_server())
#     await server_task  # Wait for the server to complete
#
# if __name__ == "__main__":
#     asyncio.run(main())

class ReturnCommandHandler:
    def __init__(self):
        self.stop_event = asyncio.Event()

        # Start server
        asyncio.run(self.run_server())

    async def run_server(self):
        server_task = asyncio.create_task(self.websocket_server())
        await server_task

    def get_message(self):
        return self.message

    async def handler(self, websocket):
        self.message = await websocket.recv()  # Wait for one message
        print(f"Received: {self.message}")
        self.stop_event.set()  # Signal to stop the server

    async def websocket_server(self):
        async with websockets.serve(self.handler, "localhost", 8765):
            await self.stop_event.wait()  # Wait until a message is received


if __name__=='__main__':
    handler = ReturnCommandHandler()
    print(handler.get_message())
    print('done')
