import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Load the image
image_path = "C:/Users/User/OneDrive/Pictures/Screenshots/Screenshot 2024-09-21 121815.png"
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Display the original image
plt.imshow(image, cmap='gray')
plt.title("Original MRI Image")
plt.show()

# Step 1: Preprocessing - Thresholding to segment the region of interest
_, binary_image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)

# Display the thresholded image
plt.imshow(binary_image, cmap='gray')
plt.title("Thresholded Image")
plt.show()

# Step 2: Creating pseudo-slices (for demonstration purposes, duplicate image with modifications)
slices = []
for i in range(20):  # Create 20 slices by rotating or translating the original
    rotation_matrix = cv2.getRotationMatrix2D((image.shape[1]//2, image.shape[0]//2), i, 1)
    rotated = cv2.warpAffine(binary_image, rotation_matrix, (image.shape[1], image.shape[0]))
    slices.append(rotated)

# Convert the slices into a 3D volume
volume = np.stack(slices, axis=-1)

# Step 3: Generate 3D model using marching cubes
verts, faces, _, _ = measure.marching_cubes(volume, level=0)

# Step 4: Plot the 3D model
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
mesh = Poly3DCollection(verts[faces], alpha=0.7)
ax.add_collection3d(mesh)

# Set plot limits
ax.set_xlim(0, volume.shape[0])
ax.set_ylim(0, volume.shape[1])
ax.set_zlim(0, volume.shape[2])

# Show the plot
plt.show()

# Optional: Export as STL or OBJ
# from stl import mesh
# your_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
# for i, f in enumerate(faces):
#     for j in range(3):
#         your_mesh.vectors[i][j] = verts[f[j],:]
# your_mesh.save('brain_model.stl')
