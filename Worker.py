

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time


class Worker(QObject):    
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self._isRunning = True

    # Play the worker thread
    def play(self):
        if not self._isRunning :
            self._isRunning = True

        self.finished.emit()
    
    # Pause the worker thread        
    def pause(self):
        self._isRunning = False
