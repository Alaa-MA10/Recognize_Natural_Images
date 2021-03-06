# -*- coding: utf-8 -*-
"""Inception ResNet V2 - Pre-Train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SlSSgZUKFzSWxwGV4Df_Ks29PMRLvzVo

# Imports
"""

!pip install tensorflow==1.15.3
!pip install q Keras==2.2.5

import warnings
warnings.filterwarnings("ignore")

from google.colab import drive
from random import shuffle
from tqdm import tqdm
from sklearn.model_selection import train_test_split

import tensorflow.contrib.keras as keras
from keras.models import Model, load_model
from keras.callbacks import TensorBoard,ModelCheckpoint
from keras.utils import to_categorical
from keras.layers import Input, GlobalMaxPooling2D, Dense, Dropout
from keras.optimizers import Adam

from datetime import datetime
import cv2
import tensorflow as tf

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv 

tf.logging.set_verbosity(tf.logging.ERROR)

"""# Configurations

## Mount Drive
"""

drive.mount('/content/drive')

"""## Constants"""

IMG_SIZE = 150
PROJECT_DIR = '/content/drive/MyDrive/Neural_Project/'
os.chdir(PROJECT_DIR)

DATA_PATH = os.path.join("Data (npy)")
date_time = datetime.now().strftime("(%Y/%m/%d, %H:%M)")

MODEL_NAME = "Inception-ResNet_V2"
EPOCHS_NUM = 10
log_dir = f"logs/{MODEL_NAME}({EPOCHS_NUM})-{date_time}"

train_image_path = os.path.join(DATA_PATH, 'train_image - (150-RGB).npy')
test_image_path = os.path.join(DATA_PATH, 'test_image - (150-RGB).npy')

MODEL_FOLDER = 'Inception_ResNet_V2'
#MODEL_PATH = os.path.join('Models', f'{MODEL_FOLDER}',f'{MODEL_NAME}_{date_time}_({EPOCHS_NUM}_epoch).model')

"""# Prepare Data

## Create Train Data
"""

def create_train_data():
  train_image = []

  for c in Classes['Image']:
    path = os.path.join('Scenes_training_set',c)   # path to building,forest,... folders , c = building,forest,..
    class_label = list(Classes['Image']).index(c)     # class_label = 0, 1, 2, 3, 4

    for img in tqdm(os.listdir(path)):
      img_data = cv2.imread(os.path.join(path,img), cv2.IMREAD_COLOR)
      img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)                  # Make it RGB 
      img_data = cv2.resize(img_data, (IMG_SIZE, IMG_SIZE))   # resize image

      train_image.append([np.array(img_data),class_label])

  shuffle(train_image)
  np.save(train_image_path, train_image)

  return train_image

"""## Create Test Data"""

def create_test_data():
  test_image = []
  path = os.path.join('Scenes_testing_set')   # path to testing folder

  for img in tqdm(os.listdir(path)):
    img_data = cv2.imread(os.path.join(path,img), cv2.IMREAD_COLOR)
    img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)                  # Make it RGB 
    img_data = cv2.resize(img_data, (IMG_SIZE, IMG_SIZE))   # resize image
    
    test_image.append([np.array(img_data), img])

  np.save(test_image_path, test_image)

  return test_image

"""# MAIN

Reading CSV file
"""

Classes = pd.read_csv('names.csv')

"""## Pre-Processing

### Train dataset created OR not
"""

# If Train dataset created or not
if (os.path.exists(train_image_path)):
  train_image = np.load(train_image_path, allow_pickle=True)
  print('Train dataset exist')
else:
  train_image = create_train_data()

"""### Test dataset created OR not"""

# If Test dataset created or not
if (os.path.exists(test_image_path)):
  test_image = np.load(test_image_path, allow_pickle=True)
  print('Test dataset exist')
else:
  test_image = create_test_data()

"""### Prepare X,Y"""

X = np.array([i[0] for i in train_image]).reshape(-1, IMG_SIZE, IMG_SIZE, 3)
Y = [i[1] for i in train_image]

# Normalization X 
X = X.astype('float32') / 255

# One Hot Encode Y
Y = to_categorical(Y)

# split train and validation
X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.3, shuffle=True)

"""## Train

### Load Pre-train Model

1. Load Pretrained Model with (imagenet) Pretrained weights
"""

from inception_resnet_v2 import InceptionResNetV2

### Transfer learning and fine-tuning

# 1. Create the base model from the pre-trained weights
base_model = InceptionResNetV2(include_top=False, input_tensor=Input(X.shape[1:]), weights='imagenet')

"""2. freeze all InceptionResNetV2 layers"""

#freeze all convolutional InceptionResNetV2 layers

for layer in base_model.layers:
  layer.trainable = False
  
print(len(base_model.layers))

"""### Define the Model"""

# Add new Layers on top

last_layer = base_model.output
x = GlobalMaxPooling2D()(last_layer)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
x_output = Dense(6, activation='softmax')(x)

model = Model(inputs= base_model.input, outputs= x_output)

model.summary()

"""### Training"""

# Compile the model 
model.compile(optimizer=Adam(lr=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

# checkpoint for pre-train model
pretrain_checkpoint_path = os.path.join('Models', f'{MODEL_FOLDER}','Pre-train_Inception-ResNetV2_epoch:{epoch:02d}_acc:{val_acc:.4f}.h5')
pretrain_checkpoint = ModelCheckpoint(pretrain_checkpoint_path, monitor= 'val_acc', mode= 'max', save_best_only= True, verbose=1)

# Train the model
model.fit(X_train, Y_train, batch_size=128, epochs=10, validation_data=(X_val, Y_val), callbacks=[pretrain_checkpoint])