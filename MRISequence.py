from Component import *

CARTESIAN_TRAJECTORY = "Cartesian"
RADIAL_TRAJECTORY = "Radial"
SPIRAL_TRAJECTORY = "Spiral"

class MRISequence:
    def __init__(self):
        self.components = [] # List of components
        self.length = 0 # Number of components
        self.TR = 0 # Repetition Time
        self.TE = 0 # Echo Time
        self.trajectory = CARTESIAN_TRAJECTORY
        
    def __repr__(self):
        string = f"Sequence Length: {self.length}\n"
        string += f"TR: {self.TR}\n"
        string += f"TE: {self.TE}\n"
        string += f"Trajectory: {self.trajectory}\n"
        for component in self.components:
            string += f"{component}\n"
        
        return string

    def add_component(self, component):
        self.components.append(component)
        self.length += 1
    
    # Getters
    def get_components(self):
        return self.components
    
    def get_length(self):
        return self.length
    
    def get_TR(self):
        return self.TR
    
    def get_TE(self):
        return self.TE
    
    def get_trajectory(self):
        return self.trajectory
    
    # Setters
    def set_TR(self, TR):
        self.TR = TR
        
    def set_TE(self, TE):
        self.TE = TE
    
    def set_trajectory(self, trajectory):
        self.trajectory = trajectory
        
    # Sort
    def sort(self, by:str='time', reverse:bool=False):
        def get_time(component):
            return component.time
        
        def get_duration(component):
            return component.duration
        
        if by == 'time':
            self.components.sort(key=get_time, reverse=reverse)
        elif by == 'duration':
            self.components.sort(key=get_duration, reverse=reverse)
        else:
            raise Exception("Invalid sorting parameter")
        
    # Setup the sequence
    def setup(self, by:str='time', reverse:bool=False):
        # Add relaxations
        relaxations_list = []
        for i, _ in enumerate(self.components):
            if i < self.length-1:
                duration = self.components[i+1].time - (self.components[i].time + self.components[i].duration)
                if duration > 0:
                    time = self.components[i].time + self.components[i].duration
                    decay_component = RelaxationComponent(time, duration)
                    relaxations_list.append(decay_component)
        
        # Extend the relaxations components into main components list
        self.components.extend(relaxations_list)
        self.sort(by, reverse)
        self.add_relaxation_at_last()

    # Add relaxation at the end
    def add_relaxation_at_last(self):
        # Add relaxation at the end (TR - Last)
        duration = self.TR - self.components[-1].time
        if duration > 0:
            decay_component = RelaxationComponent(self.components[-1].time, duration)
            self.components.append(decay_component)