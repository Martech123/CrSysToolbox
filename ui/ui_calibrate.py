# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './calibrate.ui'
#
# Created: Wed Aug  1 11:48:19 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PACalibration(object):
    def setupUi(self, PACalibration):
        PACalibration.setObjectName("PACalibration")
        PACalibration.resize(877, 455)
        self.paAtten = QtGui.QLineEdit(PACalibration)
        self.paAtten.setGeometry(QtCore.QRect(240, 90, 51, 21))
        self.paAtten.setText("")
        self.paAtten.setObjectName("paAtten")
        self.paReportDiff = QtGui.QPushButton(PACalibration)
        self.paReportDiff.setGeometry(QtCore.QRect(130, 150, 79, 25))
        self.paReportDiff.setObjectName("paReportDiff")
        self.paCap = QtGui.QPushButton(PACalibration)
        self.paCap.setGeometry(QtCore.QRect(10, 90, 79, 25))
        self.paCap.setObjectName("paCap")
        self.deviceDisconnect = QtGui.QPushButton(PACalibration)
        self.deviceDisconnect.setGeometry(QtCore.QRect(360, 50, 79, 25))
        self.deviceDisconnect.setObjectName("deviceDisconnect")
        self.label_17 = QtGui.QLabel(PACalibration)
        self.label_17.setGeometry(QtCore.QRect(140, 100, 58, 15))
        self.label_17.setObjectName("label_17")
        self.deviceIP = QtGui.QLineEdit(PACalibration)
        self.deviceIP.setGeometry(QtCore.QRect(100, 50, 113, 21))
        self.deviceIP.setObjectName("deviceIP")
        self.paReport = QtGui.QPushButton(PACalibration)
        self.paReport.setGeometry(QtCore.QRect(10, 150, 79, 25))
        self.paReport.setObjectName("paReport")
        self.label_18 = QtGui.QLabel(PACalibration)
        self.label_18.setGeometry(QtCore.QRect(10, 10, 91, 31))
        self.label_18.setObjectName("label_18")
        self.label_19 = QtGui.QLabel(PACalibration)
        self.label_19.setGeometry(QtCore.QRect(20, 50, 71, 21))
        self.label_19.setObjectName("label_19")
        self.paResultList = QtGui.QTextEdit(PACalibration)
        self.paResultList.setEnabled(False)
        self.paResultList.setGeometry(QtCore.QRect(0, 210, 871, 231))
        self.paResultList.setObjectName("paResultList")
        self.deviceConnect = QtGui.QPushButton(PACalibration)
        self.deviceConnect.setGeometry(QtCore.QRect(250, 50, 79, 25))
        self.deviceConnect.setObjectName("deviceConnect")
        self.paDiffIdx = QtGui.QLineEdit(PACalibration)
        self.paDiffIdx.setGeometry(QtCore.QRect(250, 150, 41, 21))
        self.paDiffIdx.setObjectName("paDiffIdx")
        self.paResultTable = QtGui.QTextEdit(PACalibration)
        self.paResultTable.setEnabled(False)
        self.paResultTable.setGeometry(QtCore.QRect(480, 50, 391, 131))
        self.paResultTable.setObjectName("paResultTable")

        self.retranslateUi(PACalibration)
        QtCore.QMetaObject.connectSlotsByName(PACalibration)

    def retranslateUi(self, PACalibration):
        PACalibration.setWindowTitle(QtGui.QApplication.translate("PACalibration", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.paReportDiff.setText(QtGui.QApplication.translate("PACalibration", "Report Diff", None, QtGui.QApplication.UnicodeUTF8))
        self.paCap.setText(QtGui.QApplication.translate("PACalibration", "Capture PA", None, QtGui.QApplication.UnicodeUTF8))
        self.deviceDisconnect.setText(QtGui.QApplication.translate("PACalibration", "disconnect", None, QtGui.QApplication.UnicodeUTF8))
        self.label_17.setText(QtGui.QApplication.translate("PACalibration", "PA Atten", None, QtGui.QApplication.UnicodeUTF8))
        self.paReport.setText(QtGui.QApplication.translate("PACalibration", "repoert", None, QtGui.QApplication.UnicodeUTF8))
        self.label_18.setText(QtGui.QApplication.translate("PACalibration", "Calibration PA", None, QtGui.QApplication.UnicodeUTF8))
        self.label_19.setText(QtGui.QApplication.translate("PACalibration", "DEVICE IP", None, QtGui.QApplication.UnicodeUTF8))
        self.deviceConnect.setText(QtGui.QApplication.translate("PACalibration", "connect", None, QtGui.QApplication.UnicodeUTF8))

