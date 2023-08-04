""" Phantom Viewer Class"""

# pylint: disable=C0103, W0105, C0301, W0613, E1136

# math & matrix computations library
import numpy as np

# Matplotlib
import matplotlib.image as mpimg
from viewer import viewer

# Phantom for testing
from Phantom import Phantom

PD_ATTRIBUTE = 0
T1_ATTRIBUTE = 1
T2_ATTRIBUTE = 2
T2S_ATTRIBUTE = 3
DELTA_ATTRIBUTE = 4

class PhantomViewer(viewer):
    """Phantom Viewer Class

    Args:
        FigureCanvasQTAgg (_type_)
    """
    def __init__(self, parent=None, axisExisting=False, axisColor="#fff", title=""):
        super(PhantomViewer, self).__init__(parent, axisExisting, axisColor, title)

        # Variables
        self.phantom = Phantom()
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
                        
    # Set Theme
    def setTheme(self):
        super().setTheme()

        # Set background color
        self.fig.set_facecolor("#1f1f21")
        self.axes.set_facecolor("#121212")
        
        # Annotation
        self.annot = self.axes.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->",color="white"))
        self.annot.set_visible(False)


    ###############################################
    """Image Functions"""
    ###############################################

    # Set image
    def setData(self, path:str):       
        super().setData(path)

        # Reading the image
        image = mpimg.imread(path)

        if image.ndim > 2:
            image = image[:,:,0]
        else:
            image = image
        
        self.phantom.setImage(image)
        self.drawData(self.phantom.PD, title="Protein Density")
        
    # Get phantom
    def getPhantom(self):
        return self.phantom

    # Change attribute
    def changeAttribute(self, attribute):
        if attribute == PD_ATTRIBUTE:
            self.drawData(self.phantom.PD, title="Protein Density")
        elif attribute == T1_ATTRIBUTE:
            self.drawData(self.phantom.T1, title="T1")
        elif attribute == T2_ATTRIBUTE:
            self.drawData(self.phantom.T2, title="T2")
        elif attribute == T2S_ATTRIBUTE:
            self.drawData(self.phantom.T2s, title="T2*")
        elif attribute == DELTA_ATTRIBUTE:
            self.drawData(self.phantom.DeltaB, title="Delta B")
                    
    # Reset figure and variables
    def reset(self):
        super().reset()
        self.phantom = Phantom()

    ###############################################
    """plt Functions"""
    ###############################################

    # Update annotation
    def update_annotation(self, event):
        self.annot.xy = event.xdata, event.ydata
        self.annot.get_bbox_patch().set_alpha(0.75)
        
    def hover(self, event):
        if event.xdata != None or event.ydata != None:
            self.annot.set_visible(True)
            self.update_annotation(event)
            
            # X & Y
            x = round(event.ydata)
            y = round(event.xdata)
            
            pdText = f"PD={round(self.phantom.PD[x][y],2)}"
            t1Text = f"T1={round(self.phantom.T1[x][y],2)}"
            t2Text = f"T2={round(self.phantom.T2[x][y],2)}"
            t2sText = f"T2*= {round(self.phantom.T2s[x][y],2)}"
            deltaBText = f"Delta B={round(self.phantom.DeltaB[x][y],2)}"
            text = f"{pdText}\n{t1Text}\n{t2Text}\n{t2sText}\n{deltaBText}"
            self.annot.set_text(text)
        else:
            self.annot.set_visible(False)

        self.fig.canvas.draw_idle()