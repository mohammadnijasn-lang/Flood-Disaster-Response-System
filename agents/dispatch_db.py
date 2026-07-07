from agents.database import get_connection


# -----------------------------------
# Add Dispatch Record
# -----------------------------------

def add_dispatch(district, resource, count):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO dispatch_history(

            district,
            resource,
            count

        )

        VALUES(%s,%s,%s)

    """,(

        district,
        resource,
        count

    ))

    conn.commit()

    cursor.close()
    conn.close()


# -----------------------------------
# Get Dispatch History
# -----------------------------------

def get_dispatch_history():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""

        SELECT *

        FROM dispatch_history

        ORDER BY created_at DESC

    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


# -----------------------------------
# Clear History
# -----------------------------------

def clear_dispatch_history():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM dispatch_history

    """)

    conn.commit()

    cursor.close()
    conn.close()