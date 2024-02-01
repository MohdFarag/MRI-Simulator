""" Phantom Viewer Class"""

# pylint: disable=C0103, W0105, C0301, W0613, E1136

# math & matrix computations library
import numpy as np

# Matplotlib
import matplotlib.image as mpimg
from Viewer import viewer

# Phantom for testing
from Phantom import *
from phantominator import shepp_logan


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
    def setData(self, path:str, ext:str):
        super().setData(path)

        # Reading the image
        if ext == "npy":
            array = np.load(path)
            self.phantom.set_numpy(array)            
        else:
            array = mpimg.imread(path)
            if array.ndim > 2:
                array = array[:,:,0]
            else:
                array = array
            self.phantom.setImage(array)
        
        self.drawData(self.phantom.PD, title="Protein Density")
        return array

    # Set Shepp Logan
    def setSheppLogan(self, N:int):       
        image = shepp_logan(N)

        if image.ndim > 2:
            image = image[:,:,0]
        else:
            image = image

        self.phantom.setImage(image)
        self.drawData(self.phantom.PD, title="Protein Density")
        return image

    # Set constant
    def setConstant(self, N:int, value:int):       
        image = np.ones((N, N), dtype=np.uint8)
        image = image * value

        self.phantom.setImage(image)
        self.drawData(self.phantom.PD, title="Protein Density")
        return image

    # Set specific array
    def setArray(self, array):
        array = np.array(array)
        self.phantom.setImage(array)
        self.drawData(self.phantom.PD, title="Protein Density")
    
    # Generate gradient
    def generate_gradient(self, N, color1=0, color2=255, direction="horizontal"):
        image = np.zeros((N, N), dtype=np.uint8)
        
        if direction == "horizontal":
            for x in range(N):
                image[:, x] = int(color1 * (1 - x / N) + color2 * (x / N))
        elif direction == "vertical":
            for y in range(N):
                image[y, :] = int(color1 * (1 - y / N) + color2 * (y / N))
        
        return image

    # Set gradient
    def setGradient(self, N:int):       
        image = self.generate_gradient(N)

        if image.ndim > 2:
            image = image[:,:,0]
        else:
            image = image

        self.phantom.setImage(image)
        self.drawData(self.phantom.PD, title="Protein Density")
        return image
        
    # Get phantom
    def getPhantom(self):
        return self.phantom

    # Change attribute
    def changeAttribute(self, attribute):
        if attribute == PD:
            self.drawData(self.phantom.PD, title="Protein Density")
        elif attribute == T1:
            self.drawData(self.phantom.t1, title="T1")
        elif attribute == T2:
            self.drawData(self.phantom.t2, title="T2")
        elif attribute == T2_STAR:
            self.drawData(self.phantom.t2_star, title="T2*")
                    
    # Reset figure and variables
    def reset(self):
        super().reset()
        self.phantom = Phantom()

    # Reset magnetization vector
    def resetM(self):
        self.phantom.reset_M()
        
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
            
            MText = f"(x,y,z)=({round(self.phantom.M[x][y][0],2)}, {round(self.phantom.M[x][y][1],2)}, {round(self.phantom.M[x][y][2],2)})"
            pdText = f"PD={round(self.phantom.PD[x][y],2)}"
            t1Text = f"T1={round(self.phantom.t1[x][y],2)}"
            t2Text = f"T2={round(self.phantom.t2[x][y],2)}"
            t2sText = f"T2*= {round(self.phantom.t2_star[x][y],2)}"

            text = f"{MText}\n{pdText}\n{t1Text}\n{t2Text}\n{t2sText}"
            self.annot.set_text(text)
        else:
            self.annot.set_visible(False)

        self.fig.canvas.draw_idle()