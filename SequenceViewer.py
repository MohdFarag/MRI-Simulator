""" Phantom Viewer Class"""

# pylint: disable=C0103, W0105, C0301, W0613, E1136

# math & matrix computations library
import numpy as np

import mrsd
import math
import json

from viewer import viewer

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
            self.axes, ["RF", "$G_{SS}$", "$G_{PE}$", "$G_{FE}$", "Echo signal"])
        
        self.setData("./Tests/parametersTest2.json")
        
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
        TE = params.get('TE')
        TR = params.get('TR')
        
        #################### Readout/Signal ####################
        Readout = params['Readout']
        
        # Readout parameters
        duration = Readout.get('Duration')
        if duration:
            adc, echo, readout = self.diagram.readout(
                "Echo signal", "$G_{FE}$", duration, ramp=0.2, center=TE,
                adc_kwargs={"ec": "0.5"})
            self.diagram.add("$G_{FE}$", readout.adapt(2, -0.5, 0.2, end=readout.begin))
            
        #################### RF ####################
        RFs = params['RF']
        for RF in RFs:
            rf_pulse, gradient = self.add_RF(self.diagram, RF)
        
        #################### Gradient ####################
        gradients = params['Gradient']
        for gradient in gradients:
            self.add_gradient(self.diagram, gradient)
            
        ################# Multi Gradient #################
        multi_gradients = params['Multi_gradient']
        for gradient in multi_gradients:
            self.add_multi_gradient(self.diagram, gradient)

        ################# Add Intervals #################
        # add flip angles and TE/TR intervals
        self.add_intervals(self.diagram, TE, TR)

        self.draw()
    
    # Clear figure
    def clearData(self):
        super().clearData()
        self.timeBasedSequence = list()
        self.diagram = mrsd.Diagram(
            self.axes, ["RF", "$G_{SS}$", "$G_{PE}$", "$G_{FE}$", "Echo signal"])

    ###############################################
    """Sequence Functions"""
    ###############################################

    # Add RF
    def add_RF(self, diagram:mrsd.Diagram, RF):
        FA = RF.get('FA')
        flip_angle = math.radians(FA)
        start_time = RF.get('Time')
        sign = RF.get('Sign')
        duration = RF.get('Duration')
        rf_pulse, gradient = diagram.selective_pulse("RF", "$G_{SS}$", duration=duration, pulse_amplitude=flip_angle, center=start_time)
        diagram.annotate("RF", x=rf_pulse.end, y=2, text=rf"$\alpha$={sign}{FA}" )

        return rf_pulse, gradient

    # Add gradient
    def add_gradient(self, diagram:mrsd.Diagram, gradient):
        time = gradient.get('Time')
        amplitude = gradient.get('Amp')
        duration = gradient.get('Duration')
        axis = gradient.get('Axis')
        if (axis == "y"):
            diagram.gradient("$G_{PE}$", duration, amplitude, center=time)
            self.timeBasedSequence.append(("Gy", time))
        elif (axis == "x"):
            diagram.gradient("$G_{FE}$", duration, amplitude, center=time)
            self.timeBasedSequence.append(("Gx", time))
        elif (axis == "z"):
            diagram.gradient("$G_{SS}$", duration, amplitude, center=time)
            self.timeBasedSequence.append(("Gz", time))

    # Add multi gradient
    def add_multi_gradient(self, diagram:mrsd.Diagram, gradient):
        Time = gradient.get('Time')
        Amp = gradient.get('Amp')
        axis = gradient.get('Axis')
        if (axis == "y"):
            diagram.multi_gradient("$G_{PE}$", 1.75, 0.75, 0.1, center = Time)
            self.timeBasedSequence.append(("multi Gy", Time))
        elif (axis == "x"):
            diagram.multi_gradient("$G_{FE}$", 1.75, 0.75, 0.1, center = Time)
            self.timeBasedSequence.append(("multi Gx", Time))
        elif (axis == "z"):
            diagram.multi_gradient("$G_{SS}$", 1.75, 0.75, 0.1, center = Time)
            self.timeBasedSequence.append(("multi Gz", Time))

    # Add RF
    def add_intervals(self, diagram:mrsd.Diagram, TE=0, TR=0):
        if TE != 0 :
            diagram.interval(0, TE, -1.0, "TE")
        if TR != 0 :
            diagram.interval(0, TR, -2.0, "TR")
            
    def getSequenceBasedOnTime(self):
        return self.timeBasedSequence
    
    # Reset figure and variables
    def reset(self):
        super().reset()