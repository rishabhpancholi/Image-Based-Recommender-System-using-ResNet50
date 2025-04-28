# Import required libraries
import tensorflow as tf
import numpy as np
from PIL import Image
import os
from tqdm import tqdm

# Initialize ResNet50 model with pre-trained weights from ImageNet
# We use include_top=False to get feature vectors instead of classification predictions
model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_features(img_path):
    """
    Extract features from an image using ResNet50 model.
    
    Args:
        img_path (str): Path to the image file
        
    Returns:
        numpy.ndarray: Normalized feature vector of shape (2048,)
    """
    # Load and preprocess the image
    img = Image.open(img_path).convert('RGB')
    img = img.resize((224, 224))  # ResNet50 expects 224x224 images
    img_array = np.array(img)
    img_array = tf.keras.applications.resnet50.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    
    # Extract features using the model
    features = model.predict(img_array, verbose=0)
    
    # Normalize the feature vector
    features = features / np.linalg.norm(features)
    
    return features.flatten()  # Return flattened feature vector







