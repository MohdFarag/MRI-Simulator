# PyQt5
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog
from Worker import SequenceWorker

# Matplotlib
import matplotlib.pyplot as plt

# Viewers
from PhantomViewer import PhantomViewer
from SequenceViewer import SequenceViewer
from ImageViewer import ImageViewer
from Phantom import Phantom

# Numpy
import numpy as np
import math

import warnings
warnings.filterwarnings("ignore")

# Main Window
class MainWindow(QtWidgets.QMainWindow):
    
    # Constructor
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magnetic Resonance Imaging Simulator")
        self.setWindowIcon(QtGui.QIcon("assets/icon.ico"))
        self.running = False
        self.k_space = np.array([])
        
        # Initialize the UI
        self.UI_init()
         
        # Add menu bar
        self.create_menu()

        # Connect signals and slots
        self.connect()
        
        # Show the window        
        self.phantom_viewer.setConstant(3,0)
        self.test1()

    # Initialize the UI
    def UI_init(self):
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
        #### Selector Layout
        selector_layout = QtWidgets.QHBoxLayout()
        ##### Selector
        self.mode_selector = QtWidgets.QComboBox()
        self.mode_selector.addItems(["Protein Density", "T1", "T2", "T2*", "Delta B"])
        selector_layout.addWidget(self.mode_selector,2)
        ##### Reset Button
        self.reset_M_Btn = QtWidgets.QPushButton("Reset Magnetization")
        selector_layout.addWidget(self.reset_M_Btn,1)
        viewer_layout.addLayout(selector_layout)
        #### Phantom Viewer
        self.phantom_viewer = PhantomViewer(title="Phantom")
        self.phantom_viewer.setCursor(QtGui.QCursor())
        self.phantom_viewer.setFocusPolicy(QtCore.Qt.ClickFocus)
        viewer_layout.addWidget(self.phantom_viewer)
        #### Phantom Buttons Layout
        self.phantom_buttons_layout = QtWidgets.QHBoxLayout()
        ##### Shepp Logan Button
        self.shepp_logan_button = QtWidgets.QPushButton("Shepp Logan")
        self.phantom_buttons_layout.addWidget(self.shepp_logan_button)
        ##### Gradient Button
        self.gradient_button = QtWidgets.QPushButton("Gradient")
        self.phantom_buttons_layout.addWidget(self.gradient_button)
        ##### Constant Button
        self.const_button = QtWidgets.QPushButton("Constant")
        self.phantom_buttons_layout.addWidget(self.const_button)
        viewer_layout.addLayout(self.phantom_buttons_layout)
        
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
        self.run_button.setIcon(QtGui.QIcon("./assets/play.ico"))
        self.run_button.setStyleSheet("""background-color: #4f4f4f;
                                      font-size:15px; 
                                      border-radius: 6px; 
                                      border: 1px solid rgba(27, 31, 35, 0.15); 
                                      padding: 5px 15px;
                                      color: #dadada;
                                      font-weight: bold;""")
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
        #### Progress Bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0,100)
        self.progress_bar.setValue(0)
        k_space_layout.addWidget(self.progress_bar)

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
 
    # Connect signals and slots         
    def connect(self):
        # Mode Selector
        self.mode_selector.currentIndexChanged.connect(self.change_mode)
        # Run Button
        self.run_button.clicked.connect(self.run_button_event)
        # Phantom Buttons
        self.shepp_logan_button.clicked.connect(lambda: self.phantom_viewer.setSheppLogan(32))
        self.gradient_button.clicked.connect(lambda: self.phantom_viewer.setGradient(32))
        self.const_button.clicked.connect(lambda: self.phantom_viewer.setConstant(32,120))
        # Reset Mag. Button
        self.reset_M_Btn.clicked.connect(self.phantom_viewer.resetM)

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

    # Open Phantom
    def open_phantom(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Image Files (*.png *.jpg *.jpeg *.svg *.webp)")
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            if len(filenames) > 0:
                filename = filenames[0]
                # try:
                self.load_phantom(filename)
                # except Exception as e:
                #     print(e)
                #     QtWidgets.QMessageBox.critical(self, "Error", "Unable to open the phantom file.")

    # Open Sequence
    def open_sequence(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Json Files (*.json)")
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            if len(filenames) > 0:
                filename = filenames[0]
                # try:
                self.load_sequence(filename)
                # except Exception as e:
                #     print(e)
                #     QtWidgets.QMessageBox.critical(self, "Error", "Unable to open the sequence file.")                    

    # Load Phantom
    def load_phantom(self, filename):
        self.phantom_viewer.setData(filename)

    # Load Sequence
    def load_sequence(self, filename):
        self.sequence_viewer.setData(filename)
    
    # Change mode showed
    def change_mode(self, index):
        self.phantom_viewer.changeAttribute(index)
    
    # Run Button
    def run_button_event(self):
        # Get sequence based on time
        sequence = self.sequence_viewer.get_sequence() # [(Time, Type, duration, flip_angle, Sign), ...]
        if sequence == []:
            QtWidgets.QMessageBox.critical(self, "Error", "Please load a sequence first.")
            return
        else:
            print(sequence)

        if self.running:
            self.run_button.setText("Run")
            self.run_button.setIcon(QtGui.QIcon("./assets/play.ico"))
            self.pause_sequence()
        else:
            self.run_button.setText("Cancel")
            self.run_button.setIcon(QtGui.QIcon("./assets/cancel.ico"))
            self.run_sequence(sequence)
            
        self.running = not self.running

    # Run the sequence
    def run_sequence(self, sequence):
        # Settings before running
        self.choose_output_1.setEnabled(False)
        self.choose_output_2.setEnabled(False)
        
        # Get phantom to simulate
        phantom = self.phantom_viewer.getPhantom() # Phantom object [M, T1, T2, PD]
        N = phantom.width

        # Initialize the thread and worker
        self.thread = QtCore.QThread()
        self.worker = SequenceWorker(phantom, sequence, self.k_space_viewer)

        # Final resets
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.k_space_update.connect(self.k_space_update)
        self.worker.progress.connect(self.updateSimulatorProgress)
        
        # Start the thread
        self.thread.start()

        ## Generate output
        ### Draw the result
        self.thread.finished.connect(self.output_update)

    # Pause the sequence
    def pause_sequence(self):
        self.choose_output_1.setEnabled(True)
        self.choose_output_2.setEnabled(True)
        self.worker.pause()
    
    # Update the progress bar    
    def updateSimulatorProgress(self, progress):
        self.progress_bar.setValue(progress)
        
    @QtCore.pyqtSlot(np.ndarray)
    def k_space_update(self, k_space):
        self.k_space = k_space

    @QtCore.pyqtSlot()    
    def output_update(self):
        ### Make inverse fourier transform
        result_image = np.fft.ifft2(self.k_space)
        
        if self.choose_output_1.isChecked():
            self.output_viewer_1.drawData(np.abs(result_image), title="Output 1")
        elif self.choose_output_2.isChecked():
            self.output_viewer_2.drawData(np.abs(result_image), title="Output 2")
        
        self.run_button.setIcon(QtGui.QIcon("./assets/play.ico"))
        self.run_button.setText("Run")
        
        self.choose_output_1.setEnabled(True)
        self.choose_output_2.setEnabled(True)
        self.running = False

    """MRI Functions"""           
    # Close the application
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
    
    # Exit the application  
    def exit(self):
        self.close()

    def test(self, arr):
        # Draw Inverse Fourier Transform of the k-space
        self.output_viewer_2.drawData(np.fft.fftshift(np.abs(np.fft.ifft2(arr))))
        # Set Sequence
        self.sequence_viewer.setData("./Resources/Sequences/GE_PD.json")
        
    def test1(self):
        arr = np.array([[0,1],[2,3]])
        t1 = np.array([[3000, 500], [1000, 1500]])
        t2 = np.array([[500,  250], [800,  1000]])
        dB = np.array([[50,   100], [200,   150]])
        # Set Attributes
        self.phantom_viewer.setArray(arr)
        self.phantom_viewer.getPhantom().set_specific_info(t1, t2, dB)
        self.test(arr)
        
    def test2(self, N=16):
        image = self.phantom_viewer.setSheppLogan(N)
        self.test(image)