# from PIL import Image
# import numpy as np


# def analyze_flood_mask(
#     mask_path
# ):

#     img = Image.open(
#         mask_path
#     )

#     img = img.convert(
#         "L"
#     )

#     arr = np.array(img)

#     flood_pixels = np.sum(
#         arr > 100
#     )

#     total_pixels = arr.size

#     flood_percent = round(

#         flood_pixels
#         /
#         total_pixels
#         *
#         100,

#         2
#     )

#     if flood_percent < 2:

#         severity = "LOW"

#     elif flood_percent < 5:

#         severity = "MODERATE"

#     elif flood_percent < 10:

#         severity = "HIGH"

#     else:

#         severity = "EXTREME"

#     return {

#         "flood_pixels":
#         int(flood_pixels),

#         "flood_percent":
#         flood_percent,

#         "severity":
#         severity
#     }


from openai import OpenAI
from dotenv import load_dotenv
import base64
import os
import json

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
    Analyze the image carefully.

    Return ONLY valid JSON.

    {
    "flood_detected": true,
    "severity": "Low | Medium | High | Critical",
    "road_blocked": true,
    "people_at_risk": true,
    "rescue_recommendation": "string"
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

    return {

        # "flood_detected": data["flood_detected"],

        # "severity": data["severity"],

        # "road_blocked": data["road_blocked"],

        # "people_at_risk": data["people_at_risk"],

        # "recommendation":
        # data["rescue_recommendation"]

    "flood_detected":
    data["flood_detected"],

    "severity":
    data["severity"],

    "road_blocked":
    data["road_blocked"],

    "people_at_risk":
    data["people_at_risk"],

    "recommendation":
    data["rescue_recommendation"]
}
