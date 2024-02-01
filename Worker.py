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
    def __init__(self, phantom:Phantom, sequence:MRISequence, k_space_viewer:ImageViewer):
        super().__init__()
        self._isRunning = True
        self.phantom = phantom
        self.sequence = sequence
        self.k_space_viewer = k_space_viewer
            
    # Play the worker thread
    def run(self):
        if not self._isRunning :
            self._isRunning = True
        
        # Get components
        components = self.sequence.get_components()
        
        # Get the phantom size
        N = self.phantom.width
                
        ############ Simulate the sequence ############

        # Generate k space
        self.k_space = np.zeros((N, N), dtype=complex) # Initialize an NxN complex array with zeros
        angles = np.linspace(-180, 180, N, endpoint=False) # Angles that will be used to generate the phase shifts
        
        progress_counter = 0
        pe_gradient = 0 # Phase encoding gradient
        
        # Loop over the phase encoding gradient
        while pe_gradient < N and self._isRunning:
            # Reset the frequency encoding gradient
            fe_gradient = 0
            # Loop over the sequence components
            for component in components:
                # Check component type 
                if type(component) == RFComponent:
                    # If component type is RF
                    flip_angle = component.angle
                    # Apply the RF pulse
                    self.apply_on_phantom(self.rotation, flip_angle, X_AXIS)

                elif type(component) == RelaxationComponent:
                    # If Component Type is relaxation
                    duration = component.duration
                    self.relaxation_phantom(duration)      

                elif type(component) == MultiGradientComponent:
                    # If component type is multi gradient
                    sign = component.sign
                    balanced = component.balanced
                    # Apply the phase encoding gradient
                    # self.apply_phase_encoding(angles, pe_gradient, sign)
                    # Increment the phase encoding gradient
                    # pe_gradient += 1                        
              
                elif type(component) == GradientComponent:
                    # If component type is gradient
                    encoding = component.encoding
                    sign = component.sign
                    balanced = component.balanced
                    if encoding == "phase":
                        pass
                    else:
                        # Apply the frequency encoding gradient
                        pass
       
                elif type(component) == SpoilerComponent:
                    # If component type is spoiler
                    self.apply_on_phantom(self.spoiler)
                                    
                elif type(component) == ReadoutComponent:
                    # If component type is readout
                    while fe_gradient < N and pe_gradient < N:
                        # Apply frequency encoding
                        copied_phantom = self.readout(angles, fe_gradient, pe_gradient)
                        # Read the signal
                        self.k_space[fe_gradient][pe_gradient] = np.sum(copied_phantom.getMxy())
                        # Increment the frequency encoding gradient
                        fe_gradient += 1
                    # Increment the phase encoding gradient
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
    def rotation(self, magnetization_vector:tuple, flip_angle_deg:float, axis:str=X_AXIS):
        # Convert flip angle from degrees to radians
        flip_angle_rad = np.radians(flip_angle_deg)

        # Compute the sine and cosine of the flip angle
        sin_theta = np.sin(flip_angle_rad)
        cos_theta = np.cos(flip_angle_rad)
        
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
        # new_magnetization_vector = np.dot(rotation_matrix, magnetization_vector)
        
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
    
    # Simulate T1 and T2 relaxation on phantom
    def relaxation_phantom(self, t:float):
        N = self.phantom.width
        for x in range(N):
            for y in range(N):
                self.phantom.M[x][y] = self.relaxation(self.phantom.M[x][y], t, self.phantom.t1[x][y], self.phantom.t2_star[x][y], self.phantom.PD[x][y])
   
    # TODO: Apply a spoiler gradient
    def spoiler(self, magnetization_vector):
        magnetization_vector[0] = 0
        magnetization_vector[1] = 0
        return magnetization_vector
    
    # Apply on phantom
    def apply_on_phantom(self, func, *args):
        for x in range(self.phantom.width):
            for y in range(self.phantom.width):
                self.phantom.M[x][y] = func(self.phantom.M[x][y], *args)
    
    # TODO: Apply a phase encoding gradient
    def apply_phase_encoding(self, angles, pe_gradient, sign=1):
        N = self.phantom.width
        for x in range(N):
            for y in range(N):
                # Set the rotation angle
                rotation_angle_pe = sign * angles[pe_gradient] * y                            
                # Apply the rotation
                self.phantom.M[x][y] = self.rotation(self.phantom.M[x][y], rotation_angle_pe, Z_AXIS)
    
    # TODO: Apply a frequency encoding gradient
    def readout(self, angles, fe_gradient, pe_gradient):
        copied_phantom = self.phantom.copy()
        N = self.phantom.width
        for x in range(N):
            for y in range(N):
                # Set the rotation angle
                rotation_angle_pe = angles[pe_gradient] * y                            
                # Apply the rotation
                copied_phantom.M[x][y] = self.rotation(copied_phantom.M[x][y], rotation_angle_pe, Z_AXIS)
                
                # Set the rotation angle
                rotation_angle_fe = angles[fe_gradient] * x
                # Apply the rotation
                copied_phantom.M[x][y] = self.rotation(copied_phantom.M[x][y], rotation_angle_fe, Z_AXIS)
        
        return copied_phantom