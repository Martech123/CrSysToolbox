# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './eocfw.ui'
#
# Created: Wed Aug  1 11:48:20 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_EocFirmware(object):
    def setupUi(self, EocFirmware):
        EocFirmware.setObjectName("EocFirmware")
        EocFirmware.resize(698, 343)
        self.labelLoad = QtGui.QLabel(EocFirmware)
        self.labelLoad.setGeometry(QtCore.QRect(10, 56, 58, 15))
        self.labelLoad.setObjectName("labelLoad")
        self.eocfwCfgClt100MEn = QtGui.QCheckBox(EocFirmware)
        self.eocfwCfgClt100MEn.setGeometry(QtCore.QRect(10, 120, 131, 20))
        self.eocfwCfgClt100MEn.setObjectName("eocfwCfgClt100MEn")
        self.labelSave = QtGui.QLabel(EocFirmware)
        self.labelSave.setGeometry(QtCore.QRect(10, 86, 58, 15))
        self.labelSave.setObjectName("labelSave")
        self.eocfwSave = QtGui.QPushButton(EocFirmware)
        self.eocfwSave.setGeometry(QtCore.QRect(590, 76, 79, 25))
        self.eocfwSave.setObjectName("eocfwSave")
        self.eocfwLoadChoose = QtGui.QPushButton(EocFirmware)
        self.eocfwLoadChoose.setGeometry(QtCore.QRect(470, 46, 71, 21))
        self.eocfwLoadChoose.setObjectName("eocfwLoadChoose")
        self.eocfwLoadPath = QtGui.QLineEdit(EocFirmware)
        self.eocfwLoadPath.setGeometry(QtCore.QRect(90, 46, 371, 21))
        self.eocfwLoadPath.setObjectName("eocfwLoadPath")
        self.eocfwSavePath = QtGui.QLineEdit(EocFirmware)
        self.eocfwSavePath.setGeometry(QtCore.QRect(90, 76, 371, 21))
        self.eocfwSavePath.setText("")
        self.eocfwSavePath.setObjectName("eocfwSavePath")
        self.eocfwSaveChoose = QtGui.QPushButton(EocFirmware)
        self.eocfwSaveChoose.setGeometry(QtCore.QRect(470, 76, 71, 21))
        self.eocfwSaveChoose.setObjectName("eocfwSaveChoose")
        self.eocfwLoad = QtGui.QPushButton(EocFirmware)
        self.eocfwLoad.setGeometry(QtCore.QRect(590, 46, 79, 25))
        self.eocfwLoad.setObjectName("eocfwLoad")
        self.eocfwFreq = QtGui.QWidget(EocFirmware)
        self.eocfwFreq.setGeometry(QtCore.QRect(10, 150, 681, 81))
        self.eocfwFreq.setObjectName("eocfwFreq")
        self.eocfwType = QtGui.QLineEdit(EocFirmware)
        self.eocfwType.setEnabled(False)
        self.eocfwType.setGeometry(QtCore.QRect(90, 10, 81, 21))
        self.eocfwType.setObjectName("eocfwType")
        self.labelLoad_2 = QtGui.QLabel(EocFirmware)
        self.labelLoad_2.setGeometry(QtCore.QRect(24, 15, 31, 16))
        self.labelLoad_2.setObjectName("labelLoad_2")

        self.retranslateUi(EocFirmware)
        QtCore.QMetaObject.connectSlotsByName(EocFirmware)

    def retranslateUi(self, EocFirmware):
        EocFirmware.setWindowTitle(QtGui.QApplication.translate("EocFirmware", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.labelLoad.setText(QtGui.QApplication.translate("EocFirmware", "Load Path", None, QtGui.QApplication.UnicodeUTF8))
        self.eocfwCfgClt100MEn.setText(QtGui.QApplication.translate("EocFirmware", "clt_default_100M", None, QtGui.QApplication.UnicodeUTF8))
        self.labelSave.setText(QtGui.QApplication.translate("EocFirmware", "Save Path", None, QtGui.QApplication.UnicodeUTF8))
        self.eocfwSave.setText(QtGui.QApplication.translate("EocFirmware", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.eocfwLoadChoose.setText(QtGui.QApplication.translate("EocFirmware", "choose", None, QtGui.QApplication.UnicodeUTF8))
        self.eocfwSaveChoose.setText(QtGui.QApplication.translate("EocFirmware", "choose", None, QtGui.QApplication.UnicodeUTF8))
        self.eocfwLoad.setText(QtGui.QApplication.translate("EocFirmware", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.eocfwType.setText(QtGui.QApplication.translate("EocFirmware", "fw type", None, QtGui.QApplication.UnicodeUTF8))
        self.labelLoad_2.setText(QtGui.QApplication.translate("EocFirmware", "type", None, QtGui.QApplication.UnicodeUTF8))

