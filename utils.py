import numpy as np

# Scale function
def scaleImage(image:np.ndarray, a_min=0, a_max=255):
    # Create a new image with the same shape as the original image
    resultImage = np.zeros(image.shape)
    
    # Scale the image
    image = image - image.min()
    if image.max() == 0 and image.min() == 0:
        resultImage = a_max * (image / 1)
    else:            
        resultImage = a_max * (image / image.max())

    return resultImage