import requests

CLIENT_ID = "sh-5ba22570-31e3-4d9e-8840-4796b8bb43a2"
CLIENT_SECRET = "FOGDX7B5bJQhmSwsFn6K0uY7tU1BtTC3".strip()

# Get token
token_response = requests.post(
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
)

token = token_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "input": {
        "bounds": {
            "bbox": [76.85, 8.45, 77.05, 8.65]
        },
        "data": [{
            "type": "sentinel-1-grd"
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

# Send request
r = requests.post(
    "https://sh.dataspace.copernicus.eu/api/v1/process",
    headers=headers,
    json=payload
)

# Check response
with open("vv_vh.tif", "wb") as f:
    f.write(r.content)

print("Saved vv_vh.tif")