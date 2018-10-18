# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './frequency.ui'
#
# Created: Wed Aug  1 11:48:20 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Frequency(object):
    def setupUi(self, Frequency):
        Frequency.setObjectName("Frequency")
        Frequency.resize(1176, 688)
        self.label_9 = QtGui.QLabel(Frequency)
        self.label_9.setGeometry(QtCore.QRect(140, 70, 131, 20))
        self.label_9.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.freqFC = QtGui.QComboBox(Frequency)
        self.freqFC.setGeometry(QtCore.QRect(290, 100, 120, 27))
        self.freqFC.setObjectName("freqFC")
        self.freqFC.addItem("")
        self.label_2 = QtGui.QLabel(Frequency)
        self.label_2.setGeometry(QtCore.QRect(10, 250, 41, 17))
        self.label_2.setObjectName("label_2")
        self.freqGet = QtGui.QPushButton(Frequency)
        self.freqGet.setGeometry(QtCore.QRect(100, 190, 81, 27))
        self.freqGet.setMouseTracking(False)
        self.freqGet.setObjectName("freqGet")
        self.freqLoad = QtGui.QPushButton(Frequency)
        self.freqLoad.setGeometry(QtCore.QRect(210, 250, 81, 27))
        self.freqLoad.setObjectName("freqLoad")
        self.label_10 = QtGui.QLabel(Frequency)
        self.label_10.setGeometry(QtCore.QRect(305, 70, 81, 20))
        self.label_10.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.freqHint = QtGui.QTextEdit(Frequency)
        self.freqHint.setEnabled(False)
        self.freqHint.setGeometry(QtCore.QRect(550, 30, 311, 251))
        self.freqHint.setObjectName("freqHint")
        self.label = QtGui.QLabel(Frequency)
        self.label.setGeometry(QtCore.QRect(10, 200, 91, 17))
        self.label.setObjectName("label")
        self.freqBW = QtGui.QComboBox(Frequency)
        self.freqBW.setGeometry(QtCore.QRect(150, 100, 120, 27))
        self.freqBW.setObjectName("freqBW")
        self.freqBW.addItem("")
        self.freqApply = QtGui.QPushButton(Frequency)
        self.freqApply.setGeometry(QtCore.QRect(210, 190, 81, 27))
        self.freqApply.setObjectName("freqApply")
        self.freqSave = QtGui.QPushButton(Frequency)
        self.freqSave.setGeometry(QtCore.QRect(100, 250, 81, 27))
        self.freqSave.setMouseTracking(False)
        self.freqSave.setObjectName("freqSave")
        self.freqCanvas = QtGui.QWidget(Frequency)
        self.freqCanvas.setGeometry(QtCore.QRect(10, 300, 851, 361))
        self.freqCanvas.setObjectName("freqCanvas")
        self.freqFullBW = QtGui.QComboBox(Frequency)
        self.freqFullBW.setGeometry(QtCore.QRect(7, 100, 120, 27))
        self.freqFullBW.setObjectName("freqFullBW")
        self.freqFullBW.addItem("")
        self.label_11 = QtGui.QLabel(Frequency)
        self.label_11.setGeometry(QtCore.QRect(20, 70, 101, 20))
        self.label_11.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.freqRange = QtGui.QTextEdit(Frequency)
        self.freqRange.setEnabled(False)
        self.freqRange.setGeometry(QtCore.QRect(100, 150, 311, 27))
        self.freqRange.setObjectName("freqRange")
        self.label_12 = QtGui.QLabel(Frequency)
        self.label_12.setGeometry(QtCore.QRect(10, 155, 81, 20))
        self.label_12.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")

        self.retranslateUi(Frequency)
        QtCore.QMetaObject.connectSlotsByName(Frequency)

    def retranslateUi(self, Frequency):
        Frequency.setWindowTitle(QtGui.QApplication.translate("Frequency", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Frequency", "division ratio", None, QtGui.QApplication.UnicodeUTF8))
        self.freqFC.setItemText(0, QtGui.QApplication.translate("Frequency", "fc", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Frequency", "config", None, QtGui.QApplication.UnicodeUTF8))
        self.freqGet.setText(QtGui.QApplication.translate("Frequency", "Get", None, QtGui.QApplication.UnicodeUTF8))
        self.freqLoad.setText(QtGui.QApplication.translate("Frequency", "load", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Frequency", "Fc (MHz)", None, QtGui.QApplication.UnicodeUTF8))
        self.freqHint.setHtml(QtGui.QApplication.translate("Frequency", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">Tips:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">pll   --&gt;  adc(bandwidth)</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">adc --&gt; bw(divided bandwidth)</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">bw --&gt; fc</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">pll   = 1200 ~ 1900      [MHz]</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">adc = pll / (6 or 8)      [MHz]</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">bw  = adc / 4 / div_freq      [MHz]</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">fc    = adc * offset       [MHz]</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">div_freq = 2/4/8</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">offset = oam[13:9] -&gt; 2^-2 ~ 2^-6</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Frequency", "online config", None, QtGui.QApplication.UnicodeUTF8))
        self.freqBW.setItemText(0, QtGui.QApplication.translate("Frequency", "bw divi ratio", None, QtGui.QApplication.UnicodeUTF8))
        self.freqApply.setText(QtGui.QApplication.translate("Frequency", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.freqSave.setText(QtGui.QApplication.translate("Frequency", "save", None, QtGui.QApplication.UnicodeUTF8))
        self.freqFullBW.setItemText(0, QtGui.QApplication.translate("Frequency", "bw(full)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Frequency", "bandwith(MHz)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("Frequency", "Range(L, H)", None, QtGui.QApplication.UnicodeUTF8))

