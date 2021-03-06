# -*- coding: utf-8 -*-
"""Image_classification_CNN_Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NBhWFZHNJ4rBcCTqbHSi716nVDFg3oom

# Imports
"""

from google.colab import drive
from random import shuffle
from tqdm import tqdm
from sklearn.model_selection import train_test_split

from tensorflow import keras
from keras.models import Sequential, load_model
from keras.utils import to_categorical
from keras.layers import Conv2D, BatchNormalization, Activation, MaxPooling2D, Dense, Dropout, Flatten
from keras.callbacks import TensorBoard, ModelCheckpoint
from datetime import datetime

import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os

"""# Configurations

## Mount Drive
"""

drive.mount('/content/drive')

"""## Constants"""

IMG_SIZE = 90
PROJECT_DIR = '/content/drive/MyDrive/Neural_Project/'
os.chdir(PROJECT_DIR)

date_time = datetime.now().strftime("(%Y/%m/%d, %H:%M)")

MODEL_NAME ="64x13-CNN-(Batch & dropout)"
EPOCHS_NUM = 50
log_dir = f"logs/{MODEL_NAME}({EPOCHS_NUM})-{date_time}"

DATA_PATH = os.path.join("Data (npy)")
train_image_data = os.path.join(DATA_PATH, f'train_image - ({IMG_SIZE}-RGB).npy')
test_image_data = os.path.join(DATA_PATH, f'test_image - ({IMG_SIZE}-RGB).npy')

MODEL_FOLDER = 'CNN'
MODEL_PATH = os.path.join('Models', f'{MODEL_FOLDER}')#,f'{MODEL_NAME}_{date_time}_({EPOCHS_NUM}_epoch).model')

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
      #img_data = cv2.imread(os.path.join(path,img), cv2.IMREAD_GRAYSCALE)  # Read Image and convert it to GRAY
      img_data = cv2.resize(img_data, (IMG_SIZE, IMG_SIZE))   # resize image

      train_image.append([np.array(img_data),class_label])

  shuffle(train_image)
  np.save(train_image_data, train_image)

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

  np.save(test_image_data, test_image)

  return test_image

"""# Models

## 64x13-CNN Model
"""

def create_cnn_Model(X, num_classes):
  model = Sequential()

  #Conv 1
  model.add(Conv2D(64, kernel_size=(3,3), input_shape=X.shape[1:], padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #Conv 2
  model.add(Conv2D(64, kernel_size=(3,3), padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #POOL 1
  model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
  model.add(Dropout(0.2))

  #Conv 3
  model.add(Conv2D(128, kernel_size=(3,3), padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #Conv 4
  model.add(Conv2D(128, kernel_size=(3,3), padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #POOL 2
  model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
  model.add(Dropout(0.3))

  #Conv 5
  model.add(Conv2D(256, kernel_size=(3,3), padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #Conv 6
  model.add(Conv2D(256, kernel_size=(3,3), padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #POOL 3
  model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
  model.add(Dropout(0.3))


  #Conv 7
  model.add(Conv2D(256, kernel_size=(3,3), padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))
  
  #Conv 8
  model.add(Conv2D(256, kernel_size=(3,3), padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #POOL 4
  model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
  model.add(Dropout(0.4))

  #Conv 9
  model.add(Conv2D(512, kernel_size=(3,3),  padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #Conv 10
  model.add(Conv2D(512, kernel_size=(3,3),  padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #POOL 5
  model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
  model.add(Dropout(0.4))

  #Conv 11
  model.add(Conv2D(256, kernel_size=(3,3),  padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #Conv 12
  model.add(Conv2D(256, kernel_size=(3,3), padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #POOL 6
  model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
  model.add(Dropout(0.4))

  #Conv 13
  model.add(Conv2D(512, kernel_size=(3,3), padding='same'))
  model.add(BatchNormalization())
  model.add(Activation('relu'))

  #POOL 7
  model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
  model.add(Dropout(0.4))

  model.add(Flatten())                      # 'flatten' layer that turns the inputs into a vector
  model.add(Dense(4096, activation='relu'))
  model.add(Dropout(0.5))                   #drops 50% of the existing connections
  model.add(Dense(4096, activation='relu'))
  
  # A 'dense' layer that takes that vector and generates probabilities for 6 target labels, using a Softmax 
  model.add(Dense(num_classes, activation='softmax'))  

  return model

"""### Train CNN model"""

def train_CNN_model(X_train,Y_train, X_val, Y_val, model_path):
  tensorboard = TensorBoard(log_dir, histogram_freq=1)

  checkpoint_filepath = os.path.join(model_path,'64x13-CNN-(Batch & dropout)_epoch:{epoch:02d}_acc:{val_accuracy:.4f}.h5')
  checkpoint = ModelCheckpoint(checkpoint_filepath, monitor= 'val_accuracy', mode= 'max', save_best_only= True)

  CNN_model = create_cnn_Model(X, num_classes= len(Y_train[0]))
  CNN_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
  CNN_model.fit(X_train, Y_train, batch_size=128, epochs=EPOCHS_NUM,
                validation_data=(X_val, Y_val), callbacks=[checkpoint, tensorboard]) 
  return CNN_model

"""# MAIN

Reading CSV file
"""

Classes = pd.read_csv('names.csv')

"""## Pre-Processing

### Train dataset created OR not
"""

# If Train dataset created or not
if (os.path.exists(train_image_data)):
  train_image = np.load(train_image_data, allow_pickle=True)
  print('Train dataset exist')
else:
  train_image = create_train_data()

"""### Test dataset created OR not"""

# If Test dataset created or not
if (os.path.exists(test_image_data)):
  test_image = np.load(test_image_data, allow_pickle=True)
  print('Test dataset exist')
else:
  test_image = create_test_data()

"""### Prepare X,Y"""

X = np.array([i[0] for i in train_image]).reshape(-1, IMG_SIZE, IMG_SIZE, 3)
Y = [i[1] for i in train_image]

# One Hot Encode Y
Y = to_categorical(Y)

# Normalization X 
X = X.astype('float32') / 255

# split train and validation
X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.3, shuffle=True)

"""## Train"""

CNN_model = train_CNN_model(X_train,Y_train, X_val, Y_val, MODEL_PATH)

"""## Set X_test and predict"""

'''
print(test_image.shape)
X_test = np.array([i[0] for i in test_image]).reshape(-1, IMG_SIZE, IMG_SIZE, 3)
X_test_name = [i[1] for i in test_image]
X_test = X_test.astype('float32') / 255

prediction = CNN_model.predict(X_test)
print(len(prediction))

max_pred_id = np.argmax(prediction, axis = 1)
print(len(max_pred_id))

print(list(Classes['Image'])[max_pred_id[73]])
plt.imshow(X_test[73,:,:], cmap='gray')
print(X_test_name[331])
'''

"""## Write result CSV """

'''
X_test_name = pd.Series(X_test_name, name='Image')
max_pred_id = pd.Series(max_pred_id, name='Label')
result_csv = pd.concat([X_test_name, max_pred_id], axis = 1)
result_csv.to_csv('try_submit_.88.csv', index = False)
'''