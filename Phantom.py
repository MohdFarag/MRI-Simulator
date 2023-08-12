# Numpy library
import numpy as np
from utils import scaleImage

# Phantom
class Phantom():
    # Constructor
    def __init__(self) -> None:
        self.width = 0
        self.height = 0

        self.M = np.array([[(0,0,0),(0,0,0)],[(0,0,0),(0,0,0)]])     # Magnetization vector
        self.T1 = np.array([[0,0],[0,0]])                            # T1
        self.T2 = np.array([[0,0],[0,0]])                            # T2
        self.T2s = np.array([[0,0],[0,0]])                            # T2
        self.PD = np.array([[0,0],[0,0]])                            # Protein Density
        self.DeltaB = np.array([[0,0],[0,0]])                        # Delta B
        
    # Set Data
    def setImage(self, image:np.ndarray):
        if image.ndim == 2:
            self.width  = image.shape[0]
            self.height = image.shape[1]
        else:
            self.width = 0
            self.height = 0
        
        # Scale image
        image = scaleImage(image)

        # Set data
        self.M = np.zeros((self.width, self.height, 3))      # Magnetization vector
        self.PD = image                                      # Protein Density
        self.T1 = np.zeros(image.shape)                      # T1
        self.T2 = np.zeros(image.shape)                      # T2
        self.T2s = np.zeros(image.shape)                     # T2*
        self.DeltaB = np.zeros(image.shape)                  # Delta B
        
        self.setRandomData()
    
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
    
    # Set Random Data                      
    def setRandomData(self):
        for i in range(self.width):
            for j in range(self.height):
                self.M[i][j] = (0, 0, self.PD[i][j])

                if 0 <= self.PD[i][j] < 25:
                    self.T1[i][j] = 3.5
                    self.T2[i][j] = 1.4
                    self.DeltaB[i][j] = 0.05
                    
                elif 25 <= self.PD[i][j] < 51:
                    self.T1[i][j] = 1.5
                    self.T2[i][j] = 1.2
                    self.DeltaB[i][j] = 0.10
                
                elif 51 <= self.PD[i][j] < 76:
                    self.T1[i][j] = 1.4
                    self.T2[i][j] = 0.45
                    self.DeltaB[i][j] = 0.020
                
                elif  76 <= self.PD[i][j] < 101:
                    self.T1[i][j] = 3.2
                    self.T2[i][j] = 0.8
                    self.DeltaB[i][j] = 0.3
                
                elif 101 <= self.PD[i][j] < 255:
                    self.T1[i][j] = 0.35
                    self.T2[i][j] = 0.010
                    self.DeltaB[i][j] = 0.0005

                else:
                    self.T1[i][j] = 0.8
                    self.T2[i][j] = 0.40
                    self.DeltaB[i][j] = 0.015
                    
        self.T2s = 1/((1/self.T2) + self.DeltaB)