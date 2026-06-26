import osmnx as ox
import numpy as np
import rasterio

from rasterio.features import rasterize
from rasterio.transform import from_bounds


def fetch_hydro(
    bbox,
    output_file="hydro.tiff"
):

    west, south, east, north = bbox

    print("\nFetching Hydro Data...")

    tags = {

        "natural": ["water"],

        "waterway": True
    }

    try:

        water = ox.features_from_bbox(
            (west, south, east, north),
            tags
        )

    except Exception as e:

        print(
            "Hydro Fetch Error:",
            e
        )

        return None, 0

    if len(water) == 0:

        print(
            "No water bodies found"
        )

        return None, 0

    print(
        f"Found {len(water)} water features"
    )

    width = 512
    height = 512

    transform = from_bounds(

        west,
        south,
        east,
        north,

        width,
        height
    )

    shapes = [

        (geom, 1)

        for geom in water.geometry

        if geom is not None
    ]

    raster = rasterize(

        shapes,

        out_shape=(
            height,
            width
        ),

        fill=0,

        transform=transform,

        dtype=np.uint8
    )

    with rasterio.open(

        output_file,

        "w",

        driver="GTiff",

        height=height,

        width=width,

        count=1,

        dtype=raster.dtype,

        transform=transform

    ) as dst:

        dst.write(
            raster,
            1
        )

    hydro_percent = (

        raster.sum()

        /

        raster.size

    ) * 100

    print(
        f"Hydro Saved: {output_file}"
    )

    return (
        output_file,
        hydro_percent
    )

    return None


def get_real_flood_risk(

    flood_percent,
    hydro_percent

):

    if flood_percent < 2:

        return "Low"

    elif flood_percent < 8:

        return "Moderate"

    elif flood_percent < 15:

        return "High"

    else:

        return "Severe"