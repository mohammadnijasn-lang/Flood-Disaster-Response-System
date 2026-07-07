from agents.database import get_connection
import os

DRONE_FOLDER = "uploads/drone"


def add_drone(filename):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO drone_images(filename)
        VALUES(%s)
        """,
        (filename,)
    )

    conn.commit()
    conn.close()


def latest_drone():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT filename
        FROM drone_images
        ORDER BY uploaded_at DESC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return row["filename"]


def get_all_drones():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM drone_images
        ORDER BY uploaded_at DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows