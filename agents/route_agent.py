import os

import osmnx as ox
import networkx as nx
import numpy as np
from PIL import Image


def latlon_to_pixel(
    lat,
    lon,
    bbox,
    width,
    height
):

    west, south, east, north = bbox

    x = int(
        (lon - west)
        /
        (east - west)
        *
        width
    )

    y = int(
        (north - lat)
        /
        (north - south)
        *
        height
    )

    return x, y


def get_safe_route(

    user_lat,
    user_lon,
    shelter_lat,
    shelter_lon,
    flood_mask_path,
    bbox
):

    G = ox.graph_from_point(

        (user_lat, user_lon),

        dist=20000,

        network_type="drive"
    )

    start = ox.distance.nearest_nodes(
        G,
        user_lon,
        user_lat
    )

    end = ox.distance.nearest_nodes(
        G,
        shelter_lon,
        shelter_lat
    )

    mask = Image.open(
        flood_mask_path
    )

    print(
    "MASK PATH:",
    os.path.abspath(
        flood_mask_path
    )
)

    mask = mask.convert("L")

    mask = np.array(mask)

    height, width = mask.shape

    for u, v, data in G.edges(data=True):

        data["safe_weight"] = data["length"]

        try:

            node = G.nodes[u]

            lat = node["y"]

            lon = node["x"]

            px, py = latlon_to_pixel(

                lat,
                lon,

                bbox,

                width,
                height
            )

            if (
                px >= 0
                and py >= 0
                and
                px < width
                and
                py < height
            ):

                pixel = mask[py, px]

                if pixel > 100:

                    data["safe_weight"] += 100000

        except:

            pass

    route = nx.shortest_path(

        G,

        start,

        end,

        weight="safe_weight"
    )

    return (
        G,
        route,
        start,
        end
    )