import asyncio
import cv2 as cv
import subprocess
import time
import websockets

# To be run on computer with the image
# Steps for running remotely on Zeus:
# Terminal 1. ssh into zeus. Run docker container in this shell
# Terminal 2. ssh into zeus. Then ssh -L 8765:localhost:8765 jacob@10.37.121.216
#   This forwards traffic on jacob:localhost:8765 to localhost:8765
#   Make sure AllowTcpForwarding yes on jacob in /etc/ssh/ssh_config
# Terminal 3. ssh -L 8766:localhost:8766 zeus_home
#   This forwards traffic on zeus:localhost:8766 to localhost:8766
# Terminal 4. Run remote_cam_test.py

# For sending image transfer completion flags
async def client(message):
    async with websockets.connect("ws://localhost:8766") as websocket:
        await websocket.send(message)


# For handling return commands
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


cap = cv.VideoCapture(0)

while True:
    start = time.time()
    ret, frame = cap.read()
    if not ret:
        print("Error in camera!")
        break

    # Save file
    cv.imwrite("./out.jpg", frame)
    time_to_write_img = time.time() - start

    # Send file and then file transfer completion flag
    start = time.time()
    subprocess.call(["bash", "./scp_file.sh"])
    asyncio.run(client("done"))
    print(f"Time to copy file to comp: {round(time.time() - start,4)}, time to write img: {round(time_to_write_img, 4)}")

    # Get output - blocking code
    start = time.time()
    ws_handler = ReturnCommandHandler()
    cmd = ws_handler.get_message()
    print(f"Time to get command (including inference time): {time.time() - start}")

    # Print the command
    print(f"Command: {cmd}\n")

cv.destroyAllWindows()
