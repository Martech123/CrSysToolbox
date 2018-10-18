# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './eoc_frequency.ui'
#
# Created: Wed Aug  1 11:48:20 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_EocFreq(object):
    def setupUi(self, EocFreq):
        EocFreq.setObjectName("EocFreq")
        EocFreq.resize(817, 48)
        self.freqRestore = QtGui.QPushButton(EocFreq)
        self.freqRestore.setGeometry(QtCore.QRect(650, 10, 70, 27))
        self.freqRestore.setObjectName("freqRestore")
        self.freqSave = QtGui.QPushButton(EocFreq)
        self.freqSave.setGeometry(QtCore.QRect(490, 10, 70, 27))
        self.freqSave.setMouseTracking(False)
        self.freqSave.setObjectName("freqSave")
        self.freqLoad = QtGui.QPushButton(EocFreq)
        self.freqLoad.setGeometry(QtCore.QRect(570, 10, 70, 27))
        self.freqLoad.setObjectName("freqLoad")
        self.freqLog = QtGui.QPushButton(EocFreq)
        self.freqLog.setGeometry(QtCore.QRect(730, 10, 70, 27))
        self.freqLog.setObjectName("freqLog")
        self.freqFC = QtGui.QComboBox(EocFreq)
        self.freqFC.setGeometry(QtCore.QRect(380, 10, 100, 27))
        self.freqFC.setObjectName("freqFC")
        self.freqFC.addItem("")
        self.freqFullBW = QtGui.QComboBox(EocFreq)
        self.freqFullBW.setGeometry(QtCore.QRect(160, 10, 100, 27))
        self.freqFullBW.setObjectName("freqFullBW")
        self.freqFullBW.addItem("")
        self.freqBW = QtGui.QComboBox(EocFreq)
        self.freqBW.setGeometry(QtCore.QRect(270, 10, 100, 27))
        self.freqBW.setObjectName("freqBW")
        self.freqBW.addItem("")
        self.freqRange = QtGui.QTextEdit(EocFreq)
        self.freqRange.setEnabled(False)
        self.freqRange.setGeometry(QtCore.QRect(10, 10, 140, 27))
        self.freqRange.setObjectName("freqRange")

        self.retranslateUi(EocFreq)
        QtCore.QMetaObject.connectSlotsByName(EocFreq)

    def retranslateUi(self, EocFreq):
        EocFreq.setWindowTitle(QtGui.QApplication.translate("EocFreq", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.freqRestore.setText(QtGui.QApplication.translate("EocFreq", "Restore", None, QtGui.QApplication.UnicodeUTF8))
        self.freqSave.setText(QtGui.QApplication.translate("EocFreq", "save", None, QtGui.QApplication.UnicodeUTF8))
        self.freqLoad.setText(QtGui.QApplication.translate("EocFreq", "load", None, QtGui.QApplication.UnicodeUTF8))
        self.freqLog.setText(QtGui.QApplication.translate("EocFreq", "Log", None, QtGui.QApplication.UnicodeUTF8))
        self.freqFC.setItemText(0, QtGui.QApplication.translate("EocFreq", "fc", None, QtGui.QApplication.UnicodeUTF8))
        self.freqFullBW.setItemText(0, QtGui.QApplication.translate("EocFreq", "bw", None, QtGui.QApplication.UnicodeUTF8))
        self.freqBW.setItemText(0, QtGui.QApplication.translate("EocFreq", "bw divi ratio", None, QtGui.QApplication.UnicodeUTF8))

