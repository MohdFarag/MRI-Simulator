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
            self.width  = image.shape[0]
            self.height = image.shape[1]
        else:
            self.width = 0
            self.height = 0

        self.M = np.zeros((self.width, self.height, 3))      # Magnetization vector
        self.PD = image*255                                  # Protein Density
        self.T1 = np.zeros(image.shape)                      # T1
        self.T2 = np.zeros(image.shape)                      # T2
        self.T2s = np.zeros(image.shape)                     # T2*
        self.DeltaB = np.zeros(image.shape)                  # Delta B
        
        self.setRandomData()
                        
    def setRandomData(self):
        for i in range(self.width):
            for j in range(self.height):                     
                self.M[i][j] = (0, 0, 1)
                if 0 <= self.PD[i][j] < 25:
                    self.T1[i][j] = 3500
                    self.T2[i][j] = 2000
                    self.DeltaB[i][j] = 0.5
                elif 25 <= self.PD[i][j] < 51:
                    self.T1[i][j] = 1000
                    self.T2[i][j] = 120
                    self.DeltaB[i][j] = 10
                elif 51 <= self.PD[i][j] < 76:
                    self.T1[i][j] = 400
                    self.T2[i][j] = 30
                    self.DeltaB[i][j] = 20
                elif  76 <= self.PD[i][j] < 101:
                    self.T1[i][j] = 1500
                    self.T2[i][j] = 1000
                    self.DeltaB[i][j] = 30
                elif 101 <= self.PD[i][j] < 255:
                    self.T1[i][j] = 250
                    self.T2[i][j] = 10
                    self.DeltaB[i][j] = 5
                else:
                    self.T1[i][j] = 1200
                    self.T2[i][j] = 550
                    self.DeltaB[i][j] = 15
                    
        self.T2s = 1/((1/self.T2) + self.DeltaB)