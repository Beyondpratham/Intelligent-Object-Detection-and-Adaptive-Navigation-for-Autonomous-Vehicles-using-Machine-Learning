# -*- coding: utf-8 -*-
"""ml endsem_code

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EskR1Q3hqpXVbIHNaa87VdwrhgExtO4z
"""

import numpy as np
import tensorflow
import keras
import cv2
import imutils

from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt

from keras.applications import VGG16
from keras.utils import to_categorical

from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPool2D, Flatten, Dense, InputLayer, BatchNormalization, Dropout

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tensorflow.keras.models import load_dataset

from google.colab import files
data_to_load = files.upload()

def CNN_model_function():
  imagegen = ImageDataGenerator(rotation_range=20,
                              width_shift_range=0.1,
                              height_shift_range=0.1,
                              zoom_range=0.1,
                              horizontal_flip=True)

  train = imagegen.flow_from_directory("path", class_mode = "categorical", shuffle = False, batch_size = 128, target_size = (224, 224))
  val = imagegen.flow_from_directory("path", class_mode = "categorical", shuffle = False, batch_size = 128, target_size = (224, 224))

  pretrained_model = VGG16(include_top = False, weights = "imagenet")
  pretrained_model.summary()

  vgg_features_train = pretrained_model.predict(train)
  vgg_features_val = pretrained_model.predict(val)

  train_target = to_categorical(train.labels)
  val_target = to_categorical(val.labels)

  cnn_model = Sequential()
  cnn_model.add(Flatten(input_shape=(7,7,512)))
  cnn_model.add(Dense(100, activation='relu'))
  cnn_model.add(Dropout(0.5))
  cnn_model.add(BatchNormalization())
  cnn_model.add(Dense(10, activation='softmax'))

  cnn_model.compile(optimizer='adam', metrics=['accuracy'], loss='categorical_crossentropy')

  cnn_model.summary()

  cnn_model.fit(vgg_features_train, train_target, epochs=50, batch_size=128, validation_data=(vgg_features_val, val_target))

  def classify_object(object_image):
    class_probabilities = cnn_model.predict(np.expand_dims(object_image, axis = 0))

    predicted_class = np.argmax(class_probabilities)
    return predicted_class

  def divide_into_segments(image):
    height, width, _ = image.shape
    #segment_height = height // 3
    segment_width = width // 3

    segments = [image[:, i * segment_width: (i + 1) * segment_width] for i in range(3)]
    #segments_h = [image[i * segment_height: (i + 1) * segment_height, :] for i in range(3)]
    return segments

  def calculate_loss(segment_objects):
    class_weights = {
        'human': 0.15,
        'vehicle': 0.1,
        'animal': 0.05,
        'pothole': 0.02,
        'nothing': 0.0
    }

    segment_loss = 0
    for class_name, object_image in segment_objects.items():
        loss_weight = class_weights.get(class_name, 0.0)
        if loss_weight > 0:
            predicted_class = classify_object(object_image)
            segment_loss += predicted_class * loss_weight

    return segment_loss

  def detect_objects(segment):
    bounding_boxes = cnn_model.predict(np.expand_dims(segment, axis=0))[0]

    objects = {}
    for box in bounding_boxes:
        x, y, w, h = box
        object_image = segment[y:y+h, x:x+w]
        object_class = classify_object(object_image)
        objects[object_class] = object_image

    return objects

  def predict_direction(image):
    segments = divide_into_segments(image)

    segment_objects = {}
    for i, segment in enumerate(segments):
      objects = detect_objects(segment)
      segment_name = f'segment_{i}'
      segment_objects[segment_name] = objects

    segment_losses = {segment_name: calculate_loss(objects) for segment_name, objects in segment_objects.items()}

    min_loss_segment = min(segment_losses, key=segment_losses.get)

    if min_loss_segment == 'segment_0':
        return "Go Left"
    elif min_loss_segment == 'segment_1':
        return "Go Straight"
    elif min_loss_segment == 'segment_2':
        return "Go Right"
    else:
        return "No Decision"

  for filename in os.listdir(image_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(image_dir, filename)

        image = cv2.imread(image_path)
        image = preprocess_image(image)

        prediction = direction_model.predict(np.expand_dims(image, axis=0))
        predicted_class = np.argmax(prediction)


  x, y = load_dataset("path")

  x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

  y_pred = predict_direction(x_test)

  accuracy = accuracy_score(y_test, y_pred)
  precision = precision_score(y_test, y_pred, average='weighted')
  recall = recall_score(y_test, y_pred, average='weighted')
  f1 = f1_score(y_test, y_pred, average='weighted')

  print(f"Accuracy: {accuracy:.4f}")
  print(f"Precision: {precision:.4f}")
  print(f"Recall: {recall:.4f}")
  print(f"F1 Score: {f1:.4f}")



import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Generate random data for illustration purposes (replace with your actual data)
np.random.seed(42)
num_models = 5
accuracy_data = np.random.uniform(0.7, 0.9, size=(100, num_models))
f1_score_data = np.random.uniform(0.6, 0.8, size=(100, num_models))

# Flatten the data for box plot
flat_accuracy = accuracy_data.flatten()
flat_f1_score = f1_score_data.flatten()

# Create a box plot using Seaborn
plt.figure(figsize=(12, 6))

# Box plot for Accuracy
plt.subplot(1, 2, 1)
sns.boxplot(data=flat_accuracy, width=0.5)
plt.title('Box Plot for Accuracy')

# Box plot for F1 Score
plt.subplot(1, 2, 2)
sns.boxplot(data=flat_f1_score, width=0.5)
plt.title('Box Plot for F1 Score')

# Show the box plots
plt.tight_layout()
plt.show()