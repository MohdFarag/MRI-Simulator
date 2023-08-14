""" Sequence Viewer Class"""

# math & matrix computations library
import numpy as np
import math

# MRI Sequence Diagram Library
import mrsd

# Json library
import json

# Viewer
from Viewer import viewer

# Constants
RF_PULSE = "RF"
RELAXATION = "RELAXATION"
READOUT = "READOUT"
SPOILER = "SPOILER"
PE_MULTI_GRADIENT = "PE_MULTI_GRADIENT"
PE_GRADIENT = "PE_GRADIENT"
FE_GRADIENT = "FE_GRADIENT"

RF_TITLE, GSS_TITLE, GPE_TITLE, GFE_TITLE, SIGNAL_TITLE = "RF", "$G_{SS}$", "$G_{PE}$", "$G_{FE}$", "Signal"

# Phantom for testing
class SequenceViewer(viewer):
    """Phantom Viewer Class

    Args:
        FigureCanvasQTAgg (_type_)
    """
    def __init__(self, parent=None, axisExisting=False, axisColor="#fff", title=""):
        super(SequenceViewer, self).__init__(parent, axisExisting, axisColor, title)
        
        # Variables
        self.timeBasedSequence = list()
        ## Information
        self.name = ""
        self.abbreviation = ""
        ## Intervals
        self.TR = 0
        self.TE = 0
        ## Axis of gradients
        self.ssAxis = "z"
        self.peAxis = "y"
        self.feAxis = "x"
        
        # Initialize the figure
        self.diagram = mrsd.Diagram(
            self.axes, [RF_TITLE, GSS_TITLE, GPE_TITLE, GFE_TITLE, SIGNAL_TITLE])
                
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
        self.abbreviation = params.get('abbreviation')
        self.axes.set_title(f"{self.name} ({self.abbreviation})")
        
        # Gradients Axis
        self.ssAxis = params.get('ssAxis')
        self.peAxis = params.get('peAxis')
        self.feAxis = params.get('feAxis')

        # Intervals
        self.TR = params.get('TR')
        self.TE = params.get('TE')

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
            self.add_multi_gradient(multi_PE, GPE_TITLE)
        # Single PEs
        single_PEs = PEs.get('single')
        for single_PE in single_PEs:
            self.add_gradient(single_PE, GPE_TITLE)

        #################### FE ####################
        # Single PEs
        FEs = components.get('FE')
        for FE in FEs:
            self.add_gradient(FE, GFE_TITLE)

        #################### Spoiler ####################
        spoilers = components.get('spoiler')
        for spoiler in spoilers:
            self.add_spoiler(spoiler, GPE_TITLE)
            
        #################### readout/Signal ####################
        readout = components.get('readout')
        # Readout Parameters
        trajectory = readout.get('trajectory')
        if trajectory == "Cartesian":
            # TODO: Draw Cartesian
            pass
        elif trajectory == "Radial":
            # TODO: Draw Radial
            pass
        elif trajectory == "Spiral":
            # TODO: Draw Spiral
            pass
        
        signals = readout.get('signals')
        for signal in signals:
            self.add_RO(signal)

        self.orderSequenceBasedOnTime()
        self.draw()
     
    # Clear figure
    def clearData(self):
        super().clearData()
        self.timeBasedSequence = list()
        self.diagram = mrsd.Diagram(
            self.axes, [RF_TITLE, GSS_TITLE, GPE_TITLE, GFE_TITLE, SIGNAL_TITLE])

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
        rf_pulse, gradient = self.diagram.selective_pulse(RF_TITLE, 
                                                          GSS_TITLE, 
                                                          duration=duration, 
                                                          pulse_amplitude=flip_angle_rad, 
                                                          center=time, 
                                                          gradient_amplitude=flip_angle_rad/2)
        self.diagram.annotate(RF_TITLE, x=rf_pulse.end, y=0.2, text=rf"$\alpha$={flip_angle}")

        # Add to time based sequence
        RF_dict = (time, RF_PULSE, duration, flip_angle)
        self.timeBasedSequence.append(RF_dict)

        return rf_pulse, gradient

    # Add gradient
    def add_gradient(self, gradient, loc):
        time = self.read_time(gradient)
        step = gradient.get('step')
        sign = gradient.get('sign')
        duration = gradient.get('duration')
        
        self.diagram.gradient(loc, duration, step/2, duration, center=time)

        # Add to time based sequence
        if loc == GPE_TITLE:
            gradient_dict = (time, PE_GRADIENT, duration, step, sign)
        elif loc == GFE_TITLE:
            gradient_dict = (time, FE_GRADIENT, duration, step, sign)

        self.timeBasedSequence.append(gradient_dict)

    # Add multi gradient
    def add_multi_gradient(self, gradient, loc):
        time = self.read_time(gradient)
        duration = gradient.get('duration')
        step = gradient.get('step')
        sign = gradient.get('sign')
        
        # Draw multi gradient and annotate        
        self.diagram.multi_gradient(loc, amplitude=0.65, flat_top=self.TR/10, center = time)
        if sign == True:
            self.diagram.annotate(loc, time, 0.9, r"$\uparrow$" )
        else:
            self.diagram.annotate(loc, time, 0.9, r"$\downarrow$" )

        # Add to time based sequence
        pe_multi_dict = (time, PE_MULTI_GRADIENT, duration, step, sign)
        self.timeBasedSequence.append(pe_multi_dict)

    # Add readout
    def add_RO(self, signal):
        time = self.read_time(signal)
        duration = signal.get('duration')
        adc, echo, readout = self.diagram.readout(SIGNAL_TITLE, GFE_TITLE, duration, ramp=0, center=self.TE+1/2*duration, gradient_amplitude=0.5)
        
        # Add to time based sequence
        readout_dict = (time, READOUT, 0)
        self.timeBasedSequence.append(readout_dict)

    # Add intervals
    def add_intervals(self):
        if self.TE != 0 :
            self.diagram.interval(0, self.TE, -0.5, "TE")
        if self.TR != 0 :
            self.diagram.interval(0, self.TR, -1.0, "TR")
    
    # Add Spoiler
    def add_spoiler(self, spoiler, loc):
        time = self.read_time(spoiler)
        duration = spoiler.get('duration')
        
        # Draw spoiler         
        self.diagram.gaussian_pulse(loc, amplitude=1, duration=duration, center=time)
 
        # Add to time based sequence
        spoiler_dict = (time, SPOILER, 0)
        self.timeBasedSequence.append(spoiler_dict)
       
    # Read time
    def read_time(self, item):
        time = str(item.get('time'))
        time = eval(time,
                    {}, 
                    {"TE": self.TE, "TR": self.TR})
        
        return time
    
    # Set Sequence Based On time
    def orderSequenceBasedOnTime(self):
        def get_time(comp):
            return comp[0]

        # Sort the sequence based on time
        self.timeBasedSequence.sort(reverse=False, key=get_time)
        
        # Add relaxation
        relaxationList = []
        for i, item in enumerate(self.timeBasedSequence):
            if i < len(self.timeBasedSequence)-1:
                duration = self.timeBasedSequence[i+1][0] - (self.timeBasedSequence[i][0] + self.timeBasedSequence[i][2])
                if duration > 0:
                    time = self.timeBasedSequence[i][0]
                    relaxationList.append((time, RELAXATION, duration))
        self.timeBasedSequence.extend(relaxationList)

        self.timeBasedSequence.sort(reverse=False, key=get_time)
        
        # Add relaxation at the end
        duration = self.TR-self.timeBasedSequence[-1][0]
        if duration > 0:
            self.timeBasedSequence.append((self.timeBasedSequence[-1][0], RELAXATION, duration))

    # Get Sequence Based On time
    def getSequenceBasedOnTime(self):
        return self.timeBasedSequence
    
    # Reset figure and variables
    def reset(self):
        super().reset()