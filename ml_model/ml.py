import numpy as np 
import pandas as pd 
import os, gc, pathlib
from sklearn.metrics import confusion_matrix
from fastai import *
from fastai.vision import *
from fastai.vision.models import *
import torchvision.models as models
from pathlib import Path

print(os.listdir("C:/Abhijay/PennApps/RealBrainTumorData"))

# Set up the directory for the data
DATA_DIR = Path('C:/Abhijay/PennApps/RealBrainTumorData')
if not DATA_DIR.exists():
    print(f"Path {DATA_DIR} does not exist!")
else:
    print(f"Directory contents: {os.listdir(DATA_DIR)}")

train_path = DATA_DIR / 'brain_tumor_dataset'
valid_path = DATA_DIR 

if not train_path.exists() or not valid_path.exists():
    print(f"Check your data splits. One of {train_path} or {valid_path} doesn't exist.")
else:
    print(f"Train and valid paths are set correctly.")

# Importing necessary FastAI utilities
from fastai.vision.all import *

# Data augmentation and normalization
batch_tfms = [
    *aug_transforms(
        size=224, 
        mult=1.0,
        do_flip=True,
        flip_vert=False,
        max_rotate=10.0,
        min_zoom=1.0,
        max_zoom=1.0,
        max_lighting=0.2,
        max_warp=0.2,
        p_affine=0.75,
        p_lighting=0.75,
        mode='bilinear',
        pad_mode='reflection',
        align_corners=True,
        batch=False,
        min_scale=1.1,
    ), 
    Normalize.from_stats(*imagenet_stats)
]

# DataBlock setup for loading the data
dls = DataBlock(
    blocks=(ImageBlock, CategoryBlock),
    get_items=get_image_files,
    splitter=GrandparentSplitter(train_name='train', valid_name='valid'),
    get_y=parent_label,
    item_tfms=Resize(224),
    batch_tfms=batch_tfms
).dataloaders(DATA_DIR, bs=16)

# Verify if the data loads correctly
try:
    dls.show_batch(figsize=(7, 6))
    print("Batch displayed successfully.")
except Exception as e:
    print(f"Error showing batch: {e}")

print("We are right here")

import timm

# Function to set up the learner with error handling and debugging
def get_learner(model_name='xresnet50', patience=3, bs=16):
    # Create the model based on the number of classes in the data coming from the dataloaders (dls.c)
    try:
        the_model = timm.create_model(model_name, pretrained=True, num_classes=dls.c)
    except Exception as e:
        print(f"Error creating model {model_name}: {e}")
        return None

    # Wrap the model with DataParallel for multi-GPU training
    if torch.cuda.device_count() > 1:
        the_model = torch.nn.DataParallel(the_model)
        print(f"Using {torch.cuda.device_count()} GPUs.")

    # Create the Learner
    learner = Learner(
        dls,
        the_model,
        metrics=accuracy,
        cbs=[
            EarlyStoppingCallback(monitor='valid_loss', patience=patience),
            SaveModelCallback(monitor='valid_loss', fname=f'{model_name}_best_model')
        ]
    )
    
    learner.dls.bs = bs
    return learner

# Set the parameters for learning
PERFORM_EXPORT = True
model_name = 'convnext_tiny'
learner = get_learner(model_name=model_name, patience=8)

# Learning rate finder with fallbacks in case no learning rate is found
if learner is not None:
    try:
        lr_slide, lr_valley, lr_min, lr_steep = learner.lr_find(suggest_funcs=(slide, valley, minimum, steep))
        print(f"Learning rates found:\nSlide: {lr_slide}\nValley: {lr_valley}\nMin: {lr_min}\nSteep: {lr_steep}")
        
        # Default to a fallback learning rate if lr_valley is None
        if lr_valley is None:
            lr_valley = 1e-3  # Set default learning rate
            print(f"Using fallback learning rate: {lr_valley}")
    except Exception as e:
        print(f"Error finding learning rate: {e}")
        lr_valley = 1e-3  # Fallback to default learning rate

    # Freeze the learner and fit the model
    learner.freeze()
    learner.fit_one_cycle(20, lr_valley)
    
    # Plot losses
    learner.recorder.plot_loss()
    learner.recorder.plot_loss()

    # Model interpretation
    try:
        interp = ClassificationInterpretation.from_learner(learner)
        interp.plot_top_losses(10, figsize=(10, 10))
        interp.plot_confusion_matrix(figsize=(8, 8), dpi=60)

        # Top losses
        losses, idxs = interp.top_losses()
        top_confused_files = [dls.valid_ds.items[i] for i in idxs]
        print(f"Top confused files: {top_confused_files}")
    except Exception as e:
        print(f"Error during interpretation: {e}")

    # Test set evaluation
    test_files = get_image_files(DATA_DIR/'test')
    test_dl = dls.test_dl(test_files)
    
    # Load the best model and make predictions
    try:
        learner.load(f'{model_name}_best_model')
        preds, _ = learner.get_preds(dl=test_dl)

        # Get the actual labels
        test_labels = tensor([dls.vocab.o2i[parent_label(f)] for f in test_files])

        # Calculate accuracy
        predicted_labels = preds.argmax(dim=1)
        accuracy = (predicted_labels == test_labels).float().mean()
        print(f"Test set accuracy: {accuracy:.4f}")

        # Get incorrect predictions
        incorrect_predictions = (predicted_labels != test_labels)
        incorrect_files = [f for i, f in enumerate(test_files) if incorrect_predictions[i]]
        print(f"Incorrectly classified files: {incorrect_files}")
    except Exception as e:
        print(f"Error loading the best model or predicting: {e}")

    # Export the model
    if PERFORM_EXPORT:
        try:
            learner.export(f'{model_name}.pkl')
            print(f"Model exported to {model_name}.pkl")
        except Exception as e:
            print(f"Error exporting model: {e}")
else:
    print("Learner could not be created.")
