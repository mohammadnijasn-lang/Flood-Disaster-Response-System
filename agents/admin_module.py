from agents.database import get_connection
import os

# -----------------------------------
# Drone Images
# -----------------------------------

DRONE_FOLDER = "uploads/drone"


def add_drone_image(path):
    # Image is already saved in uploads/drone
    pass


def get_drone_images():

    files = []

    if not os.path.exists(DRONE_FOLDER):
        return files

    for f in os.listdir(DRONE_FOLDER):

        if f.endswith((".jpg", ".jpeg", ".png")):

            files.append(

                os.path.join(

                    DRONE_FOLDER,

                    f

                )

            )

    return files


# -----------------------------------
# Resources (MySQL)
# -----------------------------------

def get_resources():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""

        SELECT *

        FROM resources

        ORDER BY id DESC

        LIMIT 1

    """)

    row = cursor.fetchone()

    cursor.close()

    conn.close()

    if row is None:

        return {

            "boats": 0,

            "ambulances": 0,

            "rescue_workers": 0,

            "food_packets": 0,

            "water_packets": 0

        }

    return {

        "boats": row["boats"],

        "ambulances": row["ambulances"],

        "rescue_workers": row["rescue_workers"],

        "food_packets": row["food_packets"],

        "water_packets": row["water_packets"]

    }


def update_resources(data):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE resources

        SET

            boats=%s,

            ambulances=%s,

            rescue_workers=%s,

            food_packets=%s,

            water_packets=%s,

            updated_at=NOW()

        ORDER BY id DESC

        LIMIT 1

    """, (

        data["boats"],

        data["ambulances"],

        data["rescue_workers"],

        data["food_packets"],

        data["water_packets"]

    ))

    conn.commit()

    cursor.close()

    conn.close()