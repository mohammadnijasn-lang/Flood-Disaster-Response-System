from agents.weather_agent import get_weather_risk
from agents.sentinel_agent import predict_location


def get_high_risk_districts():

    districts = [

        "Thiruvananthapuram",
        "Kollam",
        "Pathanamthitta",
        "Alappuzha",
        "Kottayam",
        "Idukki",
        "Ernakulam",
        "Thrissur",
        "Palakkad",
        "Malappuram",
        "Kozhikode",
        "Wayanad",
        "Kannur",
        "Kasaragod"

    ]

    risky = []

    for district in districts:

        weather = get_weather_risk(district)

        rain = weather["rainfall_24h"]

        # Skip low rainfall districts
        if rain < 10:
            continue

        try:

            flood = predict_location(district)

            risky.append({

            "district":district,

            "rainfall":rain,

            "flood_area":flood["flood_area"],

            "alert":weather["alert"]

        })

        except Exception as e:

            print(district, e)

    return risky