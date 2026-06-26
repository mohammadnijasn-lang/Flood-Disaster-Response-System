from ultralytics import YOLO

model = YOLO(
    "yolov8n.pt"
)

def count_people(image_path):

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

        "people_count":
        people_count,

        "vehicle_count":
        vehicle_count
    }