from agents.location_agent import create_bbox


def get_bbox_from_location(
    lat,
    lon
):

    west, south, east, north = create_bbox(
        lat,
        lon,
        size=0.25
    )

    return [

        west,
        south,

        east,
        north
    ]