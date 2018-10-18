from controller import OnlineAnalyzerControllerBase as AnalyzerControllerBase

from PySide import QtGui, QtCore
from utils.register import Register
from ui.ui_tuner_register import Ui_TunerRegister

@AnalyzerControllerBase.bindUI(Ui_TunerRegister)
@AnalyzerControllerBase.bindAnalyzer("tuner")
class TunerRegisterItem(AnalyzerControllerBase, Register):
    def __init__(self, **kw):
        AnalyzerControllerBase.__init__(self, **kw)

        Register.__init__(
            self,
            regLen  = 8,
            addrLen = 8,
            regAddr = self.ui.tunerAddr,
            regHex  = self.ui.tunerHex,
            regBin  = self.ui.tunerBin)

    # True --> success, False --> Fail; strInfo --> strInfo; Else --> inner error
    def setResult(self, value):
        if type(value) == bool:
            if value == False:
                result = "Fail"
            elif value == True:
                result = "Success"
        elif type(value) == str:
            result = value
        else:
            result = "Inner Error"
        self.ui.tunerResult.setText(result)

    @QtCore.Slot()
    def on_tunerHex_textChanged(self):
        self.regHexChanged()

    @QtCore.Slot()
    def on_tunerBin_textChanged(self):
        self.regBinChanged()

    @QtCore.Slot()
    def on_tunerGet_clicked(self):
        addr = self.getRegAddr()
        if addr is None:
            self.setResult("Err Addr")
            return

        reg = self.analyzer.tuner_get(addr)
        if reg is None:
            self.setResult(False)
            return
        self.setRegVal(reg)
        self.setResult(True)

    @QtCore.Slot()
    def on_tunerSet_clicked(self):
        addr = self.getRegAddr()
        if addr is None:
            self.setResult("Err Addr")
            return
        val  = self.getRegVal()
        if val is None:
            self.setResult("Err Val")
            return

        res = self.analyzer.tuner_set(addr, val)
        self.setResult(res is not None)

class TunerRegisterController(QtGui.QWidget):
    def __init__(self, main, num = 1, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.autoFillBackground()
        vbox = QtGui.QVBoxLayout()
        pos = parent.pos()
        xoff = pos.x()
        yoff = pos.y()
        for _ in range(num):
            item = TunerRegisterItem(main = main, parent = self)
            item.move(xoff, yoff)
            yoff += item.size().height()
