from agents.database import get_connection


# =====================================
# CREATE / UPDATE CITIZEN
# =====================================

def create_location(

    name,
    phone,
    lat,
    lon,
    district

):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(

        """

        SELECT id

        FROM citizens

        WHERE phone=%s

        """,

        (phone,)

    )

    citizen = cursor.fetchone()

    # -----------------------------
    # Update Existing Citizen
    # -----------------------------

    if citizen:

        cursor.execute(

            """

            UPDATE citizens

            SET

                name=%s,

                latitude=%s,

                longitude=%s,

                district=%s,

                status='SAFE'

            WHERE phone=%s

            """,

            (

                name,
                lat,
                lon,
                district,
                phone

            )

        )

    # -----------------------------
    # Insert New Citizen
    # -----------------------------

    else:

        cursor.execute(

            """

            INSERT INTO citizens(

                name,

                phone,

                district,

                latitude,

                longitude,

                status

            )

            VALUES(

                %s,

                %s,

                %s,

                %s,

                %s,

                %s

            )

            """,

            (

                name,
                phone,
                district,
                lat,
                lon,
                "SAFE"

            )

        )

    conn.commit()

    cursor.close()

    conn.close()


# =====================================
# GET ALL CITIZENS
# =====================================

def get_all_citizens():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(

        """

        SELECT *

        FROM citizens

        ORDER BY created_at DESC

        """

    )

    citizens = cursor.fetchall()

    cursor.close()

    conn.close()

    return citizens