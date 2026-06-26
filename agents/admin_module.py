# agents/admin_agent.py

from agents.resource_db import RESOURCES

DRONE_IMAGES = []

def add_drone_image(path):

    DRONE_IMAGES.append(path)

def get_drone_images():

    return DRONE_IMAGES

def update_resources(data):

    RESOURCES["ambulances"] = data["ambulances"]

    RESOURCES["boats"] = data["boats"]

    RESOURCES["rescue_workers"] = data["rescue_workers"]

    RESOURCES["food_packets"] = data["food_packets"]

    RESOURCES["water_packets"] = data["water_packets"]

def get_resources():

    return RESOURCES

# agents/admin_agent.py
import os

DRONE_FOLDER = "uploads/drone"

def get_drone_images():

    files = []

    for f in os.listdir(DRONE_FOLDER):

        if f.endswith((".jpg",".jpeg",".png")):

            files.append(
                os.path.join(
                    DRONE_FOLDER,
                    f
                )
            )

    return files