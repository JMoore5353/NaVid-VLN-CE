import argparse
import asyncio
import cv2 as cv
import glob
import os
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
        # asyncio.run(self.run_server())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_server())


    async def run_server(self):
        server_task = asyncio.get_event_loop().create_task(self.websocket_server())
        await server_task

    def get_message(self):
        return self.message

    async def handler(self, websocket, path):
        self.message = await websocket.recv()  # Wait for one message
        print(f"Received: {self.message}")
        self.stop_event.set()  # Signal to stop the server

    async def websocket_server(self):
        async with websockets.serve(self.handler, "localhost", 8767):
            await self.stop_event.wait()  # Wait until a message is received

def run_inference(frame):
    # Save file
    start = time.time()
    img_path = os.path.join(os.getcwd(), 'out.jpg')
    print("saving image to", img_path)
    cv.imwrite(img_path, frame)
    time_to_write_img = time.time() - start

    # Send file and then file transfer completion flag
    start = time.time()
    subprocess.call(["bash", "/home/car/Desktop/NaVid-VLN-CE/testing/scp_file.sh", img_path])
    # asyncio.run(client("done"))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client("done"))
    print(f"Time to copy file to comp: {round(time.time() - start,4)}, time to write img: {round(time_to_write_img, 4)}")

    # Get output - blocking code
    start = time.time()
    ws_handler = ReturnCommandHandler()
    cmd = ws_handler.get_message()
    print(f"Time to get command (including inference time): {time.time() - start}")

    # Print the command
    # id: 0-stop, 1 move forward, 2 turn left, 3 turn right
    print(f"Command: {cmd}\n")

    # Show image for reference
    # out_img = frame.copy()
    # cv.putText(out_img, f"command: {cmd}", (10, out_img.shape[0]-10), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0))
    # cv.imshow("Image", out_img)
    # cv.waitKey(10)
    return cmd

def load_prompt(prompt):
    # asyncio.run(client(prompt))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client(prompt))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='CARL test script')
    parser.add_argument("-c", '--use-camera', action='store_true', help='Use camera or default images')
    parser.add_argument("-d", '--img-directory', type=str, default='run1', help='Directory of test images')
    args = parser.parse_args()

    if args.use_camera:
        cap = cv.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error in camera!")
                break

            run_inference(frame)
    else:
        # Use directory
        if not os.path.exists(args.img_directory):
            raise ValueError(f"Error! Directory {args.img_directory} not found!")

        img_paths = glob.glob(os.path.join(args.img_directory, "*.jpeg"))
        img_paths = sorted(img_paths)

        # Load prompt
        load_prompt("Move forward a few feet then turn left and go through the doorway. Go past the couch and stop near the TV.")

        for imgp in img_paths:
            img = cv.imread(imgp, cv.IMREAD_COLOR)
            # Resize so it is smaller
            img = cv.resize(img, (378,504))

            # Run inference
            run_inference(img)

    cv.destroyAllWindows()
