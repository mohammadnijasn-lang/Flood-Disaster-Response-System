import os


DRONE_FOLDER = "uploads/drone"


def get_latest_drone_image():

    if not os.path.exists(DRONE_FOLDER):
        return None

    files = [

        os.path.join(DRONE_FOLDER, f)

        for f in os.listdir(DRONE_FOLDER)

        if f.lower().endswith(

            (".jpg", ".jpeg", ".png", ".webp")

        )

    ]

    if len(files) == 0:
        return None

    latest = max(

        files,

        key=os.path.getmtime

    )

    return latest