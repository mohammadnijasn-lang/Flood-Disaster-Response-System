from agents.admin_module import get_resources
from agents.admin_module import update_resources
from agents.dispatch_db import add_dispatch


def dispatch_resources(district, resources, station):

    stock = get_resources()

    stock["boats"] -= resources["boats"]
    stock["ambulances"] -= resources["ambulances"]
    stock["rescue_workers"] -= resources["rescue_workers"]
    stock["food_packets"] -= resources["food_packets"]
    stock["water_packets"] -= resources["water_packets"]

    update_resources(stock)

    add_dispatch(
        district,
        "BOATS",
        resources["boats"]
    )

    add_dispatch(
        district,
        "AMBULANCES",
        resources["ambulances"]
    )

    add_dispatch(
        district,
        "RESCUE WORKERS",
        resources["rescue_workers"]
    )

    add_dispatch(
        district,
        "FOOD PACKETS",
        resources["food_packets"]
    )

    add_dispatch(
        district,
        "WATER PACKETS",
        resources["water_packets"]
    )

    return {

        "station": station,

        "status": "DISPATCHED"

    }