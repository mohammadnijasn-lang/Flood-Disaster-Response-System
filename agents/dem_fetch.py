import requests


def fetch_dem(
    bbox,
    token,
    filename="dem.tiff"
):

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {

        "input": {

            "bounds": {
                "bbox": bbox
            },

            "data": [{
                "type": "dem"
            }]
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
        input: ["DEM"],
        output: {
            bands: 1,
            sampleType: "FLOAT32"
        }
    };
}

function evaluatePixel(sample) {
    return [sample.DEM];
}
"""
    }

    r = requests.post(
        "https://sh.dataspace.copernicus.eu/api/v1/process",
        headers=headers,
        json=payload
    )

    # print("DEM Status:", r.status_code)

    if r.status_code != 200:

        print(r.text)

        raise Exception(
            "DEM Download Failed"
        )

    with open(
        filename,
        "wb"
    ) as f:

        f.write(
            r.content
        )

    # print(
    #     f"DEM Saved: {filename}"
    # )

    return filename