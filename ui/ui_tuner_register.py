# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './tuner_register.ui'
#
# Created: Wed Aug  1 11:48:20 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_TunerRegister(object):
    def setupUi(self, TunerRegister):
        TunerRegister.setObjectName("TunerRegister")
        TunerRegister.resize(648, 45)
        self.tunerAddr = QtGui.QLineEdit(TunerRegister)
        self.tunerAddr.setGeometry(QtCore.QRect(70, 10, 41, 20))
        self.tunerAddr.setObjectName("tunerAddr")
        self.tunerHex = QtGui.QLineEdit(TunerRegister)
        self.tunerHex.setGeometry(QtCore.QRect(160, 10, 41, 20))
        self.tunerHex.setObjectName("tunerHex")
        self.tunerBin = QtGui.QLineEdit(TunerRegister)
        self.tunerBin.setGeometry(QtCore.QRect(250, 10, 121, 20))
        self.tunerBin.setObjectName("tunerBin")
        self.label = QtGui.QLabel(TunerRegister)
        self.label.setGeometry(QtCore.QRect(19, 13, 31, 16))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(TunerRegister)
        self.label_2.setGeometry(QtCore.QRect(128, 13, 31, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(TunerRegister)
        self.label_3.setGeometry(QtCore.QRect(220, 13, 21, 16))
        self.label_3.setObjectName("label_3")
        self.tunerGet = QtGui.QPushButton(TunerRegister)
        self.tunerGet.setGeometry(QtCore.QRect(470, 10, 79, 25))
        self.tunerGet.setObjectName("tunerGet")
        self.tunerSet = QtGui.QPushButton(TunerRegister)
        self.tunerSet.setGeometry(QtCore.QRect(560, 10, 79, 25))
        self.tunerSet.setObjectName("tunerSet")
        self.tunerResult = QtGui.QLineEdit(TunerRegister)
        self.tunerResult.setEnabled(False)
        self.tunerResult.setGeometry(QtCore.QRect(390, 10, 71, 21))
        self.tunerResult.setObjectName("tunerResult")

        self.retranslateUi(TunerRegister)
        QtCore.QMetaObject.connectSlotsByName(TunerRegister)

    def retranslateUi(self, TunerRegister):
        TunerRegister.setWindowTitle(QtGui.QApplication.translate("TunerRegister", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("TunerRegister", "Addr", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("TunerRegister", "Hex", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("TunerRegister", "Bin", None, QtGui.QApplication.UnicodeUTF8))
        self.tunerGet.setText(QtGui.QApplication.translate("TunerRegister", "Get", None, QtGui.QApplication.UnicodeUTF8))
        self.tunerSet.setText(QtGui.QApplication.translate("TunerRegister", "Set", None, QtGui.QApplication.UnicodeUTF8))

