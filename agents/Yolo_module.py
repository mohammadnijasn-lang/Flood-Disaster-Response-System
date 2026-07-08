from ultralytics import YOLO

# =====================
# LAZY LOAD YOLO MODEL
# =====================

model = None


def get_yolo():

    global model

    if model is None:

        print("Loading YOLO Model...")

        model = YOLO(
            "yolov8n.pt"
        )

        print("YOLO Model Loaded")

    return model


def count_people(image_path):

    model = get_yolo()

    results = model(
        image_path
    )

    people_count = 0

    vehicle_count = 0

    for r in results:

        classes = r.boxes.cls.tolist()

        for c in classes:

            c = int(c)

            if c == 0:
                people_count += 1

            elif c in [2, 3, 5, 7]:
                vehicle_count += 1

    return {

        "people_count": people_count,

        "vehicle_count": vehicle_count

    }