from controller import ControllerBase

from PySide import QtCore, QtGui

import core
from core.agent import C88xxAgentBase as AgentFactory
from core.analyzer import C88xxAnalyzerBase as AnalyzerFactory

from ui.ui_agent_config import Ui_AgentConfig

@ControllerBase.bindUI(Ui_AgentConfig)
class AgentController(ControllerBase):
    agentAvailable = 1
    agentUnavailable = 0
    agentStateChange = QtCore.Signal(int)

    def __init__(self, **kw):
        ControllerBase.__init__(self, **kw)
        self.agent = None

        self.__genAgentList()
        self.__connectEnable(True)

    def getAnalyzer(self, analyzerName):
        return AnalyzerFactory.get_analyzer(analyzerName)

    def genOfflineAnalyzer(self, analyzerName):
        return AnalyzerFactory.gen_offline_analyzer(analyzerName)

    # ==================================
    # Setup & Inner Function
    # ==================================
    def __genAgentList(self):
        agentList = AgentFactory.list_agent()
        self.ui.agentList.clear()
        self.ui.agentList.addItems(agentList)
        self.agentList = agentList
        self.__genResourceList()
        self.__reflashResource()

    def __getCurrentAgentName(self):
        return self.agentList[self.ui.agentList.currentIndex()]

    def __getCurrentConfig(self):
        return str(self.ui.agentUri.text())

    def __getCurretnResourceName(self):
        return self.resourceList[self.ui.agentResources.currentIndex()]

    def __genResourceList(self):
        agentName = self.__getCurrentAgentName()
        agent = AgentFactory.get_agent(agentName)
        resources = agent.list_resource()
        nameList = resources.keys()
        descList = [resources[name] for name in nameList]

        self.ui.agentResources.clear()
        self.ui.agentResources.addItems(descList)

        self.resourceList = nameList
        self.resourceDict = resources

    def __reflashResource(self):
        name = self.__getCurretnResourceName()
        desc = self.resourceDict[name]
        info = "Name: %s\n-----------------\nDesc: %s" % (name, desc)
        self.ui.agentResources.setToolTip(info)

        oldCfg = self.__getCurrentConfig().split("/")
        oldCfg[0] = name
        newCfg = "/".join(oldCfg)
        self.ui.agentUri.setText(newCfg)

    def __connectEnable(self, b):
        self.ui.agentConnect.setEnabled(b)
        self.ui.agentDisconnect.setEnabled(not b)

        available = self.agentAvailable if not b else self.agentUnavailable
        self.agentStateChange.emit(available)

    # ==================================
    # Public function
    # ==================================
    def lockAgent(self):
        self.agentStateChange.emit(self.agentUnavailable)

    def unlockAgent(self):
        self.agentStateChange.emit(self.agentAvailable)

    # ==================================
    # Event Callback
    # ==================================
    @QtCore.Slot(int)
    def on_agentList_activated(self, value):
        self.__genResourceList()

    @QtCore.Slot(int)
    def on_agentResources_activated(self, value):
        self.__reflashResource()

    @QtCore.Slot()
    def on_agentConnect_clicked(self):
        if self.agent:
            self.logStatus("agent already opened")
            return

        agentName = self.__getCurrentAgentName()
        agentConfig = self.__getCurrentConfig()
        uri = "%s://%s" % (agentName, agentConfig)
        agent = AgentFactory.get_agent(agentName)
        print(uri)
        try:
            agent.open(uri)
        except Exception, e:
            self.logStatus("open agent fail: %s" % e)
            return

        self.agent = agent
        AnalyzerFactory.config_agent(self.agent)
        self.logStatus("open agent success: %s" % uri)
        self.__connectEnable(False)

    @QtCore.Slot()
    def on_agentDisconnect_clicked(self):
        if self.agent:
            self.agent.close()
        self.agent = None
        self.logStatus("agent close success")
        self.__connectEnable(True)

    @QtCore.Slot()
    def on_agentReconnect_clicked(self):
        self.ui.agentDisconnect.clicked.emit()
        self.ui.agentConnect.clicked.emit()

    @QtCore.Slot()
    def on_agentTest_clicked(self):
        res = ""
        if not self.agent:
            res = "Don't have agent"
        elif self.agent.get_oam(0x7e, 0xfd) is not None:
            res = "Success"
        else:
            res = "Fail"
        self.logStatus(res)
        self.ui.agentTestResult.setText(res)
