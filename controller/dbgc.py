# -*- coding:utf-8 -*-
import numpy
import math
from utils.mplcanvas import MplCanvas

from PySide import QtGui, QtCore
from controller import OnlineAnalyzerControllerBase as AnalyzerControllerBase
from ui.ui_debugcore import Ui_DebugCore

class DebugCoreCanvas():
    def __init__(self, wgt):
        self.tabMain = QtGui.QTabWidget(wgt)
        self.capTab = QtGui.QWidget()
        self.capCanvas = MplCanvas.setupCanvasWidget(self.capTab)
        capFigure = self.capCanvas.getFigure()
        self.capAx = capFigure.add_subplot(1, 1, 1)

        self.fftTab = QtGui.QWidget()
        self.fftCanvas = MplCanvas.setupCanvasWidget(self.fftTab)
        fftFigure = self.fftCanvas.getFigure()
        self.fftAx = fftFigure.add_subplot(1, 1, 1)

        self.tabMain.addTab(self.capTab, "capture")
        self.tabMain.addTab(self.fftTab, "fft")

        self.plotCap([], None)
        self.plotFFT([], None)

    def plotCap(self, dataY, pattern = None):
        if not pattern:
            pattern = ("", "", "", "")
        title, xlabel, ylabel, draw_type = pattern
        MplCanvas.changeInfo(self.capAx, title + "-CAP", xlabel, ylabel)
        MplCanvas.plotAx(self.capAx, range(len(dataY)), dataY, draw_type)

    def plotFFT(self, dataY, pattern = None):
        if not pattern:
            pattern = ("", "", "", "")
        title, xlabel, ylabel, draw_type = pattern
        MplCanvas.changeInfo(self.fftAx, title + "-FFT", xlabel, ylabel)
        MplCanvas.plotAx(self.fftAx, range(len(dataY)), dataY, draw_type)

    def draw(self):
        self.capCanvas.draw()
        self.fftCanvas.draw()

@AnalyzerControllerBase.bindUI(Ui_DebugCore)
@AnalyzerControllerBase.bindAnalyzer("debugcore")
class DebugCoreController(AnalyzerControllerBase):
    # funcName: (
    #           u"EventName",
    # Pattern for Cap
    #           (xLabel, yLable, drawType),
    # Pattern for FFT, if don't need FFT, this item should be None
    #           (xLabel, yLable, drawType))
    EventDict = {
        "rx_adc": (
            u"rx_adc",
            ("", "", ""),
            ("", "", "")
        ), "fgup_rx_adc": (
            u"rx_adc_fgup",
            ("", "", ""),
            ("", "", ""),
        ), "ldpc_err_rx_adc": (
            u"rx_adc_ldpc_err",
            ("", "", ""),
            ("", "", ""),
        ), "fg_dsm_rx_adc": (
            u"rx_adc_fg_dsm",
            ("", "", ""),
            ("", "", ""),
        ), "online_eye": (
            u"眼图",
            ("", "", "."),
            None
        ), "online_eye_error": (
            u"眼图(错误)",
            ("", "", "."),
            None
        ), "online_frequency": (
            u"频响",
            ("", "", ""),
            None
        ), "online_frequency_error": (
            u"频响(错误)",
            ("", "", ""),
            None
        ),
    }

    def __init__(self, **kw):
        AnalyzerControllerBase.__init__(self, **kw)
        # setup wgtCanvas
        self.canvas = DebugCoreCanvas(self.ui.dbgcCanvas)

        self.eventList = None # init with __genEventList
        self.funcDict = None  # init with __genEventList
        self.maxPoint = 8192
        self.dumpInfo = None
        self.fftInfo = None

        self.__genEventList()
        self.ui.dbgcEvents.clear()
        self.ui.dbgcEvents.addItems(self.eventList)
        self.__resetPoints()
    # ==================================
    # Setup & Inner Function
    # ==================================
    def __genEventList(self):
        funcList = self.analyzer.func_list()
        def transform(funcName):
            eventInfo = self.EventDict.get(funcName, None)
            if not eventInfo:
                return funcName
            else:
                return eventInfo[0]

        eventList = map(transform, funcList)
        self.funcDict = dict(zip(eventList, funcList))
        self.eventList = sorted(eventList)

    def __getCurrentPoints(self):
        return int(self.ui.dbgcPoint.text())

    def __getCurrentEventName(self):
        name = self.eventList[self.ui.dbgcEvents.currentIndex()]
        return self.funcDict[name]

    def __getCurrentEventInfo(self):
        eventName = self.__getCurrentEventName()
        emptyPattern = ("", "", "")
        return self.EventDict.get(eventName, ("", emptyPattern, emptyPattern))

    def __resetPoints(self):
        eventName = self.__getCurrentEventName()
        self.maxPoint = ("adc" in eventName) and 2048 or 8192
        self.ui.dbgcPoint.setText(str(self.maxPoint))
        self.__resetPrePoints()

    def __resetPrePoints(self):
        self.ui.dbgcPrepoint.clear()
        self.ui.dbgcPrepoint.setEnabled(False)
        self.ui.dbgcPrepointEn.setChecked(False)

    # return None or int
    # pre trigger point
    def __getCurrentPrePoint(self):
        if not self.ui.dbgcPrepointEn.isChecked():
            return None

        txt = str(self.ui.dbgcPrepoint.text())
        if not txt.isdigit():
            return None

        prePoint = int(txt)
        if prePoint >= self.maxPoint:
            return None

        return prePoing

    # ==================================
    # Event Callback
    # ==================================
    @QtCore.Slot(int)
    def on_dbgcEvents_activated(self, idx):
        if idx < 0:
            return

        eventName = self.eventList[idx]
        self.logStatus("idx %s = %s" % (idx, eventName))
        self.__resetPoints()

    @QtCore.Slot()
    def on_dbgcCap_clicked(self):
        # dump info
        points = self.__getCurrentPoints()
        prePoint = self.__getCurrentPrePoint()
        eventName = self.__getCurrentEventName()
        dumpInfo = self.analyzer.trigger_func(eventName, points, prePoint)

        if not dumpInfo:
            self.logStatus("Capture Fail")
            return
        else:
            self.logStatus("Capture Success")

        title, capPattern, fftPattern = self.__getCurrentEventInfo()

        # draw dump info
        capX, capY, capType = capPattern
        self.canvas.plotCap(dumpInfo, (title, capX, capY, capType))

        # draw fft
        if fftPattern:
            fftX, fftY, fftType = fftPattern
            fftInfo = self.analyzer.fft(dumpInfo)
            self.canvas.plotFFT(fftInfo, (title, fftX, fftY, fftType))
        else:
            fftInfo = []
            self.canvas.plotFFT([])

        self.canvas.draw()

        # info backup
        self.dumpInfo = dumpInfo
        self.fftInfo = fftInfo

    @QtCore.Slot(int)
    def on_dbgcPrepointEn_stateChanged(self, state):
        if state == 2: # checked
            self.ui.dbgcPrepoint.setEnabled(True)
            self.ui.dbgcPrepointEn.setChecked(True)
        else: # unchecked
            self.ui.dbgcPrepoint.setEnabled(False)
            self.ui.dbgcPrepointEn.setChecked(False)
