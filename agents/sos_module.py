from agents.database import get_connection


# =====================================
# CREATE SOS
# =====================================

def create_sos(

    name,
    lat,
    lon,
    phone,
    district

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        INSERT INTO incidents(

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
            "ACTIVE"

        )

    )

    conn.commit()

    cursor.close()

    conn.close()


# =====================================
# GET ALL INCIDENTS
# =====================================

def get_active_incidents():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(

        """

        SELECT

            id,

            name,

            phone,

            district,

            latitude AS lat,

            longitude AS lon,

            status,

            created_at AS time

        FROM incidents

        ORDER BY created_at DESC

        """

    )

    incidents = cursor.fetchall()

    cursor.close()

    conn.close()

    return incidents


# =====================================
# UPDATE STATUS
# =====================================

def update_incident_status(

    phone,
    status

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        UPDATE incidents

        SET status=%s

        WHERE phone=%s

        """,

        (

            status,
            phone

        )

    )

    conn.commit()

    cursor.close()

    conn.close()


# =====================================
# SOS COUNT
# =====================================

def get_sos_count(

    district

):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(

        """

        SELECT COUNT(*) AS total

        FROM incidents

        WHERE

            district=%s

            AND

            status='ACTIVE'

        """,

        (

            district,

        )

    )

    total = cursor.fetchone()["total"]

    cursor.close()

    conn.close()

    return total


# =====================================
# DELETE INCIDENT
# =====================================

def delete_incident(

    id

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        DELETE

        FROM incidents

        WHERE id=%s

        """,

        (

            id,

        )

    )

    conn.commit()

    cursor.close()

    conn.close()