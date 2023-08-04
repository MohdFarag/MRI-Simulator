""" Viewer Class"""

# pylint: disable=C0103, W0105, C0301, W0613, E1136

# math & matrix computations library
import numpy as np

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

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
    def drawData(self, image, title="Blank", cmap=plt.cm.Greys_r):
        self.clearData()

        image = self.scaleImage(image)
        
        self.axes.set_title(title, fontsize = 16)
        self.axes.imshow(image, cmap=cmap, aspect='equal', origin='upper')
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
        
    # Scale function
    def scaleImage(self, image:np.ndarray, a_min=0, a_max=255):
        resultImage = np.zeros(image.shape)
        
        image = image - image.min()
        if image.max() == 0 and image.min() == 0:
            resultImage = a_max * (image / 1)
        else:            
            resultImage = a_max * (image / image.max())

        resultImage = np.round(np.asarray(resultImage, np.int64))
        return resultImage