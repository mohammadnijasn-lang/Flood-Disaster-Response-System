from agents.kerala_districts import (
    KERALA_DISTRICTS
)

from agents.weather_agent import (
    get_weather_risk
)

from agents.sentinel_fetch import (
    predict_location
)

def get_district_status():

    results = []

    for district in KERALA_DISTRICTS:

        try:

            weather = get_weather_risk(district)

            rain = weather["rainfall_24h"]

            if rain >= 10:

                flood = predict_location(district)

                flood_area = flood["flood_area"]

            else:

                flood_area = 0

            # AI flood prediction gets highest priority
            if flood_area >= 10:

                alert = "🔴 RED"

            elif flood_area >= 5:

                alert = "🟠 ORANGE"

            # If flood prediction is low, use rainfall
            elif weather["rainfall_24h"] >= 5:

                alert = "🟡 YELLOW"

            else:

                alert = "🟢 GREEN"

            results.append({

                "district":
                district,

                "flood_area":
                round(
                    flood_area,
                    2
                ),

                "rainfall":
                weather["rainfall_24h"],

                "alert":
                alert
            })

        except Exception as e:

            print(
                district,
                e
            )

    return results