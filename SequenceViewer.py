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
        self.sequenceTimeBased = list()
        self.setData("./temp/parameters.json")
        
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

    
    ###############################################
    """Sequence Functions"""
    ###############################################

    # Set image
    def setData(self, path:str):
        super().setData(path)

        #################### Read Json File ####################
        with open(path, 'r') as file:
            params = json.load(file)
            
        #################### Update the parameters with JSON data ####################
        TE = params.get('TE')
        TR = params.get('TR')
        
        diagram = mrsd.Diagram(
            self.axes, ["RF", "$G_{slice}$", "$G_{phase}$", "$G_{readout}$", "Signal"])

        #################### Readout/Signal ####################
        Readout = params['Readout']

        d_ramp = Readout.get('d_ramp')
        d_readout = Readout.get('d_readout')
        d_encoding = Readout.get('d_encoding')
        area_factor = Readout.get('area_factor')
        
        if d_ramp != 0:
            adc, echo, readout = diagram.readout(
                "Signal", "$G_{readout}$", d_readout, ramp = d_ramp, center=TE,
                adc_kwargs={"ec": "0.5"})
            diagram.add("$G_{readout}$", readout.adapt(d_encoding, -0.5, d_ramp, end=readout.begin))

        #################### RF ####################
        RFs = params['RF']
        slice_selection = None
        for RF in RFs:
            excitation, slice_selection = self.add_RF(diagram, RF, d_ramp)
        if slice_selection is not None:
            diagram.add("$G_{slice}$", slice_selection.adapt(d_encoding, area_factor, d_ramp, end=readout.begin))

        #################### Gradient ####################
        gradients = params['Gradient']
        for gradient in gradients:
            self.add_gradient(diagram, gradient)
            
        ################# Multi Gradient #################
        multi_gradients = params['Multi_gradient']
        for gradient in multi_gradients:
            self.add_multi_gradient(diagram, gradient, d_encoding, d_ramp)

        ################# Add Intervals #################
        # add flip angles and TE/TR intervals
        self.add_intervals(diagram, TE, TR)

        self.draw()
    
    # Add RF
    def add_RF(self, diagram:mrsd.Diagram, RF, d_ramp):
        FA = RF.get('FA')
        Flip_A = math.radians(FA)
        Time = RF.get('Time_start')
        Sign = RF.get('Sign')
        Duration = RF.get('Duration')
        excitation, slice_selection = diagram.selective_pulse("RF", "$G_{slice}$", duration=Duration, pulse_amplitude=Flip_A, ramp=d_ramp, center=Time)
        diagram.annotate("RF", excitation.center+0.5,2, r"$\alpha$ = " + str(Sign)+str(FA) )

        return excitation, slice_selection

    # Add gradient
    def add_gradient(self, diagram:mrsd.Diagram, gradient):
        Time = gradient.get('Time_start')
        Amp = gradient.get('Amp')
        Duration = gradient.get('Duration')
        if (gradient.get('Axis') == "y"):
            diagram.gradient("$G_{phase}$", Duration, Amp, center=Time)
        elif (gradient.get('Axis') == "x"):
            diagram.gradient("$G_{readout}$", Duration, Amp, center=Time)
        elif (gradient.get('Axis') == "z"):
            diagram.gradient("$G_{slice}$", Duration, Amp, center=Time)

    # Add multi gradient
    def add_multi_gradient(self, diagram:mrsd.Diagram, gradient, d_encoding, d_ramp):
        Time = gradient.get('Time_start')
        Amp = gradient.get('Amp')
        Duration = gradient.get('Duration')
        if (gradient.get('Axis') == "y"):
            diagram.multi_gradient("$G_{phase}$", d_encoding, 0.5, d_ramp, center = Time)
        elif (gradient.get('Axis') == "x"):
            diagram.multi_gradient("$G_{readout}$", d_encoding, 0.5, d_ramp, center = Time)
        elif (gradient.get('Axis') == "z"):
            diagram.multi_gradient("$G_{slice}$", d_encoding, 0.5, d_ramp, center = Time)

    # Add RF
    def add_intervals(self, diagram:mrsd.Diagram, TE=0, TR=0):
        if TE != 0 :
            diagram.interval(0, TE, -1.0, "TE")
        if TR != 0 :
            diagram.interval(0, TR, -2.0, "TR")
    
    # Reset figure and variables
    def reset(self):
        super().reset()
