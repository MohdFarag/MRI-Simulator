""" Viewer Class"""

# pylint: disable=C0103, W0105, C0301, W0613, E1136

# math & matrix computations library
import numpy as np
from utils import scale_image

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

COLOR_MAP = plt.cm.Greys_r

class viewer(FigureCanvasQTAgg):
    """Viewer Class

    Args:
        FigureCanvasQTAgg (_type_)
    """
    def __init__(self, parent=None, axisExisting=False, axisColor="#fff", title=""):
        self.fig = Figure(figsize = (6, 6), dpi = 80)
        self.axes = self.fig.add_subplot(111)
        
        # Variables
        self.axisExisting = axisExisting
        self.axisColor = axisColor
        self.title = title
        self.xlabel = "Width"
        self.ylabel = "Height"
        self.setTheme()
        
        super(viewer, self).__init__(self.fig)
                
    # Set Grid
    def setGrid(self, status):
        self.axes.grid(status)

    # Set Theme
    def setTheme(self):
        # Set labels
        fontStyle = {'fontsize': 17,
                    'fontweight' : 900,
                    'verticalalignment': 'top',
                    'color': "#fff"
                    }
        
        self.axes.set_title(self.title, fontStyle)
        self.axes.set_xlabel(self.xlabel, {'color': "#fff"})
        self.axes.set_ylabel(self.ylabel, {'color': "#fff"})
        
        # Spines Color        
        self.axes.spines['bottom'].set_color(self.axisColor)
        self.axes.spines['top'].set_color(self.axisColor)
        self.axes.spines['right'].set_color(self.axisColor)
        self.axes.spines['left'].set_color(self.axisColor)

        self.fig.set_edgecolor("black")

        # Axis Existing
        if not self.axisExisting:
            self.axes.set_xticks([])
            self.axes.set_yticks([])

        # Plot Style
        plt.style.context('fivethirtyeight')

    ###############################################
    """Image Functions"""
    ###############################################

    # Set image
    def setData(self, path:str):
        # If image is RGB transform it to gray.
        self.clearData()
                        
    # Draw image with matplotlib
    def drawData(self, image, cmap=COLOR_MAP, title=None, origin=None):
        if title is None and origin is None:
            self.drawData2(image, cmap)
        else:
            if title is None:
                title = "Blank"
            if origin is None:
                origin = 'upper'
            self.drawData1(image, cmap, title, origin)
    
    # Draw image with matplotlib
    def drawData1(self, image, cmap=COLOR_MAP, title="Blank", origin='upper'):
        # Clear figure
        self.clearData()
                 
        # Draw image
        self.axes.set_title(title, fontsize = 16)
        self.axes.imshow(image, cmap=cmap, origin=origin)
        self.draw()

    # Draw image with matplotlib without title
    def drawData2(self, image, cmap=COLOR_MAP):
        # Draw image
        self.axes.imshow(image, cmap=cmap)
        self.draw()

    # Save Image
    def saveData(self,path):
        self.fig.savefig(path, bbox_inches='tight')

    # Clear figure
    def clearData(self):
        self.axes.clear()
        self.setTheme()
        self.draw()
                    
    # Reset figure and variables
    def reset(self):
        self.clearData()