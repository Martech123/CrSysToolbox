# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './power.ui'
#
# Created: Mon Aug 13 10:37:11 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Power(object):
    def setupUi(self, Power):
        Power.setObjectName("Power")
        Power.resize(457, 82)
        self.powerSet = QtGui.QPushButton(Power)
        self.powerSet.setGeometry(QtCore.QRect(360, 30, 79, 25))
        self.powerSet.setObjectName("powerSet")
        self.powerGet = QtGui.QPushButton(Power)
        self.powerGet.setGeometry(QtCore.QRect(250, 30, 79, 25))
        self.powerGet.setObjectName("powerGet")
        self.label_3 = QtGui.QLabel(Power)
        self.label_3.setGeometry(QtCore.QRect(10, 31, 91, 20))
        self.label_3.setObjectName("label_3")
        self.powerList = QtGui.QComboBox(Power)
        self.powerList.setGeometry(QtCore.QRect(130, 30, 91, 21))
        self.powerList.setObjectName("powerList")

        self.retranslateUi(Power)
        QtCore.QMetaObject.connectSlotsByName(Power)

    def retranslateUi(self, Power):
        Power.setWindowTitle(QtGui.QApplication.translate("Power", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.powerSet.setText(QtGui.QApplication.translate("Power", "Set", None, QtGui.QApplication.UnicodeUTF8))
        self.powerGet.setText(QtGui.QApplication.translate("Power", "Get", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Power", "TxPower(dBm)", None, QtGui.QApplication.UnicodeUTF8))

