# from fastapi import FastAPI
# # from inference.predict import predict_flood
# import matplotlib.pyplot as plt
# import uuid

# app = FastAPI()

# @app.get("/")
# def home():

#     return {
#         "message": "Flood Prediction API Running"
#     }

# @app.post("/predict")
# def predict():

#     pred = predict_flood(

#         "inference/sample_data/vv_vh.tif",

#         "inference/sample_data/dem.tif",

#         "inference/sample_data/hydro.tif"
#     )

#     output_path = f"inference/outputs/{uuid.uuid4()}.png"

#     plt.imsave(
#         output_path,
#         pred,
#         cmap='gray'
#     )

#     return {

#         "status": "success",

#         "output_mask": output_path
#     }