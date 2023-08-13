""" Phantom Viewer Class"""

# pylint: disable=C0103, W0105, C0301, W0613, E1136

# math & matrix computations library
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg

from Viewer import viewer

# Phantom for testing
class ImageViewer(viewer):
    """Phantom Viewer Class

    Args:
        FigureCanvasQTAgg (_type_)
    """
    def __init__(self, parent=None, axisExisting=False, axisColor="#fff", title=""):
        super(ImageViewer, self).__init__(parent, axisExisting, axisColor, title)
        self.image = np.array([[0,0],[0,0]])
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
    """Sequence Functions"""
    ###############################################

    # Set image
    def setData(self, path:str, title:str=""):
        super().setData(path)

        # Reading the image
        self.image = mpimg.imread(path)
        
        # Draw the image        
        self.drawData(self.image, title=self.title)
        
    def drawData(self, image, title="Blank", cmap=plt.cm.Greys_r):
        self.image = image
        super().drawData(image, title, cmap)

    def drawData2(self, image, cmap=plt.cm.Greys_r):
        self.image = image
        super().drawData2(image, cmap)
        
    # Reset figure and variables
    def reset(self):
        super().reset()
        
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
            
            # Set Text
            index = f"{x} , {y}" # Index
            intensity = np.round(self.image[x][y],2) # Image intensity
            text = f"{index} = {intensity}"
            self.annot.set_text(text)
        else:
            self.annot.set_visible(False)

        self.fig.canvas.draw_idle()