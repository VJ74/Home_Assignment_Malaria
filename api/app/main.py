import io
import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import Response, FileResponse
from typing import List

from enum import Enum


class FileType(Enum):
   image: str = 'IMAGE'
   default: str = 'DEFAULT'

BASE_PATH = '/mnt/data'
IMAGE_PATH = os.path.join(BASE_PATH, FileType.image.value)
DEFAULT_PATH = os.path.join(BASE_PATH, FileType.default.value)
os.makedirs(IMAGE_PATH, exist_ok=True)
os.makedirs(DEFAULT_PATH, exist_ok=True)


app = FastAPI()

@app.get("/")
def root():
    return {"message":"Hello World-I'm not infected"}

@app.get("/images", response_model=List[str])
def getAllImages():
    return os.listdir(IMAGE_PATH)

@app.get("/image/{filename}")
def getImageById(filename: str):
    try:
       return FileResponse(filename)
    except Exception as e:
        return HTTPException(500, f'Something went wrong while trying to return file {filename}')
    

@app.post("/upload")
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
    return "v1"