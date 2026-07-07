import osmnx as ox
from geopy.distance import geodesic


def find_nearest_rescue_station(lat, lon):

    tags = {

        "amenity": [

            "fire_station",

            "hospital",

            "police"

        ]

    }

    places = ox.features_from_point(

        (lat, lon),

        tags=tags,

        dist=30000

    )

    best = None

    best_distance = float("inf")

    for _, row in places.iterrows():

        try:

            geometry = row.geometry

            if geometry.geom_type == "Point":

                p_lat = geometry.y
                p_lon = geometry.x

            else:

                c = geometry.centroid

                p_lat = c.y
                p_lon = c.x

            distance = geodesic(

                (lat, lon),

                (p_lat, p_lon)

            ).km

            if distance < best_distance:

                best_distance = distance

                best = {

                    "name": row.get("name", "Rescue Station"),

                    "lat": float(p_lat),

                    "lon": float(p_lon),

                    "distance": round(distance,2),

                    "type": row.get("amenity","Unknown")

                }

        except:

            pass

    return best