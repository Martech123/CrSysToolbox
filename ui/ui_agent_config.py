# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './agent_config.ui'
#
# Created: Wed Aug  1 11:48:19 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AgentConfig(object):
    def setupUi(self, AgentConfig):
        AgentConfig.setObjectName("AgentConfig")
        AgentConfig.resize(456, 369)
        AgentConfig.setBaseSize(QtCore.QSize(750, 0))
        self.labelAgent = QtGui.QLabel(AgentConfig)
        self.labelAgent.setGeometry(QtCore.QRect(20, 60, 66, 17))
        self.labelAgent.setObjectName("labelAgent")
        self.agentDisconnect = QtGui.QPushButton(AgentConfig)
        self.agentDisconnect.setGeometry(QtCore.QRect(310, 200, 98, 27))
        self.agentDisconnect.setObjectName("agentDisconnect")
        self.labelURI = QtGui.QLabel(AgentConfig)
        self.labelURI.setGeometry(QtCore.QRect(25, 127, 41, 20))
        self.labelURI.setObjectName("labelURI")
        self.agentTestResult = QtGui.QTextEdit(AgentConfig)
        self.agentTestResult.setGeometry(QtCore.QRect(180, 260, 111, 31))
        self.agentTestResult.setObjectName("agentTestResult")
        self.agentTest = QtGui.QPushButton(AgentConfig)
        self.agentTest.setGeometry(QtCore.QRect(30, 260, 98, 27))
        self.agentTest.setObjectName("agentTest")
        self.agentResources = QtGui.QComboBox(AgentConfig)
        self.agentResources.setGeometry(QtCore.QRect(290, 50, 151, 27))
        self.agentResources.setObjectName("agentResources")
        self.agentConnect = QtGui.QPushButton(AgentConfig)
        self.agentConnect.setGeometry(QtCore.QRect(30, 200, 98, 27))
        self.agentConnect.setObjectName("agentConnect")
        self.agentReconnect = QtGui.QPushButton(AgentConfig)
        self.agentReconnect.setGeometry(QtCore.QRect(180, 200, 98, 27))
        self.agentReconnect.setObjectName("agentReconnect")
        self.agentList = QtGui.QComboBox(AgentConfig)
        self.agentList.setGeometry(QtCore.QRect(90, 50, 78, 27))
        self.agentList.setObjectName("agentList")
        self.agentList.addItem("")
        self.agentUri = QtGui.QLineEdit(AgentConfig)
        self.agentUri.setGeometry(QtCore.QRect(80, 120, 361, 27))
        self.agentUri.setInputMethodHints(QtCore.Qt.ImhNone)
        self.agentUri.setObjectName("agentUri")
        self.labelResource = QtGui.QLabel(AgentConfig)
        self.labelResource.setGeometry(QtCore.QRect(220, 60, 71, 21))
        self.labelResource.setObjectName("labelResource")

        self.retranslateUi(AgentConfig)
        QtCore.QMetaObject.connectSlotsByName(AgentConfig)

    def retranslateUi(self, AgentConfig):
        AgentConfig.setWindowTitle(QtGui.QApplication.translate("AgentConfig", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.labelAgent.setText(QtGui.QApplication.translate("AgentConfig", "连接方式", None, QtGui.QApplication.UnicodeUTF8))
        self.agentDisconnect.setText(QtGui.QApplication.translate("AgentConfig", "断开连接", None, QtGui.QApplication.UnicodeUTF8))
        self.labelURI.setText(QtGui.QApplication.translate("AgentConfig", "URI", None, QtGui.QApplication.UnicodeUTF8))
        self.agentTestResult.setHtml(QtGui.QApplication.translate("AgentConfig", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">error or ok</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.agentTest.setText(QtGui.QApplication.translate("AgentConfig", "连接测试", None, QtGui.QApplication.UnicodeUTF8))
        self.agentConnect.setText(QtGui.QApplication.translate("AgentConfig", "建立连接", None, QtGui.QApplication.UnicodeUTF8))
        self.agentReconnect.setText(QtGui.QApplication.translate("AgentConfig", "重新连接", None, QtGui.QApplication.UnicodeUTF8))
        self.agentList.setItemText(0, QtGui.QApplication.translate("AgentConfig", "agent", None, QtGui.QApplication.UnicodeUTF8))
        self.labelResource.setText(QtGui.QApplication.translate("AgentConfig", "resource", None, QtGui.QApplication.UnicodeUTF8))

