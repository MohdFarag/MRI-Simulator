# Numpy library
import numpy as np
from utils import scale_image, find_most_frequent_pixels

# Phantom
class Phantom():
    # Constructor
    def __init__(self) -> None:
        self.width = 0
        self.height = 0

        self.M = np.array([[(0,0,0),(0,0,0)],[(0,0,0),(0,0,0)]])     # Magnetization vector
        self.T1 = np.array([[0,0],[0,0]])                            # T1
        self.T2 = np.array([[0,0],[0,0]])                            # T2
        self.T2s = np.array([[0,0],[0,0]])                           # T2 star
        self.PD = np.array([[0,0],[0,0]])                            # Protein Density
        self.DeltaB = np.array([[0,0],[0,0]])                        # Delta B
        
    # Set Data
    def setImage(self, image:np.ndarray):
        # Make sure image is grayscale
        if image.ndim == 2:
            self.width  = image.shape[0]
            self.height = image.shape[1]
        else:
            self.width = 0
            self.height = 0
        
        # Scale image
        image = scale_image(image)

        # Set data
        self.M = np.zeros((self.width, self.height, 3))      # Magnetization vector
        self.PD = image                                      # Protein Density
        self.T1 = np.zeros(image.shape)                      # T1
        self.T2 = np.zeros(image.shape)                      # T2
        self.T2s = np.zeros(image.shape)                     # T2*
        self.DeltaB = np.zeros(image.shape)                  # Delta B
        
        self.set_random_data()
    
    # Get Mz
    def getMz(self):
        return self.M[:,:,2]
    
    # Get Mxy
    def getMxy(self):
        Mxy = self.M[:,:,0] + 1j * self.M[:,:,1]
        return Mxy

    # Get Mx
    def getMx(self):
        Mx = self.M[:,:,0]
        return Mx

    # Get My
    def getMy(self):
        My = 1j * self.M[:,:,1]
        return My
    
    def copy(self):
        copy_phantom = Phantom()
        copy_phantom.width = self.width
        copy_phantom.height = self.height
        copy_phantom.M = np.copy(self.M)
        copy_phantom.T1 = np.copy(self.T1)
        copy_phantom.T2 = np.copy(self.T2)
        copy_phantom.T2s = np.copy(self.T2s)
        copy_phantom.PD = np.copy(self.PD)
        copy_phantom.DeltaB = np.copy(self.DeltaB)
        return copy_phantom
    
    # Reset Magnetization Vector
    def reset_M(self):
        for i in range(self.width):
            for j in range(self.height):
                self.M[i][j] = (0, 0, self.PD[i][j])
                
    # Set Random Data                      
    def set_random_data(self):
        for i in range(self.width):
            for j in range(self.height):
                self.M[i][j] = (0, 0, self.PD[i][j])

                if 0 <= self.PD[i][j] < 25:
                    self.T1[i][j] = 240
                    self.T2[i][j] = 85
                    self.DeltaB[i][j] = 10
                    
                elif 25 <= self.PD[i][j] < 51:
                    self.T1[i][j] = 420
                    self.T2[i][j] = 45
                    self.DeltaB[i][j] = 5
                
                elif 51 <= self.PD[i][j] < 76:
                    self.T1[i][j] = 580
                    self.T2[i][j] = 90
                    self.DeltaB[i][j] = 12
                
                elif  76 <= self.PD[i][j] < 101:
                    self.T1[i][j] = 810
                    self.T2[i][j] = 100
                    self.DeltaB[i][j] = 0.03
                                    
                elif 101 <= self.PD[i][j] < 200:
                    self.T1[i][j] = 2500
                    self.T2[i][j] = 2000
                    self.DeltaB[i][j] = 195

                else:
                    self.T1[i][j] = 1500
                    self.T2[i][j] = 100
                    self.DeltaB[i][j] = 35
                    
        self.T2s = 1/((1/self.T2) + (1/self.DeltaB))
    
    # Set T1, T2, DeltaB
    def set_specific_info(self, t1, t2, deltaB):
        self.T1 = t1
        self.T2 = t2
        self.DeltaB = deltaB
        self.T2s = 1/((1/self.T2) + (1/self.DeltaB))