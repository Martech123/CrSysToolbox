from c88xx_analyzer_base import C88xxAnalyzerBase

@C88xxAnalyzerBase.register("power")
class C88xxPower(C88xxAnalyzerBase):
    # dBuv: E1_H8
    power_dict = {
        114: 0x10,
        113: 0x20,
        112: 0x30,
        111: 0x40,
        110: 0x51,
        108: 0x11,
        107: 0x21,
        106: 0x31,
        105: 0x02,
        104: 0x52,
        102: 0x12,
        101: 0x22,
        100: 0x32,
        99 : 0x03,
        98 : 0x53,
        96 : 0x13,
        95 : 0x23,
        94 : 0x33,
        93 : 0x43,
    }

    reg_dict = dict((v,k) for k,v in power_dict.iteritems())

    @staticmethod
    def dBuv2dBm(dBuv):
        return dBuv - 107

    @staticmethod
    def dBm2dBuv(dBm):
        return dBm + 107

    # ==================================
    # Public Function
    # ==================================
    def get_power(self):
        e1 = self.agent.get_oam(0x7e, 0xe1)
        if e1 is None:
            return None

        reg_pow = (e1 >> 8) & 0xff
        return self.dBuv2dBm(self.reg_dict[reg_pow])

    def set_power(self, dBm):
        dBuv = self.dBm2dBuv(dBm)
        reg_pow = self.power_dict[dBuv]
        e1 = self.agent.get_oam(0x7e, 0xe1)
        if e1 is None:
            return None

        e1 &= ~0xFF00
        e1 |= (reg_pow & 0xff) << 8
        return self.agent.set_oam(0x7e, 0xe1, e1)

    def list_power(self):
        return sorted(map(self.dBuv2dBm, self.power_dict), reverse=True)

    def get_power_info(self, dBm):
        dBuv = self.dBm2dBuv(dBm)
        reg = self.power_dict.get(dBuv, None)
        if not reg:
            return None
        else:
            return "dBm %s, dBuv %s, reg %sXX" % (dBm, dBuv, hex(reg))

if __name__ == "__main__":
    from c88xx_analyzer_base import C88xxAgentBase as AgentFactory
    mmp_agent = AgentFactory.get_agent("mmp://eth0")

    power = C88xxPower()
    power.set_agent(mmp_agent)
    print(power.list_power())
    power_dbm = power.get_power()
    print(power_dbm)
    assert(power_dbm != None)
    assert(None != power.set_power(power_dbm))
