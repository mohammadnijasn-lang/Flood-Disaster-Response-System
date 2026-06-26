import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv(
    "OPENWEATHER_API_KEY2"
)

KERALA_DISTRICTS = {

    "Thiruvananthapuram": (8.5241, 76.9366),
    "Kollam": (8.8932, 76.6141),
    "Pathanamthitta": (9.2648, 76.7870),
    "Alappuzha": (9.4981, 76.3388),
    "Kottayam": (9.5916, 76.5222),
    "Idukki": (9.8490, 76.9720),
    "Ernakulam": (9.9816, 76.2999),
    "Thrissur": (10.5276, 76.2144),
    "Palakkad": (10.7867, 76.6548),
    "Malappuram": (11.0732, 76.0740),
    "Kozhikode": (11.2588, 75.7804),
    "Wayanad": (11.6854, 76.1320),
    "Kannur": (11.8745, 75.3704),
    "Kasaragod": (12.4996, 74.9869)

}


def get_weather_risk(district):

    if district not in KERALA_DISTRICTS:

        return {

            "rainfall_24h": 0,
            "alert": "UNKNOWN",
            "weather": "Unknown"

        }

    lat, lon = KERALA_DISTRICTS[district]

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}"
        f"&lon={lon}"
        f"&appid={API_KEY}"
        f"&units=metric"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except Exception as e:

        print("Weather API Error:", e)

        return {

            "rainfall_24h": 0,
            "alert": "UNKNOWN",
            "weather": "Unknown"

        }

    weather = data["list"][0]["weather"][0]["main"]

    rainfall = 0

    for item in data["list"][:8]:

        if "rain" in item:

            rainfall += item["rain"].get(
                "3h",
                0
            )

    if rainfall >= 15:

        alert = "🔴 RED"

    elif rainfall >= 10:

        alert = "🟠 ORANGE"

    elif rainfall >= 5:

        alert = "🟡 YELLOW"

    else:

        alert = "🟢 GREEN"

    print("\n========== WEATHER REPORT ==========")

    print("District :", district)

    print("Weather  :", weather)

    print("Rainfall :", rainfall)

    print("Alert    :", alert)

    print("====================================")

    return {

        "rainfall_24h": round(
            rainfall,
            2
        ),

        "alert": alert,

        "weather": weather

    }