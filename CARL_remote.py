import asyncio
import cv2 as cv
import os
import websockets

from navid_agent import NaVid_Agent

# For sending commands
async def client(message):
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send(message)

# For handling image transfer completion flags
class ImageFlagHandler:
    def __init__(self):
        self.stop_event = asyncio.Event()
        self.message = None

    async def run_server(self):
        server_task = asyncio.create_task(self.websocket_server())
        await server_task

    def get_message(self):
        return self.message

    async def handler(self, websocket):
        self.message = await websocket.recv()  # Wait for one message
        self.stop_event.set()  # Signal to stop the server

    async def websocket_server(self):
        async with websockets.serve(self.handler, "localhost", 8766):
            await self.stop_event.wait()  # Wait until a message is received

class CARLRemote:
    def __init__(self):
        model_path = "model_zoo/navid-7b-full-224-video-fps-1-grid-2-r2r-rxr-training-split"
        result_path = "output"

        self.agent = NaVid_Agent(model_path, result_path, require_map=False)

        self.env_id = 0
        self.info = None  # Only needed if we are doing simulation
        self.obs = {}
        self.obs['instruction'] = {}
        self.obs["instruction"]["text"] = "Go across the room to the black table and stop by the chair."     # Default
        self.img_file_path = "output/out.jpg"

        print('CARL is initialized')

    def reset(self, new_command):
        # Reset the agent
        self.agent.reset()

        # Load the new command
        print(f"Loading new command into CARL:\n{new_command}")
        self.obs['instruction']['text'] = new_command

    def update(self):
        async def update_async():
            # wait to get flag from robot -- if message not 'done', then reset agent
            ws_handler = ImageFlagHandler()
            # Start server
            await ws_handler.run_server()

            message = ws_handler.get_message()
            if message != 'done':
                self.reset(message)
                return

            # Save new image to the observation vector
            if not os.path.exists(self.img_file_path):
                print(f"No image at {self.img_file_path}! Continuing")
                return
            self.obs["rgb"] = cv.imread(self.img_file_path, cv.IMREAD_COLOR)

            # Get agent action
            action = self.agent.act(self.obs, self.info, self.env_id)
            self.env_id += 1

            # Send output action to the other computer via websockets
            await client(str(action['action']))

        asyncio.run(update_async())


# For debugging
if __name__=='__main__':
    # model_path = "model_zoo/navid-7b-full-224-video-fps-1-grid-2-r2r-rxr-training-split"
    # result_path = "output"
    #
    # agent = NaVid_Agent(model_path, result_path, require_map=False)
    #
    # env_id = 0
    # obs = {}
    # img_file_path = "output/out.jpg"
    #
    # # Load instructions
    # obs["instruction"]["text"] = "Go across the room to the black table and stop by the chair."
    #
    # while True:
    #     # Get observation - wait until file is available
    #     ws_handler = ImageFlagHandler()
    #     obs["rgb"] = cv.imread(img_file_path, cv.IMREAD_COLOR)
    #
    #     # Get info
    #     # Since we aren't using the sim, we can ignore this!
    #     info = None
    #
    #     # Get agent action
    #     action = agent.act(obs, info, env_id)
    #
    #     # Send output action to the other computer via websockets
    #     asyncio.run(client(action['action']))
    #
    #     env_id += 1

    # Instantiate CARL
    CARL = CARLRemote()

    # Run forever
    while True:
        CARL.update()


