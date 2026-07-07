from datetime import datetime
from agents.database import get_connection


def generate_alert(vision_result, incident):

    severity = vision_result["severity"]

    if severity in ["Critical", "High"]:

        priority = "HIGH"

    elif severity == "Medium":

        priority = "MEDIUM"

    else:

        priority = "LOW"

    alert = {

        "status": "ALERT",

        "priority": priority,

        "time": str(datetime.now()),

        "citizen": incident,

        "vision": vision_result,

        "message":

        f"Emergency detected near "

        f"{incident['lat']}, {incident['lon']}."

    }

    return alert


def create_admin_alert(alert):

    conn = get_connection()

    cursor = conn.cursor()

    citizen = alert.get("citizen", {})

    district = alert.get(

        "district",

        citizen.get("district", "Unknown")

    )

    phone = alert.get(

        "citizen_phone",

        citizen.get("phone", "")

    )

    cursor.execute("""

        INSERT INTO alerts(

            district,

            message,

            citizen_phone,

            status

        )

        VALUES(%s,%s,%s,%s)

    """, (

        district,

        alert.get("message", ""),

        phone,

        alert.get("status", "ALERT")

    ))

    conn.commit()

    cursor.close()

    conn.close()

def clear_admin_alerts():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("DELETE FROM alerts")

    conn.commit()

    cursor.close()

    conn.close()