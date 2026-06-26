from fileinput import filename
import hashlib
from pyexpat import features

import requests

from agents.location_agent import create_bbox
from datetime import (
    datetime,
    timedelta,
    timezone
)

from agents.location_agent import (
    get_coordinates,
    create_bbox
)

import hashlib

CLIENT_ID = "sh-5ba22570-31e3-4d9e-8840-4796b8bb43a2"
CLIENT_SECRET = "FOGDX7B5bJQhmSwsFn6K0uY7tU1BtTC3"

# =====================
# TOKEN
# =====================

def get_token():

    # print("\nRequesting access token...")

    token_response = requests.post(
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=30
    )

    # print("Token received")

    # print(
    #     "Token Response:",
    #     token_response.status_code
    # )

    token_response.raise_for_status()

    return token_response.json()["access_token"]


# =====================
# CATALOG QUERY
# =====================

def get_latest_image_date(
    bbox,
    start_date,
    end_date
):

    west, south, east, north = bbox

    url = (
        "https://catalogue.dataspace.copernicus.eu/stac/search"
    )

    params = {

        "collections":
        "sentinel-1-grd",

        "bbox":
        f"{west},{south},{east},{north}",

        "datetime":
        f"{start_date.strftime('%Y-%m-%dT00:00:00Z')}/"
        f"{end_date.strftime('%Y-%m-%dT23:59:59Z')}",

        "limit":
        1
    }

    try:

        r = requests.get(
            url,
            params=params,
            timeout=60
        )

        print(
            "\nCatalog Status:",
            r.status_code
        )

        if r.status_code != 200:

            print(r.text[:500])

            return None

        data = r.json()

        features = data.get(
            "features",
            []
        )

        if len(features) == 0:

            return None

        props = features[0][
            "properties"
        ]

        print(
            "\nProperties:"
        )

        print(props)

        return (
            props.get(
                "datetime"
            )
            or
            props.get(
                "start_datetime"
            )
        )

    except Exception as e:

        print(
            "\nCatalog Exception:"
        )

        print(str(e))

        return None

# =====================
# SENTINEL DOWNLOAD
# =====================

def fetch_sentinel(location):

    # -----------------
    # LOCATION
    # -----------------

    lat, lon = get_coordinates(
        location
    )

    bbox = create_bbox(
        lat,
        lon,
        size=0.25
    )

    # print("\nLocation :", location)
    # print("Latitude :", lat)
    # print("Longitude:", lon)
    # print("BBox     :", bbox)

    # -----------------
    # LAST 7 DAYS
    # -----------------

    end_date = datetime.now(timezone.utc)

    start_date = (
        end_date
        - timedelta(days=30)
    )

    # print(
    #     "\nSearching:",
    #     start_date.date(),
    #     "->",
    #     end_date.date()
    # )

    # -----------------
    # TOKEN
    # -----------------

    token = get_token()

    # -----------------
    # IMAGE DATE
    # -----------------
    # try:
    #     image_date = get_latest_image_date(
    #         token,
    #         bbox,
    #         start_date,
    #         end_date
    #     )
    # except Exception as e:
    #     print(
    #     "\nCould not fetch acquisition date"
    # )

    image_date = "Latest Available (Last 30 Days)"

        # print(str(e))

        # image_date = "Unknown"

    if image_date:

        print(
        f"\nSentinel Acquisition: "
        f"{image_date}"
    )

    else:

        print(
        "\nSentinel Acquisition: Unknown"
    )

    # -----------------
    # HEADERS
    # -----------------

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # -----------------
    # PROCESS API
    # -----------------

    payload = {

        "input": {

            "bounds": {
                "bbox": bbox
            },

            "data": [{

    "type": "sentinel-1-grd",

    "dataFilter": {

        "timeRange": {

            "from":
            start_date.strftime(
                "%Y-%m-%dT00:00:00Z"
            ),

            "to":
            end_date.strftime(
                "%Y-%m-%dT23:59:59Z"
            )
        }
    }
}]
#             "data": [{
#                 "type": "sentinel-1-grd",

#                 "dataFilter": {
#                     "timeRange": {
#                         "from": ...,
#             "to": ...
#         }
#     }
# }]
        },

        "output": {

            "width": 512,
            "height": 512,

            "responses": [{

                "identifier": "default",

                "format": {
                    "type": "image/tiff"
                }
            }]
        },

        "evalscript": """
//VERSION=3

function setup() {
    return {
        input: ["VV", "VH"],
        output: {
            bands: 2,
            sampleType: "FLOAT32"
        }
    };
}

function evaluatePixel(sample) {
    return [
        sample.VV,
        sample.VH
    ];
}
"""
    }

    # -----------------
    # DOWNLOAD
    # -----------------

    r = requests.post(
        "https://sh.dataspace.copernicus.eu/api/v1/process",
        headers=headers,
        json=payload
    )

    # print(
    #     "\nHTTP Status:",
    #     r.status_code
    # )

    if r.status_code != 200:

        print(
            "\nError Response:"
        )

        print(r.text)

        raise Exception(
            "Sentinel download failed"
        )

    # -----------------
    # SAVE FILE
    # -----------------

    safe_name = (
        location
        .replace(" ", "_")
        .replace("/", "_")
    )

    filename = (
        f"vv_vh_{safe_name}.tif"
    )

    with open(
        filename,
        "wb"
    ) as f:

        f.write(
            r.content
        )

    import hashlib
    import os

    with open(filename, "rb") as f:

        md5 = hashlib.md5(
        f.read()
    ).hexdigest()

    print(
    "\nDownload Time:",
    datetime.now()
)

    print(
    "File Size:",
    os.path.getsize(filename)
)

    print(
    "Image Hash:",
    md5
)

    print(
        "\nSaved:",
        filename
    )

    with open(
        filename,
    "rb"
    ) as f:

        md5 = hashlib.md5(
        f.read()
    ).hexdigest()

    print(
    "\nImage Hash:",
    md5
)

    return (
        filename,
        image_date
    )


# =====================
# TEST
# =====================

if __name__ == "__main__":

    file_name, image_date = fetch_sentinel(
        "Kottarakkara"
    )

    print("\nFile :", file_name)
    print("Date :", image_date)