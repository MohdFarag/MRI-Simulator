import numpy as np
from collections import Counter

# Scale function
def scale_image(image:np.ndarray, a_min=0, a_max=255):
    # Create a new image with the same shape as the original image
    resultImage = np.zeros(image.shape)
    
    # Scale the image
    image = image - image.min()
    if image.max() == 0 and image.min() == 0:
        resultImage = a_max * (image / 1)
    else:            
        resultImage = a_max * (image / image.max())

    return resultImage

def find_most_frequent_pixels(image, top_n=10):
    image = np.array(image)
    
    # Flatten the image
    flattened_image = image.flatten()
    
# Flatten the image into a 1D array
    pixel_values = image.flatten()

    # Count the frequency of each pixel intensity using Counter
    pixel_counts = Counter(pixel_values)

    # Sort the pixel intensity counts in descending order
    sorted_pixel_counts = sorted(pixel_counts.items(), key=lambda x: x[1], reverse=True)

    # Get the top N frequently occurring pixel intensities
    top_pixel_intensities = [pixel_intensity for pixel_intensity, count in sorted_pixel_counts[:top_n]]

    return top_pixel_intensities
