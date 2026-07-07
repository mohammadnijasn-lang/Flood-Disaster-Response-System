from agents.database import get_connection


# =====================================
# SAVE DISTRICT STATUS
# =====================================

def save_district_status(data):

    conn = get_connection()
    cursor = conn.cursor()

    for district in data:

        cursor.execute(

            """

            INSERT INTO district_status(

                district,
                rainfall,
                flood_area,
                alert

            )

            VALUES(

                %s,
                %s,
                %s,
                %s

            )

            ON DUPLICATE KEY UPDATE

                rainfall = VALUES(rainfall),
                flood_area = VALUES(flood_area),
                alert = VALUES(alert)

            """,

            (

                district["district"],
                district["rainfall"],
                district["flood_area"],
                district["alert"]

            )

        )

    conn.commit()

    cursor.close()
    conn.close()


# =====================================
# GET DISTRICT STATUS
# =====================================

def get_district_status():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(

        """

        SELECT
            district,
            rainfall,
            flood_area,
            alert

        FROM district_status

        ORDER BY district

        """

    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data


# =====================================
# CLEAR DISTRICT STATUS
# =====================================

def clear_district_status():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        DELETE FROM district_status

        """

    )

    conn.commit()

    cursor.close()
    conn.close()