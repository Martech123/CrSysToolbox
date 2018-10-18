import sys
from PySide import QtGui, QtCore
from controller.agent import AgentController
from controller.frequency import OnlineFreqController
from controller.power import PowerController
from controller.tuner import TunerController
from controller.dbgc import DebugCoreController
from controller.calibrate import CalibrateController
from controller.eocfw import CustomizeEocController
from controller.register import RegisterController

class ToolGui(QtGui.QMainWindow):
    def __init__(self):
        super(ToolGui, self).__init__()
        self.setupUi()
        self.setupAgent()
        self.setupPower()
        self.setupRegister()
        self.setupDebugCore()
        self.setupCalibration()
        self.setupFrequency()
        self.setupCustomize()

        # agent Unavailable on default
        self.ctlAgent.lockAgent()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(900, 750)
        self.tabMain = QtGui.QTabWidget(self)
        self.tabMain.setGeometry(QtCore.QRect(0, 0, 900, 700))
        self.tabMain.setAutoFillBackground(True)
        self.tabMain.setObjectName("tabMain")

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def setupAgent(self):
        self.ctlAgent = AgentController(main = self)
        self.tabMain.addTab(self.ctlAgent, "Configuration")

    def getAgentController(self):
        return self.ctlAgent

    def setupFrequency(self):
        self.ctlFreq = OnlineFreqController(main = self)
        self.tabMain.addTab(self.ctlFreq, "Frequency")

    def setupPower(self):
        powerPage = QtGui.QWidget()
        ctlPower = PowerController(main = self, parent = powerPage)
        ctlTuner = TunerController(main = self, parent = powerPage)
        pos = ctlPower.pos()
        ctlTuner.move(pos.x(), pos.y() + ctlPower.height())
        self.tabMain.addTab(powerPage, "Tuner")

    def setupDebugCore(self):
        self.ctlDbgc = DebugCoreController(main = self)
        self.tabMain.addTab(self.ctlDbgc, "Advance")

    def setupCalibration(self):
        self.ctlCalibrate = CalibrateController(main = self)
        self.tabMain.addTab(self.ctlCalibrate, "Calibration")

    def setupCustomize(self):
        self.ctlEocFw = CustomizeEocController(main = self)
        self.tabMain.addTab(self.ctlEocFw, "Customize Eoc")

    def setupRegister(self):
        self.ctlRegister = RegisterController(main = self)
        self.tabMain.addTab(self.ctlRegister, "OAM & ANA")

def main():
    app = QtGui.QApplication(sys.argv)
    ui = ToolGui()
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
