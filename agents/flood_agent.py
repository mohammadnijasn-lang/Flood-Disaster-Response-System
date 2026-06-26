import cv2
import torch
import rasterio
import numpy as np
import segmentation_models_pytorch as smp

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# =====================
# LOAD MODEL
# =====================

model = smp.UnetPlusPlus(
    encoder_name="efficientnet-b3",
    encoder_weights=None,
    in_channels=4,
    classes=1
)

model.load_state_dict(
    torch.load(
        "best_model.pth",
        map_location=DEVICE
    )
)

model = model.to(DEVICE)
model.eval()

print("Flood Model Loaded")


# =====================
# PREDICT
# =====================

def predict_flood(sentinel_file,dem_file,hydro_file):

    # -----------------
    # SAR
    # -----------------

    with rasterio.open(
        sentinel_file
    ) as src:

        vv = src.read(1)
        vh = src.read(2)

    # vv = vv.astype(np.float32)
    # vh = vh.astype(np.float32)

    # vv = vv * 5000
    # vh = vh * 5000

    # image = np.stack(
    #     [vv, vh],
    #     axis=-1
    # )

    # image = np.log1p(image)

    # image = image / image.max()
    vv = vv.astype(np.float32)
    vh = vh.astype(np.float32)

    image = np.stack(
            [vv, vh],
            axis=-1
        )

        # SAME AS TRAINING

    image = image / 30.0

    image = np.clip(
            image,
            0,
            1
        )

    # -----------------
    # DEM
    # -----------------

    with rasterio.open(
    dem_file
) as src:

        dem = src.read(1)

#     print(
#     "\nUsing DEM:",
#     dem_file
# )
    raw_dem = dem.copy()
    # print("Raw DEM Min:", raw_dem.min())
    # print("Raw DEM Max:", raw_dem.max())

    dem = dem.astype(np.float32)

    dem = (
        dem - dem.min()
    ) / (
        dem.max() - dem.min() + 1e-8
    )
    print("\nUsing DEM:", dem_file)

    # print("DEM Min:", dem.min())
    # print("DEM Max:", dem.max())
    # -----------------
    # HYDRO
    # -----------------

    with rasterio.open(
        hydro_file  
    ) as src:

        hydro = src.read(1)

    hydro = hydro.astype(np.float32)

    hydro = (
        hydro - hydro.min()
    ) / (
        hydro.max() - hydro.min() + 1e-8
    )

    # -----------------
    # RESIZE
    # -----------------

    h, w, _ = image.shape

    dem = cv2.resize(
        dem,
        (w, h)
    )

    hydro = cv2.resize(
        hydro,
        (w, h)
    )

    dem = np.expand_dims(
        dem,
        axis=-1
    )

    hydro = np.expand_dims(
        hydro,
        axis=-1
    )

    image = np.concatenate(
        [image, dem, hydro],
        axis=-1
    )

    image = cv2.resize(
        image,
        (256,256)
    )

    image = np.transpose(
        image,
        (2,0,1)
    )

    image = torch.tensor(
        image,
        dtype=torch.float32
    ).unsqueeze(0)

    image = image.to(DEVICE)

    # -----------------
    # PREDICT
    # -----------------

    with torch.no_grad():

        pred = model(image)

        pred = torch.sigmoid(
            pred
        )
    color_mask = np.zeros(
    (256,256,3),
    dtype=np.uint8
)

    mask = pred[0,0].cpu().numpy()

    # print(
#     "Mask Max:",
#     mask.max()
# )

#     print(
#     "Mask Mean:",
#     mask.mean()
# )
    raw_mask = (mask * 255).astype(np.uint8)

    cv2.imwrite(
    "raw_prediction.png",
    raw_mask
)

    binary_mask = (
        mask > 0.05
    ).astype(np.uint8)


    # Black background
    # Red flood pixels

    color_mask = np.zeros(
        (256,256,3),
        dtype=np.uint8
    )
    

    color_mask[
        binary_mask == 1
    ] = [0,0,255]

    district = sentinel_file.replace(
    "vv_vh_",
    ""
).replace(
    ".tif",
    ""
).lower()

    mask_file = (
    f"flood_mask_vv_vh_{district}.png"
)


    cv2.imwrite(
        mask_file,
        color_mask
    )

#     print(
#     f"Saved: {mask_file}"
# )

    # -----------------
    # FLOOD %
    # -----------------

    flood_percent = (
        binary_mask.sum()
        /
        binary_mask.size
    ) * 100

    return flood_percent