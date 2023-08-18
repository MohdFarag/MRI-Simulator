# Purpose: Component class for the simulation of MRI sequences

class Component:
    def __init__(self, time, duration):
        self.time = time
        self.duration = duration

    def __repr__(self):
        return f"{Component.__name__} t={self.time}ms duration={self.duration}ms"
        
    def get_time(self):
        return self.time

        
# Radio frequency pulse component
class RFComponent(Component):
    def __init__(self, time, duration, angle):
        super().__init__(time, duration)
        self.angle = angle

    def __repr__(self):
        return f"RF t={self.time}ms duration={self.duration}ms angle={self.angle}°"


# Relaxation component
class RelaxationComponent(Component):
    def __init__(self, time, duration):
        super().__init__(time, duration)

    def __repr__(self):
        return f"Relaxation t={self.time}ms duration={self.duration}ms"


# Multi gradient component
class MultiGradientComponent(Component):
    def __init__(self, time, duration, sign, balanced=False):
        super().__init__(time, duration)
        self.sign = sign
        self.balanced = balanced

    def __repr__(self):
        return f"Multi Gradient t={self.time}ms duration={self.duration}ms"


# Gradient component        
class GradientComponent(Component):
    def __init__(self, time:float, duration:float, encoding:str, sign, balanced=False):
        super().__init__(time, duration)
        if encoding != "phase" and encoding != "frequency":
            raise ValueError("Encoding must be either phase or frequency")
        
        self.sign = sign        
        self.encoding = encoding
        self.balanced = balanced

    def __repr__(self):
        return f"{self.encoding} Gradient t={self.time}ms duration={self.duration}ms balanced={self.balanced}"
        

# Readout component
class ReadoutComponent(Component):
    def __init__(self, time, duration):
        super().__init__(time, duration)

    def __repr__(self):
        return f"Readout t={self.time}ms duration={self.duration}ms"
            

# Spoiler component
class SpoilerComponent(Component):
    def __init__(self, time, duration):
        super().__init__(time, duration)

    def __repr__(self):
        return f"Spoiler t={self.time}ms duration={self.duration}ms"
