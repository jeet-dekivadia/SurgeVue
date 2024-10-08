import os
import cv2
import zipfile
from fastai.vision.all import *
import numpy as np
import glob
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid

import warnings
warnings.filterwarnings("ignore")

# parent_dir = Path("C:\Abhijay\PennApps\RealBrainTumorData")
# parent_dir.ls()

import os
import shutil
from pathlib import Path
import random

# Define the source and destination paths
source_path = Path(r'C:\adity\Documents\PennApps\RealBrainTumorData')
destination_path = Path('./processed')

# Delete the directories first if exist and then create them
shutil.rmtree(destination_path, ignore_errors=True)

# Create the processed directory and subdirectories
(destination_path / 'train' / 'yes').mkdir(parents=True, exist_ok=True)
(destination_path / 'train' / 'no').mkdir(parents=True, exist_ok=True)
(destination_path / 'valid' / 'yes').mkdir(parents=True, exist_ok=True)
(destination_path / 'valid' / 'no').mkdir(parents=True, exist_ok=True)
(destination_path / 'test' / 'yes').mkdir(parents=True, exist_ok=True)
(destination_path / 'test' / 'no').mkdir(parents=True, exist_ok=True)

# the following files are potentially mislabeled
# they need to be further investigated
potentially_mislabeled = [
    'no/28 no.jpg', 'yes/Y249.JPG', 'yes/Y252.jpg', 'yes/Y257.jpg', 'no/N15.jpg', 
    'no/N16.jpg', 'yes/Y250.jpg', 'no/N11.jpg', 'yes/Y187.jpg', 'no/N1.JPG', 'no/N19.JPG'
]
potentially_mislabeled = [source_path / p for p in potentially_mislabeled]

# Function to split and move files
def split_and_move_files(category):
    files = list((source_path / category).glob('*'))
    # exclude potentially mislabeled files
    files = [f for f in files if f not in potentially_mislabeled]
    random.shuffle(files)
    
    train_split = int(0.8 * len(files))
    valid_split = int(0.1 * len(files))
    
    train_files = files[:train_split]
    valid_files = files[train_split:train_split + valid_split]
    test_files = files[train_split + valid_split:]
    
    for f in train_files:
        shutil.copy(str(f), str(destination_path / 'train' / category / f.name))
    for f in valid_files:
        shutil.copy(str(f), str(destination_path / 'valid' / category / f.name))
    for f in test_files:
        shutil.copy(str(f), str(destination_path / 'test' / category / f.name))

# Split and copy files for 'yes' and 'no' categories
split_and_move_files('yes')
split_and_move_files('no')

print("Files split and moved successfully.")

tumour_images=[]
for name in glob.glob('C:/adity/Documents/PennApps/RealBrainTumorData/yes/*.jpg'): 
    image = cv2.imread(name)
    image = cv2.resize(image,(240,240))
    tumour_images.append(image)
fig = plt.figure(figsize=(10., 10.))
grid = ImageGrid(fig, 111, nrows_ncols=(4, 4),  axes_pad=0.1,   )
for ax, im in zip(grid, tumour_images[0:16]):
    ax.imshow(im)
plt.show()

img_path = "C:/adity/Documents/PennApps/RealBrainTumorData/yes/Y1.jpg"
image = cv2.imread(img_path)
print("width: {} pixels".format(image.shape[1]))
print("height: {} pixels".format(image.shape[0]))
print("channels: {}".format(image.shape[2]))
dim=(500,590)
image=cv2.resize(image, dim)

plt.imshow(image)
plt.show()

print("Image DIsplayed ABove")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, 0.7)
plt.imshow(image)
plt.show()


(T, thresh) = cv2.threshold(gray, 155, 255, cv2.THRESH_BINARY)
plt.imshow(thresh)
plt.show()

(T, threshInv) = cv2.threshold(gray, 155, 255, cv2.THRESH_BINARY_INV)
plt.imshow(threshInv)
plt.show()

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 5))
closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
plt.imshow(closed)
plt.show()

closed = cv2.erode(closed, None, iterations = 19)
closed = cv2.dilate(closed, None, iterations = 17)

plt.imshow(closed)
plt.show()

ret,mask = cv2.threshold(closed, 155, 255, cv2.THRESH_BINARY) 
#apply AND operation on image and mask generated by thrresholding
final = cv2.bitwise_and(image,image,mask = mask) 
plt.imshow(final)
plt.show()

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    
    # return the edged image
    return edged

canny = auto_canny(closed)
plt.imshow(canny)
plt.show()

(cnts, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(image, cnts, -1, (0, 0, 255), 2)
plt.imshow(image) 
plt.show()


