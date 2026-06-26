from agents.admin_module import (
    get_drone_images
)

from agents.vision_agents import (
    analyze_ground_image
)

from agents.Yolo_module import (
    count_people
)

def analyze_latest_drone():

    images = get_drone_images()

    if not images:

        return None

    latest = images[-1]

    vision = analyze_ground_image(
        latest
    )

    yolo = count_people(
        latest
    )

    return {

        "flood_detected":
        vision["flood_detected"],

        "severity":
        vision["severity"],

        "road_blocked":
        vision["road_blocked"],

        "people_at_risk":
        vision["people_at_risk"],

        "recommendation":
        vision["recommendation"],

        "people_count":
        yolo["people_count"],

        "vehicle_count":
        yolo["vehicle_count"]
    }