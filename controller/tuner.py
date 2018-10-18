from controller import OnlineAnalyzerControllerBase as AnalyzerControllerBase
from tuner_register import TunerRegisterController
from PySide import QtGui, QtCore
from PySide.QtCore import QRegExp
from PySide.QtGui import QRegExpValidator
from utils.thread import SimpleThread
from ui.ui_tuner import Ui_Tuner

@AnalyzerControllerBase.bindUI(Ui_Tuner)
@AnalyzerControllerBase.bindAnalyzer("tuner")
class TunerController(AnalyzerControllerBase):
    def __init__(self, **kw):
        AnalyzerControllerBase.__init__(self, **kw)

        self._pa1List = None
        self._rfvgaList = None
        self._lna1List = None
        self._lna2List = None
        self._loList = None
        self._lastLoList = None

        self._threadLOGet = SimpleThread()
        self._threadLOSet = SimpleThread()

        self._threadLOGet.registerCallback(self.__loGet)
        self._threadLOGet.finished.connect(self.__loGetFinished)
        self._threadLOGet.terminated.connect(self.__recoverAgent)

        self._threadLOSet.registerCallback(self.__loSet)
        self._threadLOSet.finished.connect(self.__recoverAgent)
        self._threadLOSet.terminated.connect(self.__recoverAgent)
        self.setupUI()

    @staticmethod
    def _dumpGainInfo(gainDict, reg = None):
        if reg is None:
            return [(reg, gain) for reg, gain in gainDict.iteritems()]

        try:
            return (reg, gainDict[reg])
        except KeyError:
            return None

    @staticmethod
    def _gainToStr(gainItem):
        '''
        gainItem: the item in _dumpGainInfo()
        '''
        reg, gain = gainItem
        return "Reg: %s, Gain: %.2f" % (bin(reg), gain)

    @staticmethod
    def _getFreqValidator():
        freqRegExp = QRegExp("^\\d*\.?\\d*[GgMm]?$")
        return QRegExpValidator(freqRegExp)

    @staticmethod
    def _translateFreq(freq):
        freq = str(freq).upper()

        base = 1
        if "G" in freq:
            freq = freq.replace("G", "")
            base = 1000
        else:
            freq = freq.replace("M", "")
            base = 1

        try:
            f = float(freq) * base
        except:
            f = None
        return f

    def setupUI(self):
        analyzer = self.analyzer
        # PA
        self._pa1List = self._dumpGainInfo(analyzer.GAIN_PA1)
        self._rfvgaList = self._dumpGainInfo(analyzer.GAIN_RFVGA)

        # LNA
        self._lna1List = self._dumpGainInfo(analyzer.GAIN_LNA1)
        self._lna2List = self._dumpGainInfo(analyzer.GAIN_LNA2)

        # LO
        self._loList = sorted(analyzer.list_lo(), key = lambda x: x.value)

        ui = self.ui
        # setup reg view
        regNum = 5
        TunerRegisterController(
                num = regNum,
                main = self.getMainWindow(),
                parent = ui.tunerReg)

        # setup PA
        ui.paPA1.clear()
        ui.paPA1.addItem("PA1")
        ui.paPA1.addItems(map(self._gainToStr, self._pa1List))

        ui.paRFVGA.clear()
        ui.paRFVGA.addItem("RFVGA")
        ui.paRFVGA.addItems(map(self._gainToStr, self._rfvgaList))
        self._reflashPA()

        # setup LNA
        ui.lnaLNA1.clear()
        ui.lnaLNA1.addItem("LNA1")
        ui.lnaLNA1.addItems(map(self._gainToStr, self._lna1List))

        ui.lnaLNA2.clear()
        ui.lnaLNA2.addItem("LNA2")
        ui.lnaLNA2.addItems(map(self._gainToStr, self._lna2List))
        self._reflashLNA()

        # setup LO
        freqVaildator = self._getFreqValidator()
        self.ui.loStart.setValidator(freqVaildator)
        self.ui.loEnd.setValidator(freqVaildator)
        self.on_loStartEn_stateChanged(0)
        self.on_loEndEn_stateChanged(0)
        self.on_loSearch_clicked()

    def _currentPAItem(self):
        pBox = self.ui.paPA1
        rBox = self.ui.paRFVGA
        pIdx = pBox.currentIndex() - 1
        rIdx = rBox.currentIndex() - 1

        if pIdx < 0 or rIdx < 0:
            return None

        pa1, _ = self._pa1List[pIdx]
        rfvga, _ = self._rfvgaList[rIdx]

        PA = self.analyzer.PA
        return PA(pa1 = pa1, rfvga = rfvga)

    def _currentLNAItem(self):
        l1Box = self.ui.lnaLNA1
        l2Box = self.ui.lnaLNA2
        l1Idx = l1Box.currentIndex() - 1
        l2Idx = l2Box.currentIndex() - 1

        if l1Idx < 0 or l2Idx < 0:
            return None

        lna1, _ = self._lna1List[l1Idx]
        lna2, _ = self._lna2List[l2Idx]

        LNA = self.analyzer.LNA
        return LNA(lna1 = lna1, lna2 = lna2)

    def _currentLOItem(self):
        loBox = self.ui.loFreq
        idx = loBox.currentIndex() - 1

        if idx < 0:
            return None
        else:
            return self._lastLoList[idx]

    def _findGainItem(self, gainList, gainItem):
        try:
            idx = gainList.index(gainItem) + 1
        except ValueError:
            idx = 0
        return idx

    def _getFreqStart(self):
        edit = self.ui.loStart
        if edit.isEnabled():
            return self._translateFreq(edit.text())
        return None

    def _getFreqEnd(self):
        edit = self.ui.loEnd
        if edit.isEnabled():
            return self._translateFreq(edit.text())
        return None

    def _reflashPA(self):
        infoEdit = self.ui.paInfo
        item = self._currentPAItem()
        if not item:
            infoEdit.setText("Total Gain")
        else:
            infoEdit.setText(str(item))

    def _reflashLNA(self):
        infoEdit = self.ui.lnaInfo
        item = self._currentLNAItem()
        if not item:
            infoEdit.setText("Total Gain")
        else:
            infoEdit.setText(str(item))

    def _reflashLO(self):
        loItem = self._currentLOItem()
        if not loItem: return

        nEdit = self.ui.loN
        divEdit = self.ui.loDiv
        infoEdit = self.ui.loInfo

        infoEdit.setText(str(loItem))
        nEdit.setText(str(loItem.n))
        divEdit.setText(str(self.analyzer.LO_DIV[loItem.div]))
        self.ui.tunerR0.setText("")
        self.ui.tunerR1.setText("")
        self.ui.tunerR2.setText("")

    def _reflashLOBox(self):
        loBox = self.ui.loFreq
        loBox.clear()
        loBox.addItem("LO")
        fs = self._getFreqStart()
        fe = self._getFreqEnd()
        self.logStatus("%sM --> %sM" %(fs or "0", fe or "inf"))

        loList = filter(
                lambda x: self.analyzer.between(fs, fe, x.value),
                self._loList)

        loBox.addItems(map(lambda x: "%.2f" % x.value, loList))
        self._lastLoList = loList

    def __loGet(self, thread):
        agentCtl = self.getAgentController()
        agentCtl.lockAgent()
        self.__lo = self.analyzer.get_lo()

    def __loGetFinished(self):
        self.__recoverAgent()
        lo = self.__lo
        if not lo:
            self.logStatus("Error, Get LO")
            return

        def locateLO():
            idx = self._lastLoList.index(lo)
            self.ui.loFreq.setCurrentIndex(idx + 1)

        # first try
        try:
            locateLO()
        except ValueError:
            # reset range
            self.on_loStartEn_stateChanged(0)
            self.on_loEndEn_stateChanged(0)
            self.on_loSearch_clicked()

            # try again
            locateLO()

        self._reflashLO()
        self.ui.tunerR0.setText(hex(lo.r0 & 0xff))
        self.ui.tunerR1.setText(hex(lo.r1 & 0xff))
        self.ui.tunerR2.setText(hex(lo.r2 & 0xff))

        self.logStatus("Get LO finished")

    def __loSet(self, thread):
        agentCtl = self.getAgentController()
        agentCtl.lockAgent()
        lo = self._currentLOItem()
        if not lo:
            self.logStatus("Error, please choose LO")
            return

        res = self.analyzer.set_lo(lo)
        self.logStatus("Set LO %s" % (res and "Success" or "fail"))

    def __recoverAgent(self):
        self.getAgentController().unlockAgent()

    @QtCore.Slot(int)
    def on_paPA1_activated(self, idx):
        self._reflashPA()

    @QtCore.Slot(int)
    def on_paRFVGA_activated(self, idx):
        self._reflashPA()

    @QtCore.Slot()
    def on_paGet_clicked(self):
        item  = self.analyzer.get_pa()
        pa1 = self._dumpGainInfo(self.analyzer.GAIN_PA1, item.pa1)
        rfvga = self._dumpGainInfo(self.analyzer.GAIN_RFVGA, item.rfvga)

        pIdx = self._findGainItem(self._pa1List, pa1)
        rIdx = self._findGainItem(self._rfvgaList, rfvga)
        if rIdx <= 0 or pIdx <= 0: self.logStatus("Sys Error pa Get")

        self.ui.paPA1.setCurrentIndex(pIdx)
        self.ui.paRFVGA.setCurrentIndex(rIdx)
        self._reflashPA()

    @QtCore.Slot()
    def on_paSet_clicked(self):
        item = self._currentPAItem()
        result = self.analyzer.set_pa(item)
        self.logStatus("PA set: %s" % result and "success" or "fail")

    @QtCore.Slot(int)
    def on_lnaLNA1_activated(self, idx):
        self._reflashLNA()

    @QtCore.Slot(int)
    def on_lnaLNA2_activated(self, idx):
        self._reflashLNA()

    @QtCore.Slot()
    def on_lnaGet_clicked(self):
        item  = self.analyzer.get_lna()
        lna1 = self._dumpGainInfo(self.analyzer.GAIN_LNA1, item.lna1)
        lna2 = self._dumpGainInfo(self.analyzer.GAIN_LNA2, item.lna2)

        l1Idx = self._findGainItem(self._lna1List, lna1)
        l2Idx = self._findGainItem(self._lna2List, lna2)
        if l1Idx <= 0 or l2Idx <= 0: self.logStatus("Sys Error lna Get")

        self.ui.lnaLNA1.setCurrentIndex(l1Idx)
        self.ui.lnaLNA2.setCurrentIndex(l2Idx)
        self._reflashLNA()

    @QtCore.Slot()
    def on_lnaSet_clicked(self):
        item = self._currentLNAItem()
        result = self.analyzer.set_lna(item)
        self.logStatus("LNA set: %s" % result and "success" or "fail")

    @QtCore.Slot(int)
    def on_loFreq_activated(self, idx):
        self._reflashLO()

    @QtCore.Slot()
    def on_loSearch_clicked(self):
        self._reflashLOBox()
        self._reflashLO()

    @QtCore.Slot(int)
    def on_loStartEn_stateChanged(self, state):
        if state == 2: # checked
            b = True
        else:
            b = False
        self.ui.loStartEn.setChecked(b)
        self.ui.loStart.setEnabled(b)

    @QtCore.Slot(int)
    def on_loEndEn_stateChanged(self, state):
        if state == 2: # checked
            b = True
        else:
            b = False
        self.ui.loEndEn.setChecked(b)
        self.ui.loEnd.setEnabled(b)

    @QtCore.Slot()
    def on_loGet_clicked(self):
        if not self._threadLOGet.isRunning():
            self._threadLOGet.start()
            self.logStatus("lo getting")
        else:
            self.logStatus("lo get, already running")

    @QtCore.Slot()
    def on_loSet_clicked(self):
        if not self._threadLOSet.isRunning():
            self._threadLOSet.start()
            self.logStatus("lo setting")
        else:
            self.logStatus("lo set, already running")
