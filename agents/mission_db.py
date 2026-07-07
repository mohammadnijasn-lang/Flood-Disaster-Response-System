from agents.database import get_connection


# =====================================
# GET ALL MISSIONS
# =====================================

def get_missions():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(

        """

        SELECT *

        FROM missions

        ORDER BY created_at DESC

        """

    )

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    missions = []

    for row in rows:

        mission = {

            "id": row["id"],

            "district": row["district"],

            "priority": row["priority"],

            "priority_score": row["priority_score"],

            "boats": row["boats"],

            "ambulances": row["ambulances"],

            "rescue_workers": row["rescue_workers"],

            "food_packets": row["food_packets"],

            "water_packets": row["water_packets"],

            "status": row["status"],

            "station": {

                "name": row["station_name"],

                "lat": row["station_lat"],

                "lon": row["station_lon"]

            },

            "dispatch": {

                "status": "DISPATCHED"

            }

        }

        missions.append(mission)

    return missions


# =====================================
# ADD MISSION
# =====================================

def add_mission(mission):

    conn = get_connection()

    cursor = conn.cursor()

    station = mission.get("station", {})

    cursor.execute(

        """

        INSERT INTO missions(

            district,

            priority,

            priority_score,

            station_name,

            station_lat,

            station_lon,

            boats,

            ambulances,

            rescue_workers,

            food_packets,

            water_packets,

            status

        )

        VALUES(

            %s,

            %s,

            %s,

            %s,

            %s,

            %s,

            %s,

            %s,

            %s,

            %s,

            %s,

            %s

        )

        """,

        (

            mission.get("district"),

            mission.get("priority"),

            mission.get("priority_score"),

            station.get("name"),

            station.get("lat"),

            station.get("lon"),

            mission.get("boats"),

            mission.get("ambulances"),

            mission.get("rescue_workers"),

            mission.get("food_packets"),

            mission.get("water_packets"),

            mission.get("status", "ACTIVE")

        )

    )

    conn.commit()

    cursor.close()

    conn.close()


# =====================================
# UPDATE STATUS
# =====================================

def update_status(

    mission_id,

    status

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        UPDATE missions

        SET status=%s

        WHERE id=%s

        """,

        (

            status,

            mission_id

        )

    )

    conn.commit()

    cursor.close()

    conn.close()


# =====================================
# CLEAR MISSIONS
# =====================================

def clear_missions():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        DELETE FROM missions

        """

    )

    conn.commit()

    cursor.close()

    conn.close()