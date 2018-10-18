from controller import OnlineAnalyzerControllerBase as AnalyzerControllerBase
from PySide import QtGui, QtCore
from ui.ui_register import Ui_Register

class RegItem(QtGui.QWidget):
    # widgetName: ("ColName", ColWidth),
    WidgetInfo = None
    # HEAD = (colName, colName, colName, ...)
    HEAD = None

    @classmethod
    def head(cls):
        widget = QtGui.QWidget()
        hbox = QtGui.QHBoxLayout()

        for col in cls.HEAD:
            hbox.addStretch(1)
            colName = cls.WidgetInfo[col][0]
            label = QtGui.QLabel(colName)
            cls._setWidgetWidth(label, col)
            hbox.addWidget(label)
        widget.setLayout(hbox)
        return widget

    @classmethod
    def _setWidgetWidth(cls, widget, widgetName):
        w = cls.WidgetInfo[widgetName][1]
        widget.setMaximumWidth(w)
        widget.setMinimumWidth(w)

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.ckEn = QtGui.QCheckBox()
        self.txtReg  = QtGui.QLineEdit()
        self.txtValH = QtGui.QLineEdit()
        self.txtValB = QtGui.QLineEdit()
        self.txtResult = QtGui.QLineEdit()
        self.btnRun = QtGui.QPushButton()
        self.btnFunc = QtGui.QPushButton()

        self.analyzer = None
        self.listEnCb = None

    def setupUI(self):
        self.ckEn.setText("En")
        self.btnRun.setText("Run")
        self.btnFunc.setText("Get")

        self.txtReg.setText("00")
        self.txtReg.setInputMask("HH")
        self.txtReg.setPlaceholderText("Register")

        self.txtValH.setText("0000")
        self.txtValH.setInputMask("HHHH")
        self.txtValH.setPlaceholderText("Value")

        self.txtValB.setText("0000 0000 0000 0000")
        self.txtValB.setInputMask("BBBB BBBB BBBB BBBB")
        self.txtValB.setPlaceholderText("Value(bin)")

        self.txtResult.setReadOnly(True)

    def setAnalyzer(self, analyzer):
        self.analyzer = analyzer

    def getAnalyzer(self):
        return self.analyzer

    def setRegValue(self, value):
        self.txtValH.setText('%04x' % value)
        self.txtValB.setText('{0:016b}'.format(value))

    def setupEvent(self):
        self.btnRun.clicked.connect(self.run)
        self.ckEn.stateChanged.connect(self.__ckEn)
        self.btnFunc.clicked.connect(self.__btnFunc)
        self.txtValB.textChanged.connect(self.__valBinChanged)
        self.txtValH.textChanged.connect(self.__valHexChanged)

    def setEn(self, b):
        self.ckEn.setChecked(b)

    def setEnCallback(self, cb):
        self.listEnCb = cb

    # return true or false
    def run(self):
        func = self.getCurrentFunc()

        strR = self.txtReg.text()
        if len(strR) != 2:
            self.setResult("Err Reg")
            return False
        reg = int(strR, 16) & 0xff

        if func == "Set":
            strH = self.txtValH.text()
            if len(strH) != 4:
                self.setResult("Err Val")
                return False
            val = int(strH, 16) & 0xffff
        else:
            val = None

        res = self._run(reg, val)
        self.setResult(res)
        return res

    # uint8, uint16, "Get" or "Set"
    # return None --> error , True  --> success, False --> fail
    def _run(self, reg, val = None):
        return None

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
        self.txtResult.setText(result)

    def clearResult(self):
        self.txtResult.setText("")

    # return "Get/Set"
    def getCurrentFunc(self):
        return str(self.btnFunc.text())

    def isEn(self):
        return self.ckEn.isChecked()

    def __btnFunc(self):
        func = self.getCurrentFunc()
        if func == "Set":
            self.btnFunc.setText("Get")
        else:
            self.btnFunc.setText("Set")

    def __valHexChanged(self):
        strH = self.txtValH.text()
        if len(strH) <= 4:
            strH = strH + "0" * (4 - len(strH))
        data = int(strH, 16) & 0xFFFF
        if self.txtValH.hasFocus() is True:
            self.txtValB.setText('{0:016b}'.format(data))

    def __valBinChanged(self):
        strB = self.txtValB.text().replace(" ", "")
        if len(strB) <= 16:
            strB = strB + "0" * (16 - len(strB))
        data = int(strB, 2) & 0xFFFF
        if self.txtValB.hasFocus() is True:
            self.txtValH.setText('%04x' % data)

    def __ckEn(self, state):
        if self.listEnCb:
            self.listEnCb(state)

class OAMItem(RegItem):
    WidgetInfo = {
        # widgetName: ("ColName", ColWidth),
        "EN":   ("EN", 60),
        "FUNC": ("Get/Set", 60),
        "LLID": ("LLID", 30),
        "REG":  ("REG", 30),
        "VALH": ("VAL", 40),
        "VALB": ("VAL(BIN)", 160),
        "RES":  ("RESULT", 80),
        "RUN":  ("RUN", 30),
    }

    HEAD = ("EN", "LLID", "REG", "VALH", "VALB", "RES", "FUNC",  "RUN")

    def __init__(self):
        RegItem.__init__(self)
        self.txtLLID = QtGui.QLineEdit()
        self.setupUI()
        self.setupEvent()

    def setupUI(self):
        RegItem.setupUI(self)
        self.txtLLID.setText("7E")
        self.txtLLID.setInputMask("HH")
        self.txtLLID.setPlaceholderText("LLID")

        self._setWidgetWidth(self.ckEn,        "EN")
        self._setWidgetWidth(self.txtLLID,     "LLID")
        self._setWidgetWidth(self.txtReg,      "REG")
        self._setWidgetWidth(self.txtValH,     "VALH")
        self._setWidgetWidth(self.txtValB,     "VALB")
        self._setWidgetWidth(self.txtResult,   "RES")
        self._setWidgetWidth(self.btnFunc,     "FUNC")
        self._setWidgetWidth(self.btnRun,      "RUN")

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(8)
        hbox.addWidget(self.ckEn)
        hbox.addWidget(self.txtLLID)
        hbox.addWidget(self.txtReg)
        hbox.addWidget(self.txtValH)
        hbox.addWidget(self.txtValB)
        hbox.addWidget(self.txtResult)
        hbox.addWidget(self.btnFunc)
        hbox.addWidget(self.btnRun)
        self.setLayout(hbox)

    def setupEvent(self):
        RegItem.setupEvent(self)

    def _run(self, reg, val = None):
        analyzer = self.getAnalyzer()
        strLlid = self.txtLLID.text()
        if len(strLlid) != 2:
            return None

        llid = int(strLlid, 16) & 0xff

        if val is None:
            res = analyzer.get_oam(llid, reg)
            if res is None:
                return False
            self.setRegValue(res)
            return True
        else:
            res = analyzer.set_oam(llid, reg, val)
            return res is not None

class ANAItem(RegItem):
    WidgetInfo = {
        # widgetName: ("ColName", ColWidth),
        "EN":   ("EN", 60),
        "FUNC": ("Get/Set", 60),
        "REG":  ("REG", 30),
        "VALH": ("VAL", 40),
        "VALB": ("VAL(BIN)", 160),
        "RES":  ("RESULT", 80),
        "RUN":  ("RUN", 30),
    }

    HEAD = ("EN", "REG", "VALH", "VALB", "RES", "FUNC", "RUN")

    def __init__(self):
        RegItem.__init__(self)
        self.setupUI()
        self.setupEvent()

    def setupUI(self):
        RegItem.setupUI(self)

        self._setWidgetWidth(self.ckEn,        "EN")
        self._setWidgetWidth(self.txtReg,      "REG")
        self._setWidgetWidth(self.txtValH,     "VALH")
        self._setWidgetWidth(self.txtValB,     "VALB")
        self._setWidgetWidth(self.txtResult,   "RES")
        self._setWidgetWidth(self.btnFunc,     "FUNC")
        self._setWidgetWidth(self.btnRun,      "RUN")

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(7)
        hbox.addWidget(self.ckEn)
        hbox.addWidget(self.txtReg)
        hbox.addWidget(self.txtValH)
        hbox.addWidget(self.txtValB)
        hbox.addWidget(self.txtResult)
        hbox.addWidget(self.btnFunc)
        hbox.addWidget(self.btnRun)
        self.setLayout(hbox)

    def setupEvent(self):
        RegItem.setupEvent(self)

    def _run(self, reg, val = None):
        analyzer = self.getAnalyzer()
        if val is None:
            res = analyzer.get_ana(reg)
            if res is None:
                return False
            self.setRegValue(res)
            return True
        else:
            res = analyzer.set_ana(reg, val)
            return res is not None

class RegList(QtGui.QWidget):
    def __init__(self, itemCls, itemNum):
        QtGui.QWidget.__init__(self)

        self.btnRunAll = QtGui.QPushButton("Run")
        self.ckOrderly = QtGui.QCheckBox("Orderly")
        self.ckEn = QtGui.QCheckBox("EN ALL")
        self.itemList = []
        self.setupUI(itemCls, itemNum)
        self.setupEvent()

    def setupUI(self, cls, num):
        toolBox = QtGui.QHBoxLayout()
        toolBox.addWidget(self.ckEn)
        toolBox.addWidget(self.ckOrderly)
        toolBox.addWidget(self.btnRunAll)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(num + 1)
        vbox.addWidget(cls.head())
        for i in range(num):
            item = cls()
            vbox.addWidget(item)
            self.itemList.append(item)

        vbox.addStretch(1)
        vbox.addLayout(toolBox)

        self.setLayout(vbox)

    def setupEvent(self):
        for item in self.itemList:
            item.setEnCallback(self.__ckEnItme)
        self.ckEn.stateChanged.connect(self.__ckEn)
        self.btnRunAll.clicked.connect(self.__btnRunAll)

    def setAnalyzer(self, analyzer):
        for item in self.itemList:
            item.setAnalyzer(analyzer)

    def isOrderly(self):
        return self.ckOrderly.isChecked()

    def __btnRunAll(self):
        isOrderly = self.isOrderly()
        for item in self.itemList:
            item.clearResult()

        for item in self.itemList:
            if item.isEn():
                res = item.run()
                if (not res) and isOrderly: return

    def __ckEn(self, state):
        if state == 2:
            b = True
        else:
            b = False

        for item in self.itemList:
            item.setEn(b)

    def __ckEnItme(self, state):
        res = True
        for item in self.itemList:
            res = item.isEn()
            if not res: break

        if res: self.ckEn.setChecked(True)

@AnalyzerControllerBase.bindUI(Ui_Register)
@AnalyzerControllerBase.bindAnalyzer("register")
class RegisterController(AnalyzerControllerBase):
    def __init__(self, **kw):
        AnalyzerControllerBase.__init__(self, **kw)
        self.tabPage = self
        self.setupEvent()

    def setupEvent(self):
        xOff = 10
        yOff = 40
        oamLabel = QtGui.QLabel("OAM", self.tabPage)
        oamLabel.move(xOff, 0)
        oamList = RegList(OAMItem, 2)
        oamList.setAnalyzer(self.analyzer)
        oamList.setParent(self.tabPage)
        oamList.move(xOff, yOff)

        oamH = 8 * 50
        anaLabel = QtGui.QLabel("ANA", self.tabPage)
        anaLabel.move(xOff, oamH + 50)
        anaList = RegList(ANAItem, 2)
        anaList.setAnalyzer(self.analyzer)
        anaList.setParent(self.tabPage)
        anaList.move(xOff, yOff + oamH + 50)
