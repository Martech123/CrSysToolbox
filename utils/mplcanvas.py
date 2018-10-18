from PySide import QtGui, QtCore
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NacigationToolbar
from matplotlib.figure import *

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.__figure = Figure()
        FigureCanvas.__init__(self, self.__figure)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def getFigure(self):
        return self.__figure

    @staticmethod
    def plotAx(ax, datax, datay, draw_type = ""):
        ax.cla()
        ax.relim()
        ax.autoscale_view()
        ax.plot(datax, datay, draw_type)

    @staticmethod
    def changeInfo(ax, title = '', xlabel = '', ylabel = ''):
        ax.clear()
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    @classmethod
    def setupCanvasWidget(cls, wgtCanvas):
        canvas = cls()
        vbox = QtGui.QVBoxLayout()
        toolbar = NacigationToolbar(canvas, None)
        vbox.addWidget(toolbar)
        vbox.addWidget(canvas)
        wgtCanvas.setLayout(vbox)
        return canvas
