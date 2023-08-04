# Numpy library
import numpy as np

# Phantom
class Phantom():
    # Constructor
    def __init__(self) -> None:
        self.width = 0
        self.height = 0

        self.M = np.array([[(0,0,1),(0,0,1)],[(0,0,1),(0,0,1)]])     # Magnetization vector
        self.T1 = np.array([[0,0],[0,0]])                            # T1
        self.T2 = np.array([[0,0],[0,0]])                            # T2
        self.T2s = np.array([[0,0],[0,0]])                            # T2
        self.PD = np.array([[0,0],[0,0]])                            # Protein Density
        self.DeltaB = np.array([[0,0],[0,0]])                        # Delta B
        
    # Set Data
    def setImage(self, image:np.ndarray):
        if image.ndim == 2:
            width  = image.shape[0]
            height = image.shape[1]
        else:
            width = 0
            height = 0

        self.M = np.zeros((width, height, 3))                # Magnetization vector
        self.T1 = np.zeros(image.shape)                      # T1
        self.T2 = np.zeros(image.shape)                      # T2
        self.T2s = np.zeros(image.shape)                     # T2*
        self.PD = np.zeros(image.shape)                      # Protein Density
        self.DeltaB = np.zeros(image.shape)                  # Delta B
        
        # TODO: test
        self.setRandomData(width, height, image)
                        
    def setRandomData(self, w, h, image):            
        for i in range(w):
            for j in range(h):
                self.M[i][j] = (0,0,1)
                self.PD[i][j] = image[i][j]

                if 0 <= image[i][j] < 25:
                    self.T1[i][j] = 4.0
                    self.T2[i][j] = 2.0
                    self.DeltaB[i][j] = 0.5
                elif 25 <= image[i][j] < 51:
                    self.T1[i][j] = 0.9
                    self.T2[i][j] = 0.05
                    self.DeltaB[i][j] = 0.02
                elif 51 <= image[i][j] < 76:
                    self.T1[i][j] = 0.5
                    self.T2[i][j] = 0.04
                    self.DeltaB[i][j] = 0.02
                elif  76 <= image[i][j] < 101:
                    self.T1[i][j] = 0.25
                    self.T2[i][j] = 0.07
                    self.DeltaB[i][j] = 0.03
                elif 101 <= image[i][j] < 255:
                    self.T1[i][j] = 0.25
                    self.T2[i][j] = 0.02
                    self.DeltaB[i][j] = 0.005
                else:
                    self.T1[i][j] = 0.4
                    self.T2[i][j] = 0.01
                    self.DeltaB[i][j] = 0.005
                    
        self.T2s = 1/((1/self.T2) + self.DeltaB)