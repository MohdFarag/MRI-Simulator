""" Sequence Viewer Class"""

# math & matrix computations library
import numpy as np
import math

# MRI Sequence Diagram Library
import mrsd
from MRISequence import *
from Component import *

# Json library
import json

# Viewer
from Viewer import viewer

# Constants
## Diagram Titles
RF_PULSE = "RF"
GSS = "$G_{SS}$"
GPE = "$G_{PE}$"
GFE = "$G_{FE}$"
SIGNAL = "Signal"

# Phantom for testing
class SequenceViewer(viewer):
    """Phantom Viewer Class

    Args:
        FigureCanvasQTAgg (_type_)
    """
    def __init__(self, parent=None, axisExisting=False, axisColor="#fff", title=""):
        super(SequenceViewer, self).__init__(parent, axisExisting, axisColor, title)
        
        # Variables
        self.sequence = MRISequence()
        ## Information
        self.name = ""
        self.acronym = ""
        ## Intervals
        self.TR = 0
        self.TE = 0
        ## Axis of gradients
        self.ssAxis = "z"
        self.peAxis = "y"
        self.feAxis = "x"
        
        # Initialize the figure
        self.diagram = mrsd.Diagram(
            self.axes, [RF_PULSE, GSS, GPE, GFE, SIGNAL])
                
    # Set Theme
    def setTheme(self):
        super().setTheme()
        
        # Set background color
        self.fig.set_facecolor("#fcfcfc")
        self.axes.set_facecolor("#ffffff")
        
        fontStyle = {
                    'fontsize': 17,
                    'fontweight' : 900,
                    'verticalalignment': 'top',
                    'color': "#000"
        }
        
        self.axes.set_title(self.title, fontStyle)
    
    # Set Data
    def setData(self, path:str):
        super().setData(path)
                
        #################### Read Json File ####################
        with open(path, 'r') as file:
            params = json.load(file)

        #################### Update the parameters with JSON data ####################
        self.name = params.get('name')
        self.acronym = params.get('acronym')
        self.axes.set_title(f"{self.name} ({self.acronym})")
        
        # Gradients Axis
        self.ssAxis = params.get('ssAxis')
        self.peAxis = params.get('peAxis')
        self.feAxis = params.get('feAxis')

        # Intervals
        self.TR = params.get('TR')
        self.TE = params.get('TE')
        self.sequence.set_TR(self.TR)
        self.sequence.set_TE(self.TE)

        ################# Add Intervals #################
        self.add_intervals()
        
        ################# Add Components #################
        components = params.get('component')
        
        ######## RF ########
        RFs = components['RF']
        for RF in RFs:
            rf_pulse, gradient = self.add_RF(RF)
        
        ######## PE ########
        PEs = components.get('PE')
        # Multi PEs
        multi_PEs = PEs.get('multi')
        for multi_PE in multi_PEs:
            self.add_multi_gradient(multi_PE, GPE)
            
        # Single PEs
        single_PEs = PEs.get('single')
        for single_PE in single_PEs:
            self.add_gradient(single_PE, GPE)

        ######## FE ########
        # Single PEs
        FEs = components.get('FE')
        for FE in FEs:
            self.add_gradient(FE, GFE)

        ######## Spoiler ########
        spoilers = components.get('spoiler')
        for spoiler in spoilers:
            self.add_spoiler(spoiler, GPE)
            
        ######## readout/Signal ########
        readout = components.get('readout')
        # Readout Parameters
        trajectory = readout.get('trajectory')
        self.sequence.set_trajectory(trajectory)
        
        signals = readout.get('signals') 
        for signal in signals:
            self.add_RO(signal)

        # Sort & Add Relaxations
        self.sequence.sort()
        self.sequence.setup()
        self.draw()
     
    # Clear figure
    def clearData(self):
        super().clearData()
        self.sequence = MRISequence()
        self.diagram = mrsd.Diagram(
            self.axes, [RF_PULSE, GSS, GPE, GFE, SIGNAL])

    ###############################################
    """Sequence Functions"""
    ###############################################

    # Add RF
    def add_RF(self, RF):
        # Get flip angle
        flip_angle = RF.get('flipAngle')
        flip_angle_rad = np.round(math.radians(flip_angle),2)
        
        # Get time and duration
        time = self.read_time(RF)
        duration = RF.get('duration')
        
        # Add RF
        rf_pulse, gradient = self.diagram.selective_pulse(RF_PULSE, 
                                                          GSS, 
                                                          duration=duration, 
                                                          pulse_amplitude=flip_angle_rad, 
                                                          center=time, 
                                                          gradient_amplitude=flip_angle_rad/2)
        self.diagram.annotate(RF_PULSE, x=rf_pulse.end, y=0.2, text=rf"$\alpha$={flip_angle}")

        # Add to sequence        
        rf_comp = RFComponent(time, duration, flip_angle)
        self.sequence.add_component(rf_comp)

        return rf_pulse, gradient

    # Add gradient
    def add_gradient(self, gradient, loc):
        time = self.read_time(gradient)
        step = gradient.get('step')
        sign = gradient.get('sign')
        duration = gradient.get('duration')
        balanced = gradient.get('balanced')
        
        self.diagram.gradient(loc, duration, step/2, duration, center=time)

        # Add to time based sequence
        if loc == GPE:
            gradient_comp = GradientComponent(time, duration, "phase", sign, balanced)
        elif loc == GFE:
            gradient_comp = GradientComponent(time, duration, "frequency", sign, balanced)
        
        self.sequence.add_component(gradient_comp)

    # Add multi gradient
    def add_multi_gradient(self, gradient, loc):
        time = self.read_time(gradient)
        duration = gradient.get('duration')
        sign = gradient.get('sign')
        balanced = gradient.get('balanced')
        
        # Draw multi gradient and annotate        
        self.diagram.multi_gradient(loc, amplitude=0.65, flat_top=self.TR/10, center = time)
        if sign == True:
            self.diagram.annotate(loc, time, 0.9, r"$\uparrow$")
        else:
            self.diagram.annotate(loc, time, 0.9, r"$\downarrow$")

        # Add to sequence
        gradient_comp = MultiGradientComponent(time, duration, sign, balanced)
        self.sequence.add_component(gradient_comp)

    # Add readout
    def add_RO(self, signal):
        time = self.read_time(signal)
        duration = signal.get('duration')
        adc, echo, readout = self.diagram.readout(SIGNAL, GFE, duration, ramp=0, center=self.TE+1/2*duration, gradient_amplitude=0.5)
        
        # Add to time based sequence
        readout_comp = ReadoutComponent(time, duration)
        self.sequence.add_component(readout_comp)

    # Add intervals
    def add_intervals(self):
        if self.TE != 0:
            self.diagram.interval(0, self.TE/4, -0.8, f"TE={self.TE}")
        if self.TR != 0:
            self.diagram.interval(0, self.TR/4, -1.2, f"TR={self.TR}")
    
    # Add Spoiler
    def add_spoiler(self, spoiler, loc):
        time = self.read_time(spoiler)
        duration = spoiler.get('duration')
        
        # Draw spoiler         
        self.diagram.gaussian_pulse(loc, amplitude=1, duration=duration, center=time)
 
        # Add to time based sequence
        spoiler_comp = SpoilerComponent(time, duration)
        self.sequence.add_component(spoiler_comp)
       
    # Read time
    def read_time(self, item):
        time = str(item.get('time'))
        time = eval(time,
                    {}, 
                    {"TE": self.TE, "TR": self.TR})
        
        return time
    
    # Get Sequence Based On time
    def get_sequence(self):
        return self.sequence
    
    # Reset figure and variables
    def reset(self):
        super().reset()