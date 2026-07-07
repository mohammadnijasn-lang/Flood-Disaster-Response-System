def calculate_priority(
    flood_percent,
    rainfall,
    people,
    trapped_houses,
    vehicles,
    sos_count,
    houses=0,
    blocked_roads=0,
    collapsed_buildings=0
):

    score = (

        flood_percent * 0.35 +

        rainfall * 0.25 +

        people * 2 +

        trapped_houses * 8 +

        vehicles * 2 +

        sos_count * 20 +

        houses * 5 +

        blocked_roads * 10 +

        collapsed_buildings * 15

    )

    if score>=120:

        level="CRITICAL"

    elif score>=80:

        level="HIGH"

    elif score>=50:

        level="MEDIUM"

    else:

        level="LOW"

    return score,level