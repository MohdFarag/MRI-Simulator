# PyQt5
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog

# Matplotlib
from PhantomViewer import PhantomViewer
from Phantom import Phantom
from SequenceViewer import SequenceViewer
from ImageViewer import ImageViewer

# Numpy
import numpy as np
import math

# Main Window
class MainWindow(QtWidgets.QMainWindow):
    
    # Constructor
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magnetic Resonance Imaging Simulator")
        self.setWindowIcon(QtGui.QIcon("assets/icon.ico"))
        
        # Create a central widget and set the layout
        central_widget = QtWidgets.QWidget()
        central_layout = QtWidgets.QHBoxLayout()
        
        # Set up the main layout
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        ##############################################################
        
        ## Top splitter
        top_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_splitter.addWidget(top_splitter)

        ###############################
        
        ### Viewer Layout
        viewer_layout = QtWidgets.QVBoxLayout()
        viewer_widget = QtWidgets.QWidget()
        viewer_widget.setLayout(viewer_layout)
        #### Selector
        self.mode_selector = QtWidgets.QComboBox()
        self.mode_selector.addItems(["Protein Density", "T1", "T2", "T2*", "Delta B"])
        viewer_layout.addWidget(self.mode_selector)
        #### Phantom Viewer
        self.phantom_viewer = PhantomViewer(title="Phantom")
        self.phantom_viewer.setCursor(QtGui.QCursor())
        self.phantom_viewer.setFocusPolicy(QtCore.Qt.ClickFocus)
        viewer_layout.addWidget(self.phantom_viewer)

        ###############################

        ### Sequence Layout
        sequence_layout = QtWidgets.QVBoxLayout()
        sequence_widget = QtWidgets.QWidget()
        sequence_widget.setLayout(sequence_layout)
        #### Sequence Viewer
        self.sequence_viewer = SequenceViewer(title="Sequence")
        self.sequence_viewer.setCursor(QtGui.QCursor())
        self.sequence_viewer.setFocusPolicy(QtCore.Qt.ClickFocus)
        sequence_layout.addWidget(self.sequence_viewer)
        #### Control Layout
        control_layout = QtWidgets.QHBoxLayout()
        sequence_layout.addLayout(control_layout)
        ##### Radio Buttons
        self.choose_output_1 = QtWidgets.QRadioButton("Output 1",checked=True)
        self.choose_output_2 = QtWidgets.QRadioButton("Output 2")
        control_layout.addWidget(self.choose_output_1, 1)
        control_layout.addWidget(self.choose_output_2, 1)
        ##### Run Button
        self.run_button = QtWidgets.QPushButton("Run")
        control_layout.addWidget(self.run_button,2)

        ###############################
        
        ### K Space Layout
        k_space_layout = QtWidgets.QVBoxLayout()
        k_space_widget = QtWidgets.QWidget()
        k_space_widget.setLayout(k_space_layout)
        #### K Space Viewer
        self.k_space_viewer = ImageViewer(title="K Space")
        self.k_space_viewer.setCursor(QtGui.QCursor())
        self.k_space_viewer.setFocusPolicy(QtCore.Qt.ClickFocus)
        k_space_layout.addWidget(self.k_space_viewer)

        ###############################
        
        # Add widgets to the layout
        top_splitter.addWidget(viewer_widget)
        top_splitter.addWidget(sequence_widget)
        top_splitter.addWidget(k_space_widget)

        ##############################################################
        
        ## Bottom Splitter
        bottom_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_splitter.addWidget(bottom_splitter)        

        ###############################
        
        ### Output 1 Layout
        output_layout_1 = QtWidgets.QVBoxLayout()
        output_widget_1 = QtWidgets.QWidget()
        output_widget_1.setLayout(output_layout_1)
        #### Output 1 Viewer
        self.output_viewer_1 = ImageViewer(title="Output 1")
        self.output_viewer_1.setCursor(QtGui.QCursor())
        self.output_viewer_1.setFocusPolicy(QtCore.Qt.ClickFocus)
        output_layout_1.addWidget(self.output_viewer_1)
        
        ###############################
        
        ### Output 2 Layout
        output_layout_2 = QtWidgets.QVBoxLayout()
        output_widget_2 = QtWidgets.QWidget()
        output_widget_2.setLayout(output_layout_2)
        #### Output 2 Viewer
        self.output_viewer_2 = ImageViewer(title="Output 2")
        self.output_viewer_2.setCursor(QtGui.QCursor())
        self.output_viewer_2.setFocusPolicy(QtCore.Qt.ClickFocus)
        output_layout_2.addWidget(self.output_viewer_2)

        ###############################
        
        # Add widgets to the layout
        bottom_splitter.addWidget(output_widget_1)
        bottom_splitter.addWidget(output_widget_2)

        ##############################################################
        
        # Set the central widget
        central_layout.addWidget(main_splitter)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
                        
        # Add menu bar
        self.create_menu()

        # Connect signals and slots
        self.connect()
        
        self.load_phantom("./Resources/Phantoms/phantom.png")
        self.load_sequence("./Resources/Sequences/gre_profile.json")
    
    # Connect signals and slots         
    def connect(self):
        self.mode_selector.currentIndexChanged.connect(self.change_mode)
        self.run_button.clicked.connect(self.run_sequence)

    # Create the menu bar
    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        open_phantom_action = QtWidgets.QAction("Open Phantom", self)
        open_phantom_action.setShortcut("Ctrl+p")
        open_phantom_action.triggered.connect(self.open_phantom)

        open_sequence_action = QtWidgets.QAction("Open Sequence", self)
        open_sequence_action.setShortcut("Ctrl+s")
        open_sequence_action.triggered.connect(self.open_sequence)

        file_menu.addAction(open_phantom_action)
        file_menu.addAction(open_sequence_action)

    # Open data
    def open_phantom(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Image Files (*.png *.jpg *.jpeg *.svg *.webp)")
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            if len(filenames) > 0:
                filename = filenames[0]
                try:
                    self.load_phantom(filename)
                except Exception as e:
                    print(e)
                    QtWidgets.QMessageBox.critical(self, "Error", "Unable to open the phantom file.")

    def open_sequence(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Json Files (*.json)")
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            if len(filenames) > 0:
                filename = filenames[0]
                try:
                    self.load_sequence(filename)
                except Exception as e:
                    print(e)
                    QtWidgets.QMessageBox.critical(self, "Error", "Unable to open the sequence file.")                    
    
    # Load the data
    def load_phantom(self, filename):
        # Set the image
        self.phantom_viewer.setData(filename)

    # Load the data
    def load_sequence(self, filename):
        self.sequence_viewer.setData(filename)
    
    # Change mode showed
    def change_mode(self, index):
        self.phantom_viewer.changeAttribute(index)
    
    # Run the sequence
    def run_sequence(self):
        # Get phantom to simulate
        phantom = self.phantom_viewer.getPhantom()
        N = phantom.width
        
        # Get sequence based on time
        sequence = self.sequence_viewer.getSequenceBasedOnTime()
        print(sequence)
        
        # Simulate the sequence
        ## Generate k space
        k_space_result = np.zeros((N, N))
        intervals = np.linspace(0, 360, N)
        angles = np.linspace(-0.5, 0.5, N, endpoint=False)
        
        i = 0
        y_gradient = 0
        while y_gradient < N-1:
            x_gradient = 0
            for seq in sequence:   
                component = seq[1]

                if component == "RF":
                    for x in range(N):
                        for y in range(N):
                            FA = seq[3]
                            phantom.M[x][y] = np.round(self.apply_rf_pulse(phantom.M[x][y], FA))

                elif component == "MGR":
                    if seq[3] == 'y':
                        y_gradient += 1
                    elif seq[3] == 'x':
                        x_gradient += 1

                elif component == "Gr":
                    if seq[4] == 'y':
                        y_gradient += 1
                    elif seq[4] == 'x':
                        x_gradient += 1

                elif component == "DE":
                    for x in range(N):
                        for y in range(N):
                            t = seq[2]
                            phantom.M[x][y] = self.relaxation(phantom.M[x][y], t, phantom.T1[x][y], phantom.T2[x][y], phantom.PD[x][y])

                if component == "RO":
                    while x_gradient < N:
                        phase_shift_x = np.exp(-1j * (np.radians(angles[x_gradient]) * x_gradient))
                        phase_shift_y = np.exp(-1j * (np.radians(angles[y_gradient]) * y_gradient))
                        phase_shift = phase_shift_x * phase_shift_y
                        k_space_result[x_gradient][y_gradient] = np.sum(phantom.M * phase_shift)

                        x_gradient += 1

                i += 1
            
            self.k_space_viewer.drawData(k_space_result, "K Space")
        
        ## Generate output
        ### Make inverse fourier transform
        result_image = np.fft.ifft2(k_space_result)
        
        # Draw the result
        if self.choose_output_1.isChecked():
            self.output_viewer_1.drawData(result_image, "Output 1")
        elif self.choose_output_2.isChecked():
            self.output_viewer_2.drawData(result_image, "Output 2")
    
    """MRI Functions"""
    
    # Apply an RF pulse to a magnetization vector
    def apply_rf_pulse(self, magnetization_vector, flip_angle_deg):
        """
        Apply an RF pulse to a magnetization vector.
        
        Args:
        magnetization (tuple): Tuple representing the initial magnetization vector (x, y, z).
        flip_angle_deg (float): Desired flip angle of the RF pulse in degrees.
        
        Returns:
        tuple: Final magnetization vector after applying the RF pulse.
        """
        # Convert flip angle from degrees to radians        
        flip_angle_rad = np.radians(flip_angle_deg)

        # Compute the sine and cosine of the flip angle
        cos_theta = np.cos(flip_angle_rad)
        sin_theta = np.sin(flip_angle_rad)
        
        # Construct the rotation matrix around x-axis
        rotation_matrix = np.array([[1, 0, 0],
                                    [0, cos_theta, sin_theta],
                                    [0, -sin_theta, cos_theta]])

        # Apply rotation to the magnetization vector
        new_magnetization = np.dot(rotation_matrix, magnetization_vector)
        
        # Apply the RF pulse by multiplying the rotation matrix with the initial magnetization vector
        
        return new_magnetization
    
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
        M0 = 1
        
        mat1 = np.array([[E2, 0, 0],
                         [0, E2, 0],
                         [0, 0, E1]])
        mat2 = np.array([0, 0, M0*(1-E1)])
        magnetization_vector = np.matmul(mat1, magnetization_vector) + mat2
        
        return magnetization_vector
       
    # Close the application
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
    
    # Exit the application  
    def exit(self):
        self.close()
