import argparse
import cv2 as cv
import time

from navid_agent import NaVid_Agent


# Maybe we make a class here for running / interfacing with CARL?



# For debugging
if __name__=='__main__':
    model_path = "model_zoo/navid-7b-full-224-video-fps-1-grid-2-r2r-rxr-training-split"
    result_path = "output"

    agent = NaVid_Agent(model_path, result_path, require_map=False)

    # Get live images
    print("Done initializing agent")
    cap = cv.VideoCapture(0)
    print("Initialized camera")

    env_id = 0
    obs = {}
    while True:
        start_time = time.time()
        # Get observations
        ret, frame = cap.read()
        cam_time = time.time() - start_time
        if not ret:
            print("Error reading from camera!")
            break

        start_time = time.time()
        obs["rgb"] = frame
        obs["instruction"] = {}
        obs["instruction"]["text"] = "Go across the room to the black table and stop by the chair."

        # Get info
        # Since we aren't using the sim, we can ignore this!
        info = None

        # Get agent action
        action = agent.act(obs, info, env_id)
        print("Getting action: ", action["action"], "  Inference time:", round(time.time() - start_time, 6), "Cam time:", round(cam_time, 6), "Env ID:", env_id)

        env_id += 1

        if env_id % 100 == 0:
            agent.reset()
