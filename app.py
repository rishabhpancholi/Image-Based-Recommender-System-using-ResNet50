from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import shutil
from pathlib import Path
import numpy as np
import pickle
import uvicorn
import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50
from helper import extract_features

def ensure_images_in_static():
    static_images_dir = Path("static/images")
    static_images_dir.mkdir(parents=True, exist_ok=True)
    
    # Get the list of images from the embeddings
    try:
        filenames = pickle.load(open('artifacts/filenames.pkl', 'rb'))
        for filename in filenames:
            src_path = Path(filename)
            if src_path.exists():
                dst_path = static_images_dir / src_path.name
                if not dst_path.exists():
                    shutil.copy2(src_path, dst_path)
    except Exception as e:
        print(f"Error copying images: {e}")

base_model = ResNet50(weights='imagenet',include_top=False,input_shape=(224,224,3))
base_model.trainable=False

model = tf.keras.Sequential([
    base_model,
    GlobalMaxPooling2D()
])

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

try:
    feature_list = pickle.load(open('artifacts/embeddings.pkl', 'rb'))
    filenames = pickle.load(open('artifacts/filenames.pkl', 'rb'))
    ensure_images_in_static()  # Ensure images are in static directory
except:
    feature_list = []
    filenames = []

@app.get("/")
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
  file_location = f"temp_{file.filename}"
  with open(file_location,"wb+") as file_object:
     shutil.copyfileobj(file.file,file_object)
  features = extract_features(file_location)
  distances = np.dot(np.array(feature_list),features)
  similar_indices = np.argsort(distances)[-6:][::-1]
  similar_images = [os.path.basename(filenames[i]) for i in similar_indices]
  os.remove(file_location)
  return {"similar_images": similar_images}

if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8000, reload=True)