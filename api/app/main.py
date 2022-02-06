import io
import os
from tabnanny import filename_only
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from typing import List
import json

from enum import Enum

import numpy as np
from skimage.io import imread
from skimage import transform
import tensorflow as tf


class FileType(Enum):
   image: str = 'IMAGE'
   default: str = 'DEFAULT'

BASE_PATH = '/mnt/data'
IMAGE_PATH = os.path.join(BASE_PATH, FileType.image.value)
DEFAULT_PATH = os.path.join(BASE_PATH, FileType.default.value)
os.makedirs(IMAGE_PATH, exist_ok=True)
os.makedirs(DEFAULT_PATH, exist_ok=True)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# load model

loaded_model=tf.keras.models.load_model('./best_model.h5')

# prediction function

def predict_Malaria_infection(file):
    im = imread(file)
    im = transform.resize(im,(50,50),mode='constant',anti_aliasing=True)
    img_array=np.array(im)
    img_batch=np.expand_dims(img_array, axis=0)
    predictions=loaded_model.predict_on_batch(img_batch).flatten()
    predictions=tf.nn.sigmoid(predictions)
    predictions=tf.where(predictions < 0.5, 0, 1)
    labels = ['The person is not infected with Malaria', 'The person is infected with Malaria']
    return {'Prediction':'{}'.format(labels[predictions.numpy()[0]])}

@app.get("/")
def root():
    return {"message":"Hello World - I'm not infected"}

@app.get("/images", response_model=List[str])
def getAllImages():
    return os.listdir(IMAGE_PATH)

@app.get("/image/{filename}", summary='Predict if someone has a malaria infection')
def getImageById(filename: str):
    try:
       return predict_Malaria_infection(filename)
    except Exception as e:
        return HTTPException(500, f'Something went wrong while trying to get file {filename}')

@app.post("/upload", summary='Upload malaria images to make prediction')
def uploadFile(file: UploadFile = File(...), type: FileType = FileType.default):
    print(f"Upload type: {type}")
    print(f"Upload type: {type.value}")
    fileLocation = os.path.join(BASE_PATH, type.value, file.filename)
    try:
        open(fileLocation, 'wb').write(file.file.read())
    except Exception as e:
        print(e)
        return HTTPException(500, f'Something went wrong while trying to upload file {file.filename}')

    return Response(f'Uploaded file to {fileLocation}', 200)


@app.get('/app/info', summary='Return version number')
def appInfo():
    """
    Return version number
    """
    return "v2"