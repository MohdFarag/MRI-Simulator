# PyQt5 imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Other imports
import time
import numpy as np

# Importing the Phantom class
from Phantom import Phantom
from ImageViewer import ImageViewer
from SequenceViewer import *

X_AXIS = 'x'
Y_AXIS = 'y'
Z_AXIS = 'z'

class SequenceWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    k_space_update = pyqtSignal(np.ndarray)
    
    # Initialize the worker thread
    def __init__(self, phantom:Phantom, sequence:list, k_space_viewer:ImageViewer):
        super().__init__()
        self._isRunning = True
        self.phantom = phantom
        self.sequence = sequence
        self.k_space_viewer = k_space_viewer
            
    # Play the worker thread
    def run(self):
        if not self._isRunning :
            self._isRunning = True
            
        # Get the phantom size
        N = self.phantom.width
                
        # Simulate the sequence
        ## Generate k space
        self.k_space = np.zeros((N, N), dtype=complex) # Initialize an NxN complex array with zeros        
        angles = np.linspace(-180, 180, N, endpoint=False) # Angles that will be used to generate the phase shifts
        
        pe_gradient = 0 # Phase encoding gradient        
        pe_flag = False # Flag to check if the sequence has phase encoding component
        progress_counter = 0 # Progress counter
        
        # Loop over the phase encoding gradient
        while pe_gradient < N and self._isRunning:
            # Reset the frequency encoding gradient
            fe_gradient = 0
            # Loop over the sequence components
            for component in self.sequence:
                # Get Component Type
                component_type = component[1]

                # Check component type 
                if component_type == RF_PULSE:
                    # If component type is RF
                    for x in range(N):
                        for y in range(N):
                            # Get Flip Angle
                            flip_angle = component[3]
                            # Apply RF pulse by specific flip angle
                            self.phantom.M[x][y] = self.rotation(self.phantom.M[x][y], flip_angle, X_AXIS)
                
                elif component_type == RELAXATION:
                    # If Component Type is relaxation
                    for x in range(N):
                        for y in range(N):
                            t = component[2]
                            self.phantom.M[x][y] = self.relaxation(self.phantom.M[x][y], t, self.phantom.T1[x][y], self.phantom.T2[x][y], self.phantom.PD[x][y])
                                                        
                elif component_type == PE_MULTI_GRADIENT:
                    pe_flag = True

                elif component_type == FE_GRADIENT:
                    pass

                elif component_type == SPOILER:
                    for x in range(N):
                        for y in range(N):
                            self.phantom.M[x][y] = self.spoiler(self.phantom.M[x][y])
                                    
                elif component_type == READOUT:
                    # If component type is readout
                    while fe_gradient < N and pe_gradient < N:
                        copied_phantom = self.phantom.copy()
                        for x in range(N):
                            for y in range(N):
                                # Set the rotation angle
                                rotation_angle_pe = angles[pe_gradient] * y
                                rotation_angle_fe = angles[fe_gradient] * x
                                
                                # Apply the rotation
                                copied_phantom.M[x][y] = self.rotation(copied_phantom.M[x][y], rotation_angle_pe, Z_AXIS)
                                copied_phantom.M[x][y] = self.rotation(copied_phantom.M[x][y], rotation_angle_fe, Z_AXIS)
                                
                                # Read the signal
                                self.k_space[pe_gradient][fe_gradient] += copied_phantom.getMxy()[x][y]

                        fe_gradient += 1

                    # If sequence has phase encoding component
                    if pe_flag:
                        pe_gradient += 1

                    # Update the k-space matrix
                    self.k_space_update.emit(self.k_space)
                    self.k_space_viewer.drawData2(np.abs(self.k_space))
                
            progress_counter += 1
            self.progress.emit(round((progress_counter/N)*100))
                
        self.finished.emit()
    
    # Pause the worker thread
    def pause(self):
        self._isRunning = False

    # Apply an RF pulse to a magnetization vector
    def rotation(self, magnetization_vector:tuple, flip_angle_deg:float, axis:str="x"):
        # Convert flip angle from degrees to radians
        flip_angle_rad = np.radians(flip_angle_deg)

        # Compute the sine and cosine of the flip angle
        sin_theta = np.sin(flip_angle_rad)
        cos_theta = np.cos(flip_angle_rad)
        
        axis = axis.lower() # Convert axis to lowercase        
        if axis == X_AXIS:
            # Construct the rotation matrix around x-axis
            rotation_matrix = np.array([[1,             0,                  0],
                                        [0,             cos_theta,   sin_theta],
                                        [0,             -sin_theta,  cos_theta]])
        
        elif axis == Y_AXIS:
            rotation_matrix = np.array([[cos_theta,     0,      -sin_theta],
                                        [0,             1,               0],
                                        [sin_theta,     0,       cos_theta]])
        
        elif axis == Z_AXIS:
            rotation_matrix = np.array([[cos_theta,     sin_theta,     0],
                                        [-sin_theta,    cos_theta,     0],
                                        [0,             0,             1]])            

        # Apply rotation to the magnetization vector
        new_magnetization_vector = np.matmul(rotation_matrix, magnetization_vector)
        return new_magnetization_vector
    
    # Simulate T1 and T2 relaxation of magnetization
    def relaxation(self, magnetization_vector, t:float, t1:float, t2:float, PD:float):
        """
        Simulate T1 and T2 relaxation of magnetization.
        
        Parameters:
        phantom (Phantom): Phantom object.
        t (float): Time elapsed since excitation.
        
        Returns:
        phantom (Phantom): Phantom object.
        """
        E1 = np.exp(-t/t1)
        E2 = np.exp(-t/t2)
        M0 = PD
        
        mat1 = np.array([[E2, 0, 0],
                         [0, E2, 0],
                         [0, 0, E1]])
        mat2 = np.array([0, 0, M0*(1-E1)])
        magnetization_vector = np.dot(mat1, magnetization_vector) + mat2
        
        return magnetization_vector
    
    # Apply a spoiler gradient
    def spoiler(self, magnetization_vector):
        magnetization_vector[0] = 0
        magnetization_vector[1] = 0
        return magnetization_vector