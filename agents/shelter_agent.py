import osmnx as ox
import pandas as pd
from geopy.distance import geodesic


def find_nearest_shelter(
    lat,
    lon
):

    # print(
    #     f"\nSearching shelters near "
    #     f"{lat}, {lon}"
    # )

    tags = {
        "amenity": True
    }

    shelters = ox.features_from_point(
        (lat, lon),
        tags=tags,
        dist=20000
    )

    # print(
    #     f"Found {len(shelters)} amenities"
    # )

    best = None
    best_dist = float("inf")

    shelter_types = [

        "community_centre",

        "school",

        "college",

        "social_facility"
    ]

    for _, row in shelters.iterrows():

        try:

            amenity = row.get(
                "amenity",
                ""
            )

            if amenity not in shelter_types:
                continue

            geometry = row.geometry

            if geometry.geom_type == "Point":

                s_lat = geometry.y
                s_lon = geometry.x

            else:

                centroid = geometry.centroid

                s_lat = centroid.y
                s_lon = centroid.x

            distance = geodesic(
                (lat, lon),
                (s_lat, s_lon)
            ).km

            if distance < best_dist:

                best_dist = distance

                shelter_name = row.get(
                    "name"
                )

                if (
                    shelter_name is None
                    or
                    pd.isna(
                        shelter_name
                    )
                ):

                    shelter_name = (
                        amenity
                        .replace(
                            "_",
                            " "
                        )
                        .title()
                        + " Shelter"
                    )

                best = {

                    "name":
                    shelter_name,

                    "type":
                    amenity,

                    "lat":
                    float(
                        s_lat
                    ),

                    "lon":
                    float(
                        s_lon
                    ),

                    "distance":
                    round(
                        distance,
                        2
                    )
                }

        except Exception as e:

            continue

    # print(best)

    return best