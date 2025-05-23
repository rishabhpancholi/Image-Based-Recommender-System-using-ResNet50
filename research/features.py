import tensorflow as tf
import numpy as np
from numpy.linalg import norm
import os
import pickle
from tqdm import tqdm
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50,preprocess_input

model = ResNet50(weights='imagenet',include_top=False,input_shape=(224,224,3))
model.trainable=False

model = tf.keras.Sequential([
    model,
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

filenames = []
data_dir = os.path.join( 'static', 'images')
for file in os.listdir(data_dir):
    filenames.append(os.path.join(data_dir, file))

feature_list = []

for file in tqdm(filenames):
    feature_list.append(extract_features(file))

pickle.dump(feature_list,open('embeddings.pkl','wb'))
pickle.dump(filenames,open('filenames.pkl','wb'))