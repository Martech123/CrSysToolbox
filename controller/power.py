from controller import OnlineAnalyzerControllerBase as AnalyzerControllerBase
from PySide import QtGui, QtCore
from ui.ui_power import Ui_Power

@AnalyzerControllerBase.bindUI(Ui_Power)
@AnalyzerControllerBase.bindAnalyzer("power")
class PowerController(AnalyzerControllerBase):
    def __init__(self, **kw):
        AnalyzerControllerBase.__init__(self, **kw)

        powerList = self.__getPowerList()
        powerList.clear()
        powerListInfo = self.analyzer.list_power()
        powerList.addItems(map(str, powerListInfo))

    def __getPowerList(self):
        return self.ui.powerList

    def __getCurrentPower(self):
        power = int(self.__getPowerList().currentText())
        return power

    def __log(self, info, success):
        if success == True:
            res = "Success"
        else:
            res = "Fail"
        self.logStatus("%s: %s" % (info, res))

    # ==================================
    # Event Callback
    # ==================================
    @QtCore.Slot()
    def on_powerGet_clicked(self):
        power = self.analyzer.get_power()
        if power is None:
            self.__log("Get Power", False)
            return
        idx = self.__getPowerList().findText(str(power))
        self.__getPowerList().setCurrentIndex(idx)
        self.__log("Get Power", True)

    @QtCore.Slot()
    def on_powerSet_clicked(self):
        power = self.__getCurrentPower()
        res = self.analyzer.set_power(power)
        self.__log("Set Power", res is not None)

    @QtCore.Slot(int)
    def on_powerList_currentIndexChanged(self, idx):
        power = self.__getCurrentPower()
        powerInfo = self.analyzer.get_power_info(power)
        if not powerInfo:
            info = "Power: Error"
        else:
            info = "Power: %s" % powerInfo
        self.__getPowerList().setToolTip(info)
        self.logStatus(info)
