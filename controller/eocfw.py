import os
from controller import ControllerBase
from eoc_frequency import EocFreqWrapper
from PySide import QtGui, QtCore

from PySide.QtGui import QFileDialog
from fw_customize.fw_gen import fw_gen
from ui.ui_eocfw import Ui_EocFirmware


@ControllerBase.bindUI(Ui_EocFirmware)
class CustomizeEocController(ControllerBase):
    fw_save_path_default = os.curdir + os.sep + "tmp-fw-gen.bin"

    def __init__(self, **kw):
        ControllerBase.__init__(self, **kw)

        self.fw = fw_gen()

        # setup UI
        self.ui.eocfwSave.setEnabled(False)
        self.ui.eocfwSavePath.setText(self.fw_save_path_default)
        self.freqWidget = EocFreqWrapper(
                            main = self.getMainWindow(),
                            parent = self.ui.eocfwFreq)

        # setup Event
        self.freqWidget.setupRestoreCallback(self._getFreqByIdx)

    def _getFreqByIdx(self, idx):
        regList = self.fw.get_band_reg_list()
        if idx >= len(regList):
            return [None for i in range(4)]

        return regList[idx]

    def __getLoadPath(self):
        return str(self.ui.eocfwLoadPath.text())

    def __getSavePath(self):
        return str(self.ui.eocfwSavePath.text())

    def __synFromFirmware(self, iscnu):
        # ---- clt only ----
        if not iscnu:
            # NIC mode
            force_100M = self.fw.get_force_nic_mode_default()
            self.ui.eocfwCfgClt100MEn.setChecked(force_100M)
        self.ui.eocfwCfgClt100MEn.setEnabled(not iscnu)

        # ---- common ----
        # Bands config
        try:
            self.freqWidget.setEnabled(True)
            regsList = self.fw.get_band_reg_list()
            self.freqWidget.reloadFreq(regsList)
        except fw_gen.ErrorBandAna15Unsupported:
            self.freqWidget.setEnabled(False)
            self.freqWidget.setError("band unsupported")
            self.logStatus("Ana15 unsupported")

    def __synToFirmware(self, iscnu):
        if self.ui.eocfwCfgClt100MEn.isEnabled():
            force_100M = self.ui.eocfwCfgClt100MEn.isChecked()
            self.fw.set_force_nic_mode_default(force_100M)

        if self.freqWidget.isEnabled():
            # Bands config
            regList = self.freqWidget.dumpRegister()
            rangList = self.freqWidget.dumpRange()
            bandsInfo = zip(regList, rangList)
            for i, info in enumerate(bandsInfo):
                regs = info[0]
                rangs = info[1]
                # only config valid info
                if None in rangs:
                    print("Warning bands info {idx}: {value}".format(
                            idx = i, value = rangs))
                    continue

                self.fw.set_band_reg(i, *regs)
                self.fw.set_band_range(i, *map(int, rangs))

        # re-calc check sum
        self.fw.set_csum()

    def _iscnu(self):
        return self.fw.get_firmware_type() == "cnu"

    # ==================================
    # Event Callback
    # ==================================
    @QtCore.Slot()
    def on_eocfwSaveChoose_clicked(self):
        mainWindow = self._mainWindow
        info = "Save Firmware"
        path = self.__getSavePath()
        path = str(QFileDialog.getSaveFileName(mainWindow, info, path)[0])
        if not path:
            path = self.fw_save_path_default
        self.ui.eocfwSavePath.setText(path)

    @QtCore.Slot()
    def on_eocfwLoadChoose_clicked(self):
        mainWindow = self._mainWindow
        info = "Load Firmware"
        path = self.__getLoadPath()
        path = str(QFileDialog.getOpenFileName(mainWindow, info, path)[0])
        self.ui.eocfwLoadPath.setText(path)

    @QtCore.Slot()
    def on_eocfwSave_clicked(self):
        path = self.__getSavePath()
        if path == "":
            path = self.fw_save_path_default

        iscnu = self._iscnu()
        self.__synToFirmware(iscnu)
        self.fw.save_fw(path, iscnu = iscnu)

    @QtCore.Slot()
    def on_eocfwLoad_clicked(self):
        self.ui.eocfwSave.setEnabled(False)
        path = self.__getLoadPath()
        self.fw.load_fw(path)
        iscnu = self._iscnu()
        self.__synFromFirmware(iscnu)
        self.ui.eocfwType.setText(self.fw.get_firmware_type())
        self.ui.eocfwSave.setEnabled(True)
