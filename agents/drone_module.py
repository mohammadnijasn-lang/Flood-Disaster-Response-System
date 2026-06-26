from agents.vision_agents import (
    analyze_ground_image
)

from agents.Yolo_module import (
    count_people
)

def analyze_drone_image(
    image_path
):

    vision = analyze_ground_image(
        image_path
    )

    yolo = count_people(
        image_path
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