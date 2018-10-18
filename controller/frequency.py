# -*- coding:utf-8 -*-
from controller import OnlineAnalyzerControllerBase as OnlineAnalyzer
from controller import OfflineAnalyzerControllerBase as OfflineAnalyzer
from PySide import QtGui, QtCore
from PySide.QtGui import QFileDialog
from ui.ui_frequency import Ui_Frequency

import os
import numpy
import math
from utils.mplcanvas import MplCanvas

class FreqCanvas(MplCanvas):
    def __init__(self):
        MplCanvas.__init__(self)
        figure = self.getFigure()
        self.freqAx = figure.add_subplot(1, 1, 1)
        self.clearFreq()

    def plotFreq(self, adc,  bw, fc):
        def yTransfer(x):
            if x < xMin:
                return 0
            elif x > xMax:
                return 0
            return 1

        def drawLine(x, y, info, align = "center"):
            linePattern = (-0.0, 1.0, "k", "dashdot")
            ax.vlines(x, *linePattern)
            ax.text(x, y, info, horizontalalignment=align)

        ax = self.freqAx
        ax.cla()
        ax.relim()
        ax.autoscale_view()

        xMin = fc - (bw / 2)
        xMax = fc + (bw / 2)

        halfAdc = adc / 2
        ax.set_xlim(0, halfAdc + 10)
        ax.set_ylim(-1, 2)
        ax.set_xlabel("Frequency(MHz)")

        xData = numpy.arange(0, halfAdc, 0.01)

        yData = map(yTransfer, xData)
        ax.plot(xData, yData, ".")

        ax.vlines(fc, 0, 1.5, "k", "dashdot")
        ax.text(fc, 1.5, "fc %.2f, bw %.2f" % (fc, bw), horizontalalignment='center')

        drawLine(xMin, -0.5, "Min: %.2f" % xMin, "right")
        drawLine(xMax, -0.5, "Max: %.2f" % xMax, "left")
        drawLine(adc / 2, 1.5, "adc/2 %.2f" % halfAdc)

        self.draw()

    def clearFreq(self):
        self.freqAx.cla()
        self.draw()

class FreqControllerBase(object):
    def __init__(self):
        self.pllList = None
        self.adcList = None
        self.plladcList = None
        self.bwList = None
        self.fcList = None

        # has box fullBW
        self.__fullBWEnable = False
        # has box pll & box adc
        self.__pllAndAdcEnable = False

    def __resultToStr(self, component, frObject, inputList = True):
        if inputList:
            frList = frObject or []
        else:
            frList = [frObject] if frObject else []

        strList = []
        if component == "fullBW":
            def trans(adc):
                value = adc.get_val()
                return "%.2f" % self.analyzer._calc_bw(value, 1)

            for pll, adc in frList:
                if adc: strList.append(trans(adc))
        elif component == "bw":
            strList += [str(bw.get_opt()) for bw in frList]
        else:
            strList += map(str, frList)

        if not inputList:
            try:
                return strList[0]
            except IndexError:
                return str(None)

        nameDict = {
            "fullBW": "Bandwidth",
            "pll": "fpll",
            "adc": "fadc",
            "bw": "Division Ratio",
            "fc": "FC",
        }

        strList.insert(0, nameDict[component])
        return strList

    def __reflashBox(self, component):
        analyzer = self.analyzer
        if component == "pll":
            freqList = analyzer.list_pll()
            box = self.ui.freqPLL
            res = analyzer.get_pll()
            self.pllList = freqList
        elif component == "adc":
            freqList = analyzer.list_adc_clock()
            box = self.ui.freqADC
            res = analyzer.get_adc_clock()
            self.adcList = freqList
        elif component == "bw":
            freqList = analyzer.list_bandwidth()
            box = self.ui.freqBW
            res = analyzer.get_bandwidth()
            self.bwList = freqList
        elif component == "fc":
            freqList = analyzer.list_cent_freq()
            box = self.ui.freqFC
            res = analyzer.get_cent_freq()
            self.fcList = freqList
        elif component == "fullBW":
            freqList = analyzer.list_adc_clock_all()
            box = self.ui.freqFullBW
            res = (analyzer.get_pll(), analyzer.get_adc_clock())
            self.plladcList = freqList
        else:
            print("error component: %s in __reflashBox" % component)
            return

        box.clear()
        box.addItems(self.__resultToStr(component, freqList))
        resStr = self.__resultToStr(component, res, inputList = False)
        idx = box.findText(resStr)
        if idx < 0:
            idx = 0
        box.setCurrentIndex(idx)

    def __drawFreq(self, fillAll, adc, bw, fc):
        if not self.canvas: return

        if fillAll:
            self.canvas.plotFreq(float(adc), float(bw), float(fc))
        else:
            self.canvas.clearFreq()

    @staticmethod
    def __tofloat(value):
      try:
        return float(value)
      except ValueError:
        return None

    def _getADC(self):
        if self.__fullBWEnable:
            idx = self.ui.freqFullBW.currentIndex()
            if idx <= 0:
                return None
            _, adc = self.plladcList[idx - 1]
            txt = str(adc)
        else: # __pllAndAdcEnable
            txt = self.ui.freqADC.currentText()

        return self.__tofloat(txt)

    def _getBW(self):
        idx = self.ui.freqBW.currentIndex()
        if idx <= 0:
            return None
        txt = str(self.bwList[idx - 1])
        return self.__tofloat(txt)

    def _getFC(self):
        txt = self.ui.freqFC.currentText()
        return self.__tofloat(txt)

    def _isFillAll(self):
        bw = self._getBW()
        fc = self._getFC()
        return bool(bw and fc)

    def _setPLLADC(self, plladc):
        analyzer = self.analyzer
        pll, adc = plladc
        analyzer.set_pll(pll)
        analyzer.set_adc_clock(adc)

    def _reflash(self):
        if self.__pllAndAdcEnable:
            self.__reflashBox("pll")
            self.__reflashBox("adc")

        if self.__fullBWEnable:
            self.__reflashBox("fullBW")

        self.__reflashBox("bw")
        self.__reflashBox("fc")

        fillAll = self._isFillAll()
        adc = self._getADC()
        bw = self._getBW()
        fc = self._getFC()
        self.__drawFreq(fillAll, adc, bw, fc)
        freqSave = getattr(self.ui, "freqSave")
        if freqSave: freqSave.setEnabled(fillAll)

        freqRange = getattr(self.ui, "freqRange")
        if freqRange:
            fl, fh = self.analyzer.get_range()
            if None in (fl, fh):
                info = ""
            else:
                info = "L:%.2f; H:%.2f;" % (fl, fh)
            freqRange.setText(info)

    def __boxAcivated(self, component, idx):
        # prepare component map
        analyzer = self.analyzer
        cMap = {"pll":("pllList", analyzer.set_pll),
                "adc":("adcList", analyzer.set_adc_clock),
                "bw" :("bwList",  analyzer.set_bandwitdth),
                "fc" :("fcList",  analyzer.set_cent_freq),
                "fullBW":("plladcList", self._setPLLADC),
                }

        listName, setter = cMap[component]
        freqList = getattr(self, listName)
        if idx <= 0 or not freqList:
            return
        res = freqList[idx - 1]
        setter(res)
        self._reflash()

    # ==================================
    # Event Callback
    # ==================================
    def on_freqPLL_activated(self, idx):
        self.__boxAcivated("pll", idx)

    def on_freqADC_activated(self, idx):
        self.__boxAcivated("adc", idx)

    def on_freqFullBW_activated(self, idx):
        self.__boxAcivated("fullBW", idx)

    def on_freqFC_activated(self, idx):
        self.__boxAcivated("fc", idx)

    def on_freqBW_activated(self, idx):
        self.__boxAcivated("bw", idx)

    def on_freqSave_clicked(self):
        mainWindow = self._mainWindow
        info = "Save Band Config"
        path = str(QFileDialog.getSaveFileName(mainWindow, info, os.curdir)[0])
        print(path)
        res = self.analyzer.save_frequency(path)
        self.logStatus("freq save to %s: %s" % (path, res and "success" or "fail"))

    def on_freqLoad_clicked(self):
        mainWindow = self._mainWindow
        info = "Load Band Config"
        path = str(QFileDialog.getOpenFileName(mainWindow, info, os.curdir)[0])
        res = self.analyzer.load_frequency(path)
        self.logStatus("freq load from %s: %s" % (path, res and "success" or "fail"))
        self._reflash()

    def _setupEvent(self):
        # detect ui
        ui = self.ui
        if getattr(ui, "freqFullBW", None):
            self.__fullBWEnable = True

        if getattr(ui, "freqPLL", None) and getattr(ui, "freqADC", None):
            self.__pllAndAdcEnable = True

        if not (self.__pllAndAdcEnable or self.__fullBWEnable):
            raise Exception("Error: not found fullBW or (pll and adc)")

        if self.__pllAndAdcEnable:
            ui.freqPLL.activated.connect(self.on_freqPLL_activated)
            ui.freqADC.activated.connect(self.on_freqADC_activated)
        if self.__fullBWEnable:
            ui.freqFullBW.activated.connect(self.on_freqFullBW_activated)
        ui.freqFC.activated.connect(self.on_freqFC_activated)
        ui.freqBW.activated.connect(self.on_freqBW_activated)

        ui.freqSave.clicked.connect(self.on_freqSave_clicked)
        ui.freqLoad.clicked.connect(self.on_freqLoad_clicked)

@OnlineAnalyzer.bindUI(Ui_Frequency)
@OnlineAnalyzer.bindAnalyzer("frequency")
class OnlineFreqController(FreqControllerBase, OnlineAnalyzer):
    def __init__(self, **kw):
        FreqControllerBase.__init__(self)
        OnlineAnalyzer.__init__(self, **kw)
        if self.ui.freqCanvas:
            self.canvas = FreqCanvas.setupCanvasWidget(self.ui.freqCanvas)
        else:
            self.canvas = None

        self._setupEvent()
        self._reflash()

    def _setControllerEnabled(self, enable):
        self.ui.freqApply.setEnabled(enable)
        self.ui.freqGet.setEnabled(enable)

    def _setupEvent(self):
        FreqControllerBase._setupEvent(self)
        self.ui.freqGet.clicked.connect(self.on_freqGet_clicked)
        self.ui.freqApply.clicked.connect(self.on_freqApply_clicked)

    def on_freqGet_clicked(self):
        if not self.analyzer.get_online_frequency():
            self.logStatus("online freq config: fail")
            return

        self.logStatus("online freq config: success")
        self._reflash()

    def on_freqApply_clicked(self):
        # TODO env bakup
        if self.analyzer.apply_frequency():
            result = "apply freq config: success"
        else:
            result = "apply freq config: success"

        self.logStatus(result)
