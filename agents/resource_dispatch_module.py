from agents.admin_module import get_resources
from agents.admin_module import update_resources
from agents.history_module import DISPATCH_HISTORY

def calculate_resources(people):

    return {

        "boats": max(
            1,
            people // 20
        ),

        "ambulances": max(
            1,
            people // 100
        ),

        "rescue_workers": max(
            5,
            people // 20
        ),

        "food_packets":
        people * 3,

        "water_packets":
        people * 5
    }


def calculate_priority(

    forecast_probability,

    people,

    sos_count,

    flood_area

):
    
    people_score = min(people, 100)

    score = (

        forecast_probability * 0.4

        +

        people_score* 0.3

        +

        sos_count * 20

        +

        flood_area * 5

    )

    return round(score, 2)

def dispatch_boats(district, count):

    resources = get_resources()

    resources["boats"] = max(0,resources["boats"]-count)

    update_resources(resources)

    DISPATCH_HISTORY.append({

    "district": district,

    "resource": "Boats",

    "count": count
})


    print(
        f"🚤 Dispatching {count} boats to {district}"
    )

def dispatch_workers(district, count):

    resources = get_resources()

    workers = resources.get("rescue_workers", 0)
    
    print(resources)

    resources["rescue_workers"] = max(0,resources["rescue_workers"]-count)

    update_resources(resources)

    DISPATCH_HISTORY.append({

    "district": district,

    "resource": "rescue_workers",

    "count": count
})

    print(
        f"👷 Dispatching {count} rescue_workers to {district}"
    )

def dispatch_ambulances(district, count):

    resources = get_resources()

    resources["ambulances"] = max(0,resources["ambulances"]-count)

    update_resources(resources)

    DISPATCH_HISTORY.append({

    "district": district,

    "resource": "ambulances",

    "count": count
})

    print(
        f"🚑 Dispatching {count} ambulances to {district}"
    )


def auto_dispatch(

    district,
    priority_score,
    resource_plan
):

    if priority_score > 80:

        dispatch_boats(
            district,
            resource_plan["boats"]
        )

        dispatch_workers(
            district,
            resource_plan["rescue_workers"]
        )

        dispatch_ambulances(
            district,
            resource_plan["ambulances"]
        )

        return "FULL DISPATCH"

    elif priority_score > 50:

        dispatch_workers(
            district,
            resource_plan["rescue_workers"]
        )

        return "PARTIAL DISPATCH"

    else:

        return "MONITOR"