# -*- coding: utf-8 -*-
from __future__ import division, print_function
from keras.callbacks import ModelCheckpoint
from keras.layers import Dense, Dropout, Input
from keras.models import Model, load_model
from keras.utils import np_utils
import numpy as np
import os

import fttlutils

DATA_DIR = "../data/files"
MODEL_DIR = os.path.join(DATA_DIR, "models")
NUM_EPOCHS = 50
BATCH_SIZE = 32

# data
X = np.loadtxt(os.path.join(DATA_DIR, "images-X.txt"), delimiter=",")
y = np.loadtxt(os.path.join(DATA_DIR, "images-y.txt"), delimiter=",", 
               dtype=np.int)
Y = np_utils.to_categorical(y, nb_classes=5)               

np.random.seed(42)

Xtrain, Xtest, Ytrain, Ytest = fttlutils.train_test_split(
    X, Y, test_size=0.3, random_state=42)
print(Xtrain.shape, Xtest.shape, Ytrain.shape, Ytest.shape)

# model
# input: (None, 25088)
imgvecs = Input(shape=(Xtrain.shape[1],), dtype="float32")
# hidden layer: (None, 256)
fc1 = Dense(256,
            activation="relu",
            init="he_uniform",
            name="dl1fc1")(imgvecs)
fc1 = Dropout(0.5)(fc1)
# output layer: (None, 5)
predictions = Dense(5, activation="softmax", name="dl1preds")(fc1)

model = Model(input=[imgvecs], output=[predictions])

model.compile(optimizer="adadelta", loss="categorical_crossentropy",
              metrics=["accuracy"])

best_model = os.path.join(MODEL_DIR, "tl-dl1-model-best.h5")
checkpoint = ModelCheckpoint(filepath=best_model, verbose=1, 
                             save_best_only=True)
history = model.fit([Xtrain], [Ytrain], nb_epoch=NUM_EPOCHS, 
                    batch_size=BATCH_SIZE, validation_split=0.1, 
                    callbacks=[checkpoint])
fttlutils.plot_loss(history)

# evaluate final model
Ytest_ = model.predict(Xtest)
ytest = np_utils.categorical_probas_to_classes(Ytest)
ytest_ = np_utils.categorical_probas_to_classes(Ytest_)
fttlutils.print_stats(ytest, ytest_, "Final Model (DL#1)")
model.save(os.path.join(MODEL_DIR, "tl-dl1-model-final.h5"))

# load best model and evaluate
model = load_model(os.path.join(MODEL_DIR, "tl-dl1-model-best.h5"))
model.compile(optimizer="adadelta", loss="categorical_crossentropy",
              metrics=["accuracy"])
Ytest_ = model.predict(Xtest)
ytest = np_utils.categorical_probas_to_classes(Ytest)
ytest_ = np_utils.categorical_probas_to_classes(Ytest_)
fttlutils.print_stats(ytest, ytest_, "Best Model (DL#1)")
