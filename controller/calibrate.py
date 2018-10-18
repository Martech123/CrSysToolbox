from controller import OnlineAnalyzerControllerBase as AnalyzerControllerBase
from PySide import QtGui, QtCore
from utils.thread import SimpleThread
from ui.ui_calibrate import Ui_PACalibration

@AnalyzerControllerBase.bindUI(Ui_PACalibration)
@AnalyzerControllerBase.bindAnalyzer("calibration")
class CalibrateController(AnalyzerControllerBase):
    def __init__(self, **kw):
        AnalyzerControllerBase.__init__(self, **kw)

        self.device_ip = "192.168.36.109"
        self.reports = None
        self.threadPA = SimpleThread()

        # setup UI
        self.ui.paDiffIdx.setText("0")
        self.ui.paAtten.setText("10")
        self.ui.deviceIP.setText(self.device_ip)
        self.__setDeviceConnEnable(True)

        # PA thread
        self.threadPA.registerCallback(self.__threadCapturePA)
        self.threadPA.finished.connect(self.__displayPA)
        self.threadPA.terminated.connect(self.__recoverAgent)

    def __setDeviceConnEnable(self, b):
        self.ui.deviceConnect.setEnabled(b)
        self.ui.deviceDisconnect.setEnabled(not b)

    def __threadCapturePA(self, thread):
        # setup device Atten
        atten = str(self.ui.paAtten.text())
        self.analyzer.set_attenuation(atten)

        self.ui.paAtten.setText(str(self.analyzer.get_attenuation()))
        self.getAgentController().lockAgent()
        self.reports = self.analyzer.calibrate_pa()

    def __displayPA(self):
        self.__recoverAgent()
        reports = self.reports
        res_list = reports.report()
        res_tab = reports.report_table()
        self.ui.paResultTable.setText(res_tab)
        self.ui.paResultList.setText(res_list)
        self.logStatus("capture statuse: done")

    def __recoverAgent(self):
        self.getAgentController().unlockAgent()

    # ==================================
    # Event Callback
    # ==================================
    @QtCore.Slot()
    def on_deviceConnect_clicked(self):
        self.analyzer.connet_device(self.device_ip)
        self.__setDeviceConnEnable(False)

    @QtCore.Slot()
    def on_deviceDisconnect_clicked(self):
        self.analyzer.disconnect_device()
        self.__setDeviceConnEnable(True)

    @QtCore.Slot()
    def on_paCap_clicked(self):
        if not self.analyzer.is_device_available():
            self.logStatus("please connect device")
            return

        if not self.threadPA.isRunning():
            self.threadPA.start()
            info = "PA Capture is running, it may take some time"
            self.ui.paResultList.setText(info)
            self.ui.paResultTable.setText(info)
            self.logStatus("capture status: running")
        else:
            self.logStatus("Warning: capture is already running")

    @QtCore.Slot()
    def on_paReport_clicked(self):
        res_list = self.reports.report()
        self.ui.paResultList.setText(res_list)

    @QtCore.Slot()
    def on_paReportDiff_clicked(self):
        report_number = self.reports.count()
        idx = int(self.ui.paDiffIdx.text())

        if idx not in range(report_number):
            return None

        res_list = self.reports.report_diff(idx)
        self.ui.paResultList.setText(res_list)
