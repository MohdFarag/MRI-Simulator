""" Phantom Viewer Class"""

# pylint: disable=C0103, W0105, C0301, W0613, E1136

# math & matrix computations library
import numpy as np
import matplotlib.image as mpimg

from viewer import viewer

# Phantom for testing
class ImageViewer(viewer):
    """Phantom Viewer Class

    Args:
        FigureCanvasQTAgg (_type_)
    """
    def __init__(self, parent=None, axisExisting=False, axisColor="#fff", title=""):
        super(ImageViewer, self).__init__(parent, axisExisting, axisColor, title)
                        
    # Set Theme
    def setTheme(self):
        super().setTheme()
        
        # Set background color
        self.fig.set_facecolor("#1f1f21")
        self.axes.set_facecolor("#121212")
    
    ###############################################
    """Sequence Functions"""
    ###############################################

    # Set image
    def setData(self, path:str):
        super().setData(path)

        # Reading the image
        image = mpimg.imread(path)
    
    # Reset figure and variables
    def reset(self):
        super().reset()
