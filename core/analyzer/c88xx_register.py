from c88xx_analyzer_base import C88xxAnalyzerBase

@C88xxAnalyzerBase.register("register")
class C88xxRegister(C88xxAnalyzerBase):
    def get_oam(self, *args, **kw):
        return self.agent.get_oam(*args, **kw)

    def set_oam(self, *args, **kw):
        return self.agent.set_oam(*args, **kw)

    def get_ana(self, *args, **kw):
        return self.agent.get_ana(*args, **kw)

    def set_ana(self, *args, **kw):
        return self.agent.set_ana(*args, **kw)

if __name__ == "__main__":
    from c88xx_analyzer_base import C88xxAgentBase as AgentFactory
    mmp_agent = AgentFactory.get_agent("mmp://eth0")

    register = C88xxRegister()
    register.set_agent(mmp_agent)

    # oam test
    llid = 0x7e
    reg = 0xce
    val = 0x0001
    register.set_oam(llid, reg, val)
    print(register.get_oam(llid, reg))
