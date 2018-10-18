# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './debugcore.ui'
#
# Created: Wed Aug  1 11:48:20 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_DebugCore(object):
    def setupUi(self, DebugCore):
        DebugCore.setObjectName("DebugCore")
        DebugCore.resize(907, 700)
        self.dbgcPrepointEn = QtGui.QCheckBox(DebugCore)
        self.dbgcPrepointEn.setGeometry(QtCore.QRect(480, 20, 85, 20))
        self.dbgcPrepointEn.setObjectName("dbgcPrepointEn")
        self.dbgcPoint = QtGui.QLineEdit(DebugCore)
        self.dbgcPoint.setGeometry(QtCore.QRect(360, 10, 71, 31))
        self.dbgcPoint.setObjectName("dbgcPoint")
        self.dbgcCap = QtGui.QPushButton(DebugCore)
        self.dbgcCap.setGeometry(QtCore.QRect(30, 60, 98, 27))
        self.dbgcCap.setObjectName("dbgcCap")
        self.dbgcPrepoint = QtGui.QLineEdit(DebugCore)
        self.dbgcPrepoint.setGeometry(QtCore.QRect(570, 10, 71, 31))
        self.dbgcPrepoint.setObjectName("dbgcPrepoint")
        self.labelEvents = QtGui.QLabel(DebugCore)
        self.labelEvents.setGeometry(QtCore.QRect(10, 10, 41, 21))
        self.labelEvents.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.labelEvents.setObjectName("labelEvents")
        self.labelPoint = QtGui.QLabel(DebugCore)
        self.labelPoint.setGeometry(QtCore.QRect(310, 20, 41, 17))
        self.labelPoint.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPoint.setObjectName("labelPoint")
        self.dbgcEvents = QtGui.QComboBox(DebugCore)
        self.dbgcEvents.setGeometry(QtCore.QRect(60, 10, 191, 27))
        self.dbgcEvents.setObjectName("dbgcEvents")
        self.dbgcEvents.addItem("")
        self.dbgcCanvas = QtGui.QWidget(DebugCore)
        self.dbgcCanvas.setGeometry(QtCore.QRect(10, 90, 880, 600))
        self.dbgcCanvas.setObjectName("dbgcCanvas")

        self.retranslateUi(DebugCore)
        QtCore.QMetaObject.connectSlotsByName(DebugCore)

    def retranslateUi(self, DebugCore):
        DebugCore.setWindowTitle(QtGui.QApplication.translate("DebugCore", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.dbgcPrepointEn.setText(QtGui.QApplication.translate("DebugCore", "PrePoint", None, QtGui.QApplication.UnicodeUTF8))
        self.dbgcCap.setText(QtGui.QApplication.translate("DebugCore", "capture", None, QtGui.QApplication.UnicodeUTF8))
        self.labelEvents.setText(QtGui.QApplication.translate("DebugCore", "Event", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPoint.setText(QtGui.QApplication.translate("DebugCore", "Point", None, QtGui.QApplication.UnicodeUTF8))
        self.dbgcEvents.setItemText(0, QtGui.QApplication.translate("DebugCore", "event", None, QtGui.QApplication.UnicodeUTF8))

