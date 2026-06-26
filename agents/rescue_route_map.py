import folium


def create_rescue_route(

    rescue_lat,

    rescue_lon,

    user_lat,

    user_lon,

    coords
):
    

    m = folium.Map(

        location=[user_lat, user_lon],

        zoom_start=14

    )

    folium.Marker(

        [rescue_lat, rescue_lon],

        tooltip="🚑 Rescue Team",

        icon=folium.Icon(color="green")

    ).add_to(m)

    folium.Marker(

        [user_lat, user_lon],

        tooltip="🆘 Citizen",

        icon=folium.Icon(color="red")

    ).add_to(m)

    folium.PolyLine(

        coords,

        color="blue",

        weight=6

    ).add_to(m)

    m.save("templates/rescue_route.html")