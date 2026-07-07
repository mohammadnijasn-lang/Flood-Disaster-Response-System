from agents.sms_module import send_sms
from agents.citizen_db import get_all_citizens


# ----------------------------------------
# Notify all citizens in a district
# ----------------------------------------

def notify_district(district, report):

    """
    Send CrewAI disaster report
    to every citizen in the district.
    """

    print(f"\nSending report to {district}")

    citizens = get_all_citizens()

    count = 0

    for citizen in citizens:

        if citizen.get("district") != district:
            continue

        phone = citizen.get("phone", "")

        if not phone:
            continue

        if not phone.startswith("+"):

            phone = "+91" + phone

        try:

            send_sms(

                phone,

                report

            )

            print(f"✅ SMS sent to {citizen['name']}")

            count += 1

        except Exception as e:

            print(f"❌ SMS failed for {citizen['name']}")

            print(e)

    return {

        "status": "SUCCESS",

        "citizens_notified": count

    }


# ----------------------------------------
# Emergency Alert
# ----------------------------------------

def send_alert(district, message):

    citizens = get_all_citizens()

    delivered = []

    for citizen in citizens:

        if citizen.get("district") != district:
            continue

        phone = citizen.get("phone", "")

        if not phone:
            continue

        if not phone.startswith("+"):

            phone = "+91" + phone

        try:

            send_sms(

                phone,

                message

            )

            print(f"🚨 Alert sent to {citizen['name']}")

            delivered.append(

                citizen["name"]

            )

        except Exception as e:

            print(f"❌ Failed sending alert to {citizen['name']}")

            print(e)

    return {

        "district": district,

        "sent_to": delivered

    }