from agents.citizen_db import get_citizens
from agents.sms_module import send_sms

def send_alert_to_district(

    district,

    alert

):

    citizens = get_citizens()

    for citizen in citizens:

        if citizen["district"] == district:

            message = f"""

Kerala SDMA

District :

{district}

Alert :

{alert}

Please stay safe.

Emergency : 1077

"""

            send_sms(

                citizen["phone"],

                message

            )