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
    """
    Ensure all images referenced in the database are available in the static directory.
    Copies images from their original location to static/images if they don't exist there.
    """
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

# Initialize ResNet50 model for feature extraction
base_model = ResNet50(weights='imagenet',include_top=False,input_shape=(224,224,3))
base_model.trainable=False

model = tf.keras.Sequential([
    base_model,
    GlobalMaxPooling2D()
])

# Initialize FastAPI application
app = FastAPI(title="Image-Based Recommender System")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Load pre-computed features and filenames
try:
    feature_list = pickle.load(open('artifacts/embeddings.pkl', 'rb'))
    filenames = pickle.load(open('artifacts/filenames.pkl', 'rb'))
    ensure_images_in_static()  # Ensure images are in static directory
except:
    feature_list = []
    filenames = []

@app.get("/")
def main(request: Request):
    """
    Render the home page with the image upload interface.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    """
    Handle image upload and return similar image recommendations.
    
    Args:
        file (UploadFile): The uploaded image file
        
    Returns:
        dict: Dictionary containing list of similar image filenames
    """
    # Save uploaded file temporarily
    file_location = f"temp_{file.filename}"
    with open(file_location,"wb+") as file_object:
        shutil.copyfileobj(file.file,file_object)
    
    # Extract features from uploaded image
    features = extract_features(file_location)
    
    # Calculate similarity scores
    distances = np.dot(np.array(feature_list),features)
    
    # Get indices of most similar images
    similar_indices = np.argsort(distances)[-6:][::-1]
    
    # Get filenames of similar images
    similar_images = [os.path.basename(filenames[i]) for i in similar_indices]
    
    # Clean up temporary file
    os.remove(file_location)
    
    return {"similar_images": similar_images}

def load_features():
    """
    Load pre-computed features and filenames from the database.
    This function is called when the application starts.
    """
    global feature_list, filenames
    
    # Load features and filenames 
    with open('artifacts/embeddings.pkl', 'rb') as f:
        feature_list = pickle.load(f)
    with open('artifacts/filenames.pkl', 'rb') as f:
        filenames = pickle.load(f)

# Load features when the application starts
load_features()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)