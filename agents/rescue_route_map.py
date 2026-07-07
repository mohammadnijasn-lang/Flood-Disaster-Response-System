import folium


def create_rescue_route(

    rescue_lat,
    rescue_lon,

    user_lat,
    user_lon,

    G,
    route

):
    """
    Creates rescue route map from
    NetworkX graph and route.
    """

    # -----------------------------
    # Convert route nodes to Lat/Lon
    # -----------------------------

    coords = []

    for node in route:

        coords.append(

            (

                G.nodes[node]["y"],

                G.nodes[node]["x"]

            )

        )

    # -----------------------------
    # Create Map
    # -----------------------------

    m = folium.Map(

        location=[user_lat, user_lon],

        zoom_start=14,

        tiles="OpenStreetMap"

    )

    # -----------------------------
    # Rescue Team Marker
    # -----------------------------

    folium.Marker(

        [rescue_lat, rescue_lon],

        popup="🚑 Rescue Team",

        tooltip="Rescue Team",

        icon=folium.Icon(

            color="green",

            icon="plus"

        )

    ).add_to(m)

    # -----------------------------
    # Citizen Marker
    # -----------------------------

    folium.Marker(

        [user_lat, user_lon],

        popup="🆘 Citizen",

        tooltip="Citizen",

        icon=folium.Icon(

            color="red",

            icon="user"

        )

    ).add_to(m)

    # -----------------------------
    # Rescue Route
    # -----------------------------

    folium.PolyLine(

        coords,

        color="blue",

        weight=6,

        opacity=1

    ).add_to(m)

    # -----------------------------
    # Fit map to route
    # -----------------------------

    m.fit_bounds(coords)

    # -----------------------------
    # Save
    # -----------------------------

    m.save(

        "templates/rescue_route.html"

    )