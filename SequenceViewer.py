""" Sequence Viewer Class"""

# math & matrix computations library
import numpy as np
import math

# MRI Sequence Diagram Library
import mrsd

# Json library
import json

# Viewer
from viewer import viewer

RF_PULSE = "RF"
RELAXATION = "RELAXATION"
READOUT = "READOUT"
GRADIENT = "GRADIENT"
MULTI_GRADIENT = "MULTI_GRADIENT"

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
        
        # Initialize the figure
        self.diagram = mrsd.Diagram(
            self.axes, ["RF", "$G_{SS}$", "$G_{PE}$", "$G_{FE}$", "Signal"])
                
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
            self.setSequenceBasedOnTime(params) # Set Sequence List Based On time

        #################### Update the parameters with JSON data ####################
        TE = params.get('TE')
        TR = params.get('TR')
        
        #################### readout/Signal ####################
        readout = params['readout']
        
        # readout parameters
        duration = readout.get('duration')
        axis = readout.get('axis')
        if duration:
            adc, echo, readout = self.diagram.readout(
                "Signal", "$G_{FE}$", duration, ramp=0.2, center=TE,
                adc_kwargs={"ec": "0.5"})
            self.diagram.add("$G_{FE}$", readout.adapt(2, -0.5, 0.2, end=readout.begin))
            
        #################### RF ####################
        RFs = params['RF']
        for RF in RFs:
            rf_pulse, gradient = self.add_RF(self.diagram, RF, TE, TR)
        
        #################### Gradient ####################
        gradients = params['gradient']
        for gradient in gradients:
            self.add_gradient(self.diagram, gradient)
            
        ################# Multi gradient #################
        multi_gradients = params['multi_gradient']
        for gradient in multi_gradients:
            self.add_multi_gradient(self.diagram, gradient)

        ################# Add Intervals #################
        self.add_intervals(self.diagram, TE, TR)

        self.draw()
    
    # Clear figure
    def clearData(self):
        super().clearData()
        self.timeBasedSequence = list()
        self.diagram = mrsd.Diagram(
            self.axes, ["RF", "$G_{SS}$", "$G_{PE}$", "$G_{FE}$", "Signal"])

    ###############################################
    """Sequence Functions"""
    ###############################################

    # Add RF
    def add_RF(self, diagram:mrsd.Diagram, RF, TE=0, TR=0):
        flip_angle = RF.get('flip_angle')
        flip_angle_rad = math.radians(flip_angle)
        start_time = eval(str(RF.get('time')), {}, {"TE": TE, "TR": TR})
        duration = RF.get('duration')
        rf_pulse, gradient = diagram.selective_pulse("RF", "$G_{SS}$", duration=duration, pulse_amplitude=flip_angle_rad, center=start_time)
        diagram.annotate("RF", x=rf_pulse.end, y=2, text=rf"$\alpha$={flip_angle}" )

        return rf_pulse, gradient

    # Add gradient
    def add_gradient(self, diagram:mrsd.Diagram, gradient):
        time = gradient.get('time')
        amplitude = gradient.get('amplitude')
        duration = gradient.get('duration')
        axis = gradient.get('axis')
        if (axis == "y"):
            diagram.gradient("$G_{PE}$", duration, amplitude, center=time)
        elif (axis == "x"):
            diagram.gradient("$G_{FE}$", duration, amplitude, center=time)
        elif (axis == "z"):
            diagram.gradient("$G_{SS}$", duration, amplitude, center=time)

    # Add multi gradient
    def add_multi_gradient(self, diagram:mrsd.Diagram, gradient):
        time = gradient.get('time')
        axis = gradient.get('axis')
        sign = gradient.get('sign')
        if (axis == "y"):
            gradient_loc = "$G_{PE}$"
        elif (axis == "x"):
            gradient_loc = "$G_{FE}$"
        elif (axis == "z"):
            gradient_loc = "$G_{SS}$"
        
        diagram.multi_gradient(gradient_loc, 1.75, 0.75, 0.1, center = time)
        if sign == True:
            diagram.annotate(gradient_loc, time-1.75, 0.5, r"$\uparrow$" )
        else:
            diagram.annotate(gradient_loc, time-1.75, 0.5, r"$\downarrow$" )


    # Add RF
    def add_intervals(self, diagram:mrsd.Diagram, TE=0, TR=0):
        if TE != 0 :
            diagram.interval(0, TE, -1.0, "TE")
        if TR != 0 :
            diagram.interval(0, TR, -2.0, "TR")
    
    # Set Sequence Based On time
    def setSequenceBasedOnTime(self, sequence):
        # Get parameters
        RF = sequence['RF']
        gradient = sequence['gradient']
        multi_gradient = sequence['multi_gradient']
        TE = sequence['TE']
        TR = sequence['TR']

        # RF
        for item in RF:
            time = eval(str(item.get('time')), {}, {"TE": TE, "TR": TR})
            duration = item.get('duration')
            flip_angle = item.get("flip_angle")
            self.timeBasedSequence.append((time, RF_PULSE, duration, flip_angle))
        
        # Gradient
        for item in gradient:
            time = item.get('time')
            duration = item.get('duration')
            amplitude = item.get("amplitude")
            axis = item.get('axis')
            self.timeBasedSequence.append((time, GRADIENT, duration, amplitude, axis))
        
        # Multi Gradient
        for item in multi_gradient:
            time = item.get('time')
            axis = item.get('axis')
            sign = item.get('sign')
            self.timeBasedSequence.append((time, MULTI_GRADIENT, axis, sign))

        self.timeBasedSequence.append((TE, READOUT))

        relaxationList = []
        for i, item in enumerate(self.timeBasedSequence):
            if i < len(self.timeBasedSequence)-1:
                duration = self.timeBasedSequence[i+1][0] - self.timeBasedSequence[i][0]
                if duration != 0:
                    time = self.timeBasedSequence[i][0]
                    relaxationList.append((time, RELAXATION, duration))
                    
        self.timeBasedSequence.extend(relaxationList)
                
        def gettime(comp):
            return comp[0]

        self.timeBasedSequence.sort(reverse=False, key=gettime)

    # Get Sequence Based On time
    def getSequenceBasedOnTime(self):
        return self.timeBasedSequence
    
    # Reset figure and variables
    def reset(self):
        super().reset()