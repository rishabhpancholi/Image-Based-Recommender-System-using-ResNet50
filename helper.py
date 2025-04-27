import tensorflow as tf
import numpy as np
from numpy.linalg import norm
import os
import pickle
from tqdm import tqdm
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50,preprocess_input

# Initialize model once
base_model = ResNet50(weights='imagenet',include_top=False,input_shape=(224,224,3))
base_model.trainable=False

model = tf.keras.Sequential([
    base_model,
    GlobalMaxPooling2D()
])

def extract_features(img_path):
    img = image.load_img(img_path,target_size=(224,224))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array,axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result/norm(result)
    return normalized_result







