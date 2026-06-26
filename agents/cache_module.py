import json
import os

CACHE_FILE = (
    "district_cache.json"
)

def save_cache(data):

    with open(
        CACHE_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

def load_cache():

    if not os.path.exists(
        CACHE_FILE
    ):

        return None

    with open(
        CACHE_FILE
    ) as f:

        return json.load(f)