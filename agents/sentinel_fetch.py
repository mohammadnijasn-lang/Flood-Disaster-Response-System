from agents.live_fetch_agent import (
    fetch_sentinel,
    get_token
)

from agents.flood_agent import predict_flood

from agents.location_agent import (
    get_coordinates,
    create_bbox
)

from agents.shelter_agent import (
    find_nearest_shelter
)

from agents.route_agent import (
    get_safe_route
)

from agents.dem_fetch import fetch_dem

from agents.hydro_fetch import (
    fetch_hydro,
    get_real_flood_risk
)

def get_flood_severity(
    flood_percent
):

    if flood_percent < 1:

        return "No Flood"

    elif flood_percent < 5:

        return "Minor Flooding"

    elif flood_percent < 10:

        return "Moderate Flooding"

    elif flood_percent < 20:

        return "Severe Flooding"

    else:

        return "Extreme Flooding"


def predict_location(location):

    print(
        f"\nFetching Sentinel data for {location}..."
    )

    # =====================
    # LOCATION
    # =====================

    lat, lon = get_coordinates(
        location
    )

    bbox = create_bbox(
        lat,
        lon,
        size=0.25
    )

    token = get_token()

    # =====================
    # SENTINEL
    # =====================

    tif_file, image_date = fetch_sentinel(
        location
    )

    # =====================
    # DEM
    # =====================

    dem_file = fetch_dem(
        bbox,
        token,
        f"dem_{location}.tiff"
    )

    # =====================
    # DEM ANALYSIS
    # =====================

    import rasterio

    with rasterio.open(
        dem_file
    ) as src:

        dem = src.read(1)

    dem_min = float(
        dem.min()
    )

    dem_max = float(
        dem.max()
    )

    dem_mean = float(
        dem.mean()
    )

    if dem_mean < 50:

        terrain = "Low Lying"

    elif dem_mean < 300:

        terrain = "Moderate Elevation"

    else:

        terrain = "High Elevation"

        # =====================
        # HYDRO
        # =====================

    hydro_file, hydro_percent = fetch_hydro(
            bbox,
            f"hydro_{location}.tiff"
        )
    if hydro_file is None:

        hydro_file= (
            "agents/data/default_hydro.tiff"
    )
        hydro_percent = 0

    print(
            "\nRunning flood prediction..."
        )

        # =====================
        # FLOOD MODEL
        # =====================

    flood_percent = predict_flood(
            tif_file,
            dem_file,
            hydro_file
        )

    risk = get_real_flood_risk(
            flood_percent,
            hydro_percent
        )
    severity = get_flood_severity(
    flood_percent
)

        # =====================
        # SHELTER
        # =====================

    shelter = find_nearest_shelter(
            lat,
            lon
        )

    if shelter is None:

            print(
                "\nNo shelter found"
            )

            return {

                "district":
                location,

                "hydro_coverage":
                round(
                    hydro_percent,
                    2
                ),

                "flood_area":
                round(
                    flood_percent,
                    2
                ),

                "risk_level":
                risk,

                "nearest_shelter":
                None
            }

    # =====================
    # ROUTE
    # =====================

    flood_mask_path = (

    f"flood_mask_vv_vh_"
    f"{location.lower()}.png"

)

    # G, route, start, end = get_safe_route(

    #     lat,
    #     lon,

    #     shelter["lat"],
    #     shelter["lon"],
    #     flood_mask_path,
    #     bbox


    # )

    # =====================
    # MAP
    # =====================

    # create_map(

    #     lat,
    #     lon,

    #     flood_percent,

    #     location,

    #     shelter,

    #     G,

    #     route,

    #     start,

    #     end
    # )

    # webbrowser.open(
    #     "flood_map.html"
    # )

    return {

        "district": location,

        "lat": lat,

        "lon": lon,

        "terrain": terrain,

        "hydro_coverage": round(hydro_percent,2),

        "flood_area": round(flood_percent,2),

        "risk_level": risk,

        "severity": severity,

        "nearest_shelter": {

            "name": shelter["name"],

            "type": shelter["type"],

            "distance": shelter["distance"],

            "lat": shelter["lat"],

            "lon": shelter["lon"]

        },

        "mask_path": flood_mask_path,

        "bbox": bbox,

        "image_path": tif_file

    }


if __name__ == "__main__":

    result = predict_location(
        "Kollam"
    )

    print(result)