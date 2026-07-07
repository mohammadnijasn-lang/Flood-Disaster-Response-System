from agents.notification_module import send_alert


def create_alert(

    district,

    vision_result

):

    severity = vision_result["severity"]

    message = f"""

Flood Severity : {severity}

People At Risk : {vision_result['people_at_risk']}

Road Blocked : {vision_result['road_blocked']}

Recommendation :

{vision_result['recommendation']}

"""

    print("\nALERT CREATED")

    return send_alert(

        district,

        message

    )