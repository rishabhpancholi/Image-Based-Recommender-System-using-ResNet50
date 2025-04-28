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

app = FastAPI(title="Image-Based Recommender System")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

try:
    feature_list = pickle.load(open('artifacts/embeddings.pkl', 'rb'))
    filenames = pickle.load(open('artifacts/filenames.pkl', 'rb'))
    ensure_images_in_static()  # Ensure images are in static directory
except:
    feature_list = []
    filenames = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the home page with the image upload interface.
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        HTMLResponse: Rendered home page template
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_image(request: Request, file: UploadFile = File(...)):
    """
    Handle image upload and return similar image recommendations.
    
    Args:
        request (Request): FastAPI request object
        file (UploadFile): Uploaded image file
        
    Returns:
        TemplateResponse: Rendered results page with recommendations
    """
    # Save the uploaded file temporarily
    file_path = f"static/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Extract features from the uploaded image
    query_features = extract_features(file_path)
    
    # Calculate similarity scores with all images in the database
    similarity_scores = []
    for features in feature_list:
        # Calculate cosine similarity
        similarity = np.dot(query_features, features)
        similarity_scores.append(similarity)
    
    # Get indices of top 5 most similar images
    top_indices = np.argsort(similarity_scores)[-5:][::-1]
    
    # Get filenames of similar images
    similar_images = [filenames[i] for i in top_indices]
    
    # Return the results page with recommendations
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "query_image": file.filename,
            "similar_images": similar_images
        }
    )

def load_features():
    """
    Load pre-computed features and filenames from the database.
    This function is called when the application starts.
    """
    global feature_list, filenames
    
    # Load features and filenames from numpy files
    feature_list = np.load('artifacts/features.npy')
    filenames = np.load('artifacts/filenames.npy')

# Load features when the application starts
load_features()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)