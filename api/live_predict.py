import torch
import cv2
import rasterio
import numpy as np
import segmentation_models_pytorch as smp
import matplotlib.pyplot as plt

# =====================
# DEVICE
# =====================

import os

print("Current Directory:")
print(os.getcwd())

print("Model Exists:",
      os.path.exists("../best_model.pth"))

print("DEM Exists:",
      os.path.exists(
          "../inference/sample_data/dem.tiff"
      ))

print("Hydro Exists:",
      os.path.exists(
          "../inference/sample_data/hydro.tiff"
      ))

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# =====================
# MODEL
# =====================

model = smp.UnetPlusPlus(
    encoder_name="efficientnet-b3",
    encoder_weights=None,
    in_channels=4,
    classes=1
)

model.load_state_dict(
    torch.load(
        "../best_model.pth",
        map_location=device
    )
)


model = model.to(device)
model.eval()

print("Model Loaded")

# =====================
# READ VV/VH
# =====================

with rasterio.open("vv_vh.tif") as src:

    vv = src.read(1)
    vh = src.read(2)

print("VV:", vv.min(), vv.max())
print("VH:", vh.min(), vh.max())

# =====================
# COPERNICUS → MMFLOOD
# =====================

vv = vv.astype(np.float32)
vh = vh.astype(np.float32)

# scaling factor we discovered
vv = vv * 5000
vh = vh * 5000

image = np.stack(
    [vv, vh],
    axis=-1
)

image = np.log1p(image)
image = image / image.max()

print(
    "Normalized:",
    image.min(),
    image.max(),
    image.mean()
)

# =====================
# DEM
# =====================

with rasterio.open(
    "../inference/sample_data/dem.tiff"
) as src:

    dem = src.read(1)

dem = dem.astype(np.float32)

dem = (
    dem - dem.min()
) / (
    dem.max() - dem.min() + 1e-8
)

# =====================
# HYDRO
# =====================

with rasterio.open(
    "../inference/sample_data/hydro.tiff"
) as src:

    hydro = src.read(1)

hydro = hydro.astype(np.float32)

hydro = (
    hydro - hydro.min()
) / (
    hydro.max() - hydro.min() + 1e-8
)

# =====================
# RESIZE DEM/HYDRO
# =====================

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

print("Final Shape:", image.shape)

# =====================
# MODEL INPUT
# =====================

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
).unsqueeze(0).to(device)

# =====================
# PREDICT
# =====================

with torch.no_grad():

    pred = model(image)

    pred = torch.sigmoid(pred)

mask = pred[0,0].cpu().numpy()

print(
    "Prediction Range:",
    mask.min(),
    mask.max(),
    mask.mean()
)

binary = (
    mask > 0.05
).astype(np.uint8)

flood_percent = (
    binary.sum() /
    binary.size
) * 100

print(
    f"Flood Area: {flood_percent:.2f}%"
)

plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.imshow(vv, cmap="gray")
plt.title("VV")

plt.subplot(1,2,2)
plt.imshow(mask, cmap="jet")
plt.colorbar()
plt.title("Flood Prediction")

plt.show()

print(
    "Pixels > 0.01:",
    np.mean(mask > 0.01) * 100
)

print(
    "Pixels > 0.05:",
    np.mean(mask > 0.05) * 100
)

print(
    "Pixels > 0.10:",
    np.mean(mask > 0.10) * 100
)

flood_percent = binary.sum() / binary.size * 100
print(f"Flood Area: {flood_percent:.2f}%")