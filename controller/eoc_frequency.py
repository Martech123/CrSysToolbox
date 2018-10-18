import functools
from PySide import QtGui, QtCore
from PySide.QtGui import QTabWidget

from controller import OfflineAnalyzerControllerBase as OfflineAnalyzer
from frequency import FreqControllerBase
from ui.ui_eoc_frequency import Ui_EocFreq

@OfflineAnalyzer.bindUI(Ui_EocFreq)
@OfflineAnalyzer.bindAnalyzer("frequency")
class EocFreqController(FreqControllerBase, OfflineAnalyzer):
    def __init__(self, **kw):
        FreqControllerBase.__init__(self)
        OfflineAnalyzer.__init__(self, **kw)
        self.canvas = None
        self._idx = None
        self._restoreFunc = None

        self._setupEvent()
        self._reflash()

    def setReg(self, a08, a13, a15, of9):
        self.analyzer.set_offline_frequency(a08, a13, a15, of9)
        self._reflash()

    def getReg(self):
        return self.analyzer.dump_registers()

    def getRange(self):
        bw = self.ui.freqBW.currentText()
        fc = self.ui.freqFC.currentText()
        if bw.isalpha() or fc.isalpha():
            return (None, None)

        bw = float(bw)
        fc = float(fc)

        xMin = fc - (bw / 2)
        xMax = fc + (bw / 2)
        return (xMin, xMax)

    def _setupEvent(self):
        FreqControllerBase._setupEvent(self)
        self.ui.freqLog.clicked.connect(self.on_freqLog_clicked)
        self.ui.freqRestore.clicked.connect(self.on_freqRestor_clicked)

    def setupIdx(self, idx):
        self._idx = idx

    def setupRestoreCallback(self, func):
        '''
        func(idx)
        return (*regList)
        '''
        if not self._idx: return False
        self._restoreFunc = functools.partial(func, self._idx)
        return True

    def on_freqRestor_clicked(self):
        if not self._restoreFunc:
            self.logStatus("freq restore unimplemented")
            return

        regList = self._restoreFunc()
        self.setReg(*regList)

    def on_freqLog_clicked(self):
        bw = self.ui.freqBW.currentText()
        fc = self.ui.freqFC.currentText()
        if bw.isalpha() or fc.isalpha():
            self.logStatus("please fill all config")
            return

        regList = map(lambda h: "0x%04x" % (h), self.getReg())
        rangeOri = self.getRange()
        rangeInt = map(int, rangeOri)
        rangeFloat = map(str, rangeOri)
        rangeList = zip(rangeFloat, rangeInt)


        oneline = "band{idx}: range{r}, a08:{} a13:{} a15:{} of9:{}"
        self.logStatus(oneline.format(idx = self._idx, r = rangeList, *regList))

class EocFreqWrapper(QTabWidget):
    def __init__(self, main, parent = None) :
        QTabWidget.__init__(self, parent = parent)
        self.main = main
        self.parent = parent
        self._restoreFunc = None

        self.setupUi()

    def setupUi(self):
        self.parent.resize(900, 100)
        self.resize(850, 80)
        self.setObjectName("tabFreq")

    def setupRestoreCallback(self, func):
        '''
        func(idx)
        return (*regList)
        '''
        self._restoreFunc = func

    def reloadFreq(self, regsList):
        self.clear()
        self._freqCtlList = []
        for i, regs in enumerate(regsList):
            freqCtl = EocFreqController(main = self.main)
            freqCtl.setupIdx(i)
            freqCtl.setReg(*regs)
            self.addTab(freqCtl, "Band %d" % i)

            # register restor callback
            if self._restoreFunc: freqCtl.setupRestoreCallback(self._restoreFunc)
            self._freqCtlList.append(freqCtl)

    def dumpRegister(self):
        return [freqCtl.getReg() for freqCtl in self._freqCtlList]

    def dumpRange(self):
        return [freqCtl.getRange() for freqCtl in self._freqCtlList]

    def setError(self, errInfo):
        self.clear()
        errorLabel = QtGui.QLabel("<font color=red size=40> %s </font>" % errInfo)
        self.addTab(errorLabel, "error info")
