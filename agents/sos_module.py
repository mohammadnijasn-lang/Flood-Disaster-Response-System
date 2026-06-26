import json
import os
from datetime import datetime

FILE = "active_incidents.json"

def create_sos(
    name,
    lat,
    lon
):

    incident = {

        "name": name,

        "lat": lat,

        "lon": lon,

        "time":
        str(datetime.now())
    }

    data = []

    if os.path.exists(FILE):

        with open(FILE,"r") as f:

            data = json.load(f)

    data.append(
        incident
    )

    with open(FILE,"w") as f:

        json.dump(
            data,
            f,
            indent=4
        )

def get_active_incidents():

    if not os.path.exists(FILE):

        return []

    with open(FILE,"r") as f:

        return json.load(f)