from openai import OpenAI
from dotenv import load_dotenv
import base64
import os
import json
from agents.drone_db import latest_drone
from agents.Yolo_module import count_people

def analyze_ground_image(image_path):
    load_dotenv()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    with open(image_path, "rb") as img:
        image_b64 = base64.b64encode(img.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="qwen/qwen2.5-vl-72b-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
    You are an expert disaster image analyst.

    Your job is to determine ONLY what is visually observable.

    Rules:

    1. Never assume a flood exists.
    2. Flooding exists ONLY if standing or flowing floodwater is clearly visible.
    3. Wet roads, reflections, shadows, or dark pavement are NOT floods.
    4. If you are uncertain, answer "flood_detected": false.
    5. Never invent trapped people, damaged buildings, or blocked roads.
    6. Count only objects that are actually visible.
    7. Ignore weather conditions unless they are directly visible.
    8. Base every answer ONLY on the uploaded image.
    9. Do not use outside knowledge.
    10. Return ONLY valid JSON.

    Return exactly:

    {
    "flood_detected": true,
    "confidence": 0.95,
    "severity":"None|Low|Medium|High|Critical",
    "road_blocked":false,
    "people_at_risk":false,
    "estimated_people":0,
    "vehicles_visible":0,
    "houses_damaged":0,
    "collapsed_buildings":0,
    "water_level":"None|Ankle|Knee|Waist|Roof",
    "rescue_recommendation":"string"
    }
    """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300,
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    # Remove markdown if model adds it
    result = result.replace("```json", "")
    result = result.replace("```", "")
    result = result.strip()

    try:
        data = json.loads(result)

        print("\n===== VISION REPORT =====")
        print("Flood Detected :", data["flood_detected"])
        print("Severity       :", data["severity"])
        print("Road Blocked   :", data["road_blocked"])
        print("People At Risk :", data["people_at_risk"])
        print("Recommendation :", data["rescue_recommendation"])

    except Exception as e:
        print("JSON Parsing Error")
        print(result)
        print(e)

    # --------------------------
    # YOLO Detection
    # --------------------------

    yolo = count_people(image_path)

    return {

        "flood_detected": data["flood_detected"],

        "severity": data["severity"],

        "road_blocked": data["road_blocked"],

        "people_at_risk": data["people_at_risk"],

        "recommendation": data["rescue_recommendation"],

        "people_count": yolo["people_count"],

        "vehicle_count": yolo["vehicle_count"],

        "house_count": data["houses_damaged"]

    }


# def analyze_scene(detections):

#     people = 0
#     vehicles = 0

#     for d in detections:

#         if d["class"] == "person":
#             people += 1

#         elif d["class"] in ["car", "truck", "bus"]:
#             vehicles += 1

#     return {

#         "people": people,

#         "vehicles": vehicles,

#         "crowded": people > 20,

#         "priority_score": people * 3 + vehicles

#     }

def analyze_latest_drone():

    image = latest_drone()

    if image is None:

        return None

    return analyze_ground_image(image)
