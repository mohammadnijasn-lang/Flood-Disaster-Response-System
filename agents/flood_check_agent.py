import cv2


def is_user_in_flood(

    flood_mask_file,

    lat,

    lon,

    bbox
):

    mask = cv2.imread(

        flood_mask_file,

        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:

        print(
            "\nFlood Mask Not Found"
        )

        return False

    h, w = mask.shape[:2]

    west, south, east, north = bbox

    x = int(

        (lon - west)

        /

        (east - west)

        * w
    )

    y = int(

        (north - lat)

        /

        (north - south)

        * h
    )

    x = max(
        0,
        min(x, w - 1)
    )

    y = max(
        0,
        min(y, h - 1)
    )

    pixel = mask[y, x]

    print(f"Pixel Value: {pixel}")
    print(f"Pixel Position: ({x}, {y})")

    return bool(pixel > 0)