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
        #### Run Button
        self.run_button = QtWidgets.QPushButton("Run")
        sequence_layout.addWidget(self.run_button)

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
        # Get sequence based on time
        sequence = self.sequence_viewer.getSequenceBasedOnTime()
        
        for element in sequence:
            if element[0] == "RF":
                pass
    
    """MRI Functions"""
    def relaxation(self, phantom:Phantom, t:float):
        """
        Simulate T1 and T2 relaxation of magnetization.
        
        Parameters:
        phantom (Phantom): Phantom object.
        t (float): Time elapsed since excitation.
        
        Returns:
        phantom (Phantom): Phantom object.
        """
        for i in range(phantom.width):
            for j in range(phantom.height):
                phantom.M[i][j][0] = phantom.M[i][j][0] * math.exp(-t / phantom.T2[i][j])
                phantom.M[i][j][1] = phantom.M[i][j][1] * math.exp(-t / phantom.T2[i][j])
                phantom.M[i][j][2] = phantom.PD * (1 - math.exp(-t / phantom.T1[i][j]))
                
        return phantom
       
    # Close the application
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
    
    # Exit the application  
    def exit(self):
        self.close()
