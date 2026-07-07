from agents.weather_agent import get_weather_risk
from agents.sentinel_fetch import predict_location

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

    results = []

    for district in districts:

        weather = get_weather_risk(district)

        rain = weather["rainfall_24h"]

        try:

            flood = predict_location(district)

            flood_area = flood["flood_area"]

            # Start with the weather alert
            alert = weather["alert"]

            # Upgrade alert if flood prediction is severe
            if flood_area >= 20:

                alert = "🔴 RED"

            elif flood_area >= 10:

                alert = "🟠 ORANGE"

            results.append({

                "district": district,

                "rainfall": rain,

                "flood_area": flood_area,

                "alert": alert

            })

        except Exception as e:

            print(district, e)

    return results