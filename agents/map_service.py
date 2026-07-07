import folium
import os
from PIL import Image
import numpy as np
from folium.raster_layers import ImageOverlay

def add_flood_overlay(
    m,
    flood_mask_file,
    bbox
):

    if not os.path.exists(
        flood_mask_file
    ):

        print(
            "\nNo Flood Mask Found"
        )

        return

    west, south, east, north = bbox

    img = Image.open(
        flood_mask_file
    )

    img = img.convert(
        "RGBA"
    )

    data = np.array(img)

    red = (
        (data[:, :, 0] > 200)
        &
        (data[:, :, 1] < 50)
        &
        (data[:, :, 2] < 50)
    )

    data[red] = [
        255,
        0,
        0,
        120
    ]

    overlay = Image.fromarray(
        data
    )

    overlay.save(
        "overlay.png"
    )

    folium.raster_layers.ImageOverlay(

        image="overlay.png",

        bounds=[
            [south, west],
            [north, east]
        ],

        opacity=0.6

    ).add_to(m)


def create_map(
    lat,
    lon,
    flood_percent,
    location,
    shelter=None,
    G=None,
    route=None,
    start_node=None,
    end_node=None
):
    
    print("MAP LAT:", lat)
    print("MAP LON:", lon)

    user_lat = lat

    user_lon = lon


    m = folium.Map(
        
        location=[user_lat, user_lon],
        zoom_start=18
    )

    # =====================
    # FLOOD OVERLAY
    # =====================

    if location.lower() != "user location":

        flood_mask_file = (
            f"flood_mask_vv_vh_{location.lower()}.png"
        )

        bbox = [

            lon - 0.25,
            lat - 0.25,

            lon + 0.25,
            lat + 0.25
        ]

        add_flood_overlay(

            m,

            flood_mask_file,

            bbox
        )
    # =====================
    # USER LOCATION
    # =====================

    # if (
    #     G is not None
    #     and
    #     start_node is not None
    # ):

    #     user_lat = lat
    #     user_lon = lon

    # else:

    #     user_lat = lat
    #     user_lon = lon

    print(
    "\nMAP GPS:"
)

    print(
    user_lat,
    user_lon
)

    folium.Marker(
        [user_lat, user_lon],
        popup=f"""
        <b>{location}</b><br>
        Flood Risk: {flood_percent:.2f}%
        """,
        tooltip="User Location",
        icon=folium.Icon(color="red")
    ).add_to(m)

    # =====================
    # FLOOD AREA
    # =====================

    folium.Circle(
        [user_lat, user_lon],
        radius=11000,
        color="red",
        fill=True,
        fill_opacity=0.15,
        popup="Flood Prediction Area"
    ).add_to(m)

# =====================
# FLOOD MASK OVERLAY
# =====================

#     try:

#         flood_mask_file = (
#             f"flood_mask_vv_vh_{location}.png"
#         )

#         ImageOverlay(

#             image=flood_mask_file,

#             bounds=[

#                 [lat - 0.25, lon - 0.25],

#                 [lat + 0.25, lon + 0.25]

#             ],

#             opacity=0.4,

#             interactive=True,

#             cross_origin=False,

#             zindex=1

#         ).add_to(m)

#     except Exception as e:

#         print(
#             "Flood Overlay Error:",
#             e
#         )

    # =====================
    # SHELTER
    # =====================

    if shelter is not None:

        folium.Marker(
            [
                shelter["lat"],
                shelter["lon"]
            ],
            popup=f"""
            <b>{shelter['name']}</b><br>
            Type: {shelter['type']}<br>
            Distance: {shelter['distance']} km
            """,
            tooltip="Nearest Shelter",
            icon=folium.Icon(color="green")
        ).add_to(m)

    # =====================
# FLOODED ROAD SEGMENTS
# =====================

    if G is not None:

        for u, v, data in G.edges(data=True):

            if data.get(
                "safe_weight",
                0
            ) > data.get(
                "length",
                0
            ):

                coords = [

                    (
                        G.nodes[u]["y"],
                        G.nodes[u]["x"]
                    ),

                    (
                        G.nodes[v]["y"],
                        G.nodes[v]["x"]
                    )

                ]

                folium.PolyLine(

                    coords,

                    color="red",

                    weight=2,

                    opacity=0.4,

                    popup="Flooded Road"

                ).add_to(m)

    # =====================
    # SAFE ROUTE
    # =====================

    if G is not None and route is not None:

        route_coords = [

            (
                G.nodes[node]["y"],
                G.nodes[node]["x"]
            )

            for node in route

        ]

        folium.PolyLine(

            route_coords,

            color="blue",

            weight=8,

            opacity=0.9,

            popup="Safe Route"

        ).add_to(m)
        
    folium.LayerControl().add_to(m)

    if G is not None and route is not None:

        m.save("templates/safe_route.html")

        print("SAFE ROUTE CREATED")

    else:

        m.save("templates/flood_map.html")

        print("FLOOD MAP CREATED")

def create_flood_map(

    lat,
    lon,

    district,

    flood_percent,

    shelter

):

    m = folium.Map(

        location=[lat, lon],

        zoom_start=14

    )

    # Flood Overlay

    flood_mask = f"flood_mask_vv_vh_{district.lower()}.png"

    bbox = [

        lon-0.25,

        lat-0.25,

        lon+0.25,

        lat+0.25

    ]

    add_flood_overlay(

        m,

        flood_mask,

        bbox

    )

    # Citizen

    folium.Marker(

        [lat, lon],

        tooltip="📍 You",

        icon=folium.Icon(

            color="red"

        )

    ).add_to(m)

    # Flood Area

    folium.Circle(

        [lat, lon],

        radius=10000,

        color="red",

        fill=True,

        fill_opacity=0.2,

        popup=f"Flood Area : {flood_percent:.2f}%"

    ).add_to(m)

    # Shelter

    folium.Marker(

        [

            shelter["lat"],

            shelter["lon"]

        ],

        popup=f"""

        <b>{shelter['name']}</b><br>

        {shelter['type']}<br>

        {shelter['distance']:.2f} km

        """,

        icon=folium.Icon(

            color="green"

        )

    ).add_to(m)

    m.save(

        "templates/flood_map.html"

    )
    