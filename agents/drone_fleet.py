import json

DISPATCH_FILE = "dispatch_log.json"


def dispatch_team(

    district,
    boats,
    ambulances,
    rescue_workers

):

    data = {

        "district": district,

        "boats": boats,

        "ambulances": ambulances,

        "workers": rescue_workers
    }

    try:

        with open(
            DISPATCH_FILE,
            "r"
        ) as f:

            logs = json.load(f)

    except:

        logs = []

    logs.append(data)

    with open(
        DISPATCH_FILE,
        "w"
    ) as f:

        json.dump(
            logs,
            f,
            indent=4
        )

    return data