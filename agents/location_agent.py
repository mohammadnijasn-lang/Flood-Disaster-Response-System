from geopy.geocoders import Nominatim

def get_coordinates(location):

    geolocator = Nominatim(
        user_agent="flood_prediction"
    )

    loc = geolocator.geocode(
        location + ", Kerala, India"
    )

    if loc is None:

        raise Exception(
            f"Location not found: {location}"
        )

    return (
        loc.latitude,
        loc.longitude
    )


def create_bbox(
    lat,
    lon,
    size=0.1
):

    return [
        lon - size,
        lat - size,
        lon + size,
        lat + size
    ]