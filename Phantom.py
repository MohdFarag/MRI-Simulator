# Numpy library
import numpy as np
from utils import scale_image, find_most_frequent_pixels

# Enum
PD = 0
T1 = 1
T2 = 2
T2_STAR = 3
DB = 4

MX = 0
MY = 1
MZ = 2

# Phantom
class Phantom():
    # Constructor
    def __init__(self) -> None:
        self.width = 0
        self.height = 0

        self.M = np.array([[(0,0,0),(0,0,0)],[(0,0,0),(0,0,0)]])     # Magnetization vector
        self.t1 = np.array([[0,0],[0,0]])                            # T1
        self.t2 = np.array([[0,0],[0,0]])                            # T2
        self.t2_star = np.array([[0,0],[0,0]])                           # T2 star
        self.PD = np.array([[0,0],[0,0]])                            # Protein Density
        
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
        self.t1 = np.zeros(image.shape)                      # T1
        self.t2 = np.zeros(image.shape)                      # T2
        self.t2_star = np.zeros(image.shape)                     # T2*
        
        self.set_random_data()
        
    def set_numpy(self, numpy_matrix:np.ndarray):
        # Make sure image is grayscale
        if numpy_matrix.ndim == 3:
            self.width  = numpy_matrix.shape[0]
            self.height = numpy_matrix.shape[1]
        else:
            self.width = 0
            self.height = 0

        # Set data
        self.PD = numpy_matrix[:,:,PD]                        # Protein Density
        self.t1 = numpy_matrix[:,:,T1]                        # T1
        self.t2 = numpy_matrix[:,:,T2]                        # T2
        self.t2_star = numpy_matrix[:,:,T2_STAR]              # T2*
            
        self.M = np.zeros((self.width, self.height, 3))       # Magnetization vector
        for i in range(self.width):
            for j in range(self.height):
                self.M[i][j] = (0, 0, self.PD[i][j])

    # Get Mz
    def getMz(self):
        return self.M[:,:,MZ]
    
    # Get Mxy
    def getMxy(self):
        Mxy = self.M[:,:,MX] + 1j * self.M[:,:,MY]
        return Mxy

    # Get Mx
    def getMx(self):
        Mx = self.M[:,:,MX]
        return Mx

    # Get My
    def getMy(self):
        My = 1j * self.M[:,:,MY]
        return My
    
    def copy(self):
        copy_phantom = Phantom()
        copy_phantom.width = self.width
        copy_phantom.height = self.height
        copy_phantom.M = np.copy(self.M)
        copy_phantom.t1 = np.copy(self.t1)
        copy_phantom.t2 = np.copy(self.t2)
        copy_phantom.t2_star = np.copy(self.t2_star)
        copy_phantom.PD = np.copy(self.PD)
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
                    self.t1[i][j] = 240
                    self.t2[i][j] = 85
                    self.t2_star[i][j] = 100
                    
                elif 25 <= self.PD[i][j] < 51:
                    self.t1[i][j] = 420
                    self.t2[i][j] = 45
                    self.t2_star[i][j] = 50
                
                elif 51 <= self.PD[i][j] < 76:
                    self.t1[i][j] = 580
                    self.t2[i][j] = 90
                    self.t2_star[i][j] = 120
                
                elif  76 <= self.PD[i][j] < 101:
                    self.t1[i][j] = 810
                    self.t2[i][j] = 100
                    self.t2_star[i][j] = 5
                                    
                elif 101 <= self.PD[i][j] < 200:
                    self.t1[i][j] = 2500
                    self.t2[i][j] = 2000
                    self.t2_star[i][j] = 1550

                else:
                    self.t1[i][j] = 1500
                    self.t2[i][j] = 100
                    self.t2_star[i][j] = 35
                        
    # Set T1, T2, DeltaB
    def set_information(self, t1, t2, t2_star):
        self.t1 = t1
        self.t2 = t2
        self.t2_star = t2_star