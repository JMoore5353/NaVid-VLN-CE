import argparse
import cv2 as cv

from navid_agent import NaVid_Agent


# Maybe we make a class here for running / interfacing with CARL?



# For debugging
if __name__=='__main__':
    model_path = "model_zoo/navid-7b-full-224-video-fps-1-grid-2-r2r-rxr-training-split"
    result_path = "output"

    agent = NaVid_Agent(model_path, result_path, require_map=False)

    # Get live images
    cap = cv.VideoCapture(0)

    env_id = 0
    obs = {}
    while True:
        # Get observations
        ret, frame = cap.read()
        if not ret:
            break

        obs["rgb"] = frame
        obs["instruction"]["text"] = "Go across the room to the black table and stop by the chair."

        # Get info
        # Since we aren't using the sim, we can ignore this!
        info = None

        # Get agent action
        action = agent.act(obs, info, env_id)

        env_id += 1
