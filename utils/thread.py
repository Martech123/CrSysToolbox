from PySide import QtCore
from PySide.QtCore import QThread

class SimpleThread(QThread):
    def __init__(self, *args, **kw):
        QThread.__init__(self, *args, **kw)

        self.__cb = None

    def registerCallback(self, func):
        '''
        func(thread)
        '''
        self.__cb = func

    def run(self):
        self.__cb(self)
