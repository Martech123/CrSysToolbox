import struct
import collections

from c88xx_analyzer_base import C88xxAnalyzerBase

class FreqResult(object):
    def __init__(self, val, opt):
        # val(value, opt)
        self.val = (val, opt)

    def __repr__(self):
        return "%s" % (self.get_val())

    def __str__(self):
        return "%.2f" % (self.get_val())

    def __eq__(self, obj):
        if not isinstance(obj, FreqResult):
            return False
        return self.get_opt() == obj.get_opt()

    def get_val(self):
        return self.val[0]

    def get_opt(self):
        return self.val[1]

@C88xxAnalyzerBase.register("frequency")
class C88xxFrequency(C88xxAnalyzerBase):
    FULL_PLL_LIST = [1, 2, 4]
    FULL_ADC_LIST = [6, 8]
    FULL_FC_LIST = range(1, 32)
    FULL_BW_LIST = [1, 2, 4, 8]

    COMMON_PLL_LIST = [1]
    COMMON_ADC_LIST = [8]
    COMMON_FC_LIST = range(1, 32)
    COMMON_BW_LIST = [1, 2, 4, 8]

    def __init__(self, agent = None, all_possibilities = False):
        C88xxAnalyzerBase.__init__(self, agent)
        self.agent = agent
        self.__a08 = 0x0
        self.__a13 = 0x0
        self.__a15 = 0x0
        self.__of9 = 0x0
        self.__reset_reg()

        self.__pll = None
        self.__adc = None
        self.__bw = None
        self.__fc = None
        self.__reset_dep_cfg("all")

        # inner list init
        if all_possibilities:
            pll_list = self.FULL_PLL_LIST
            adc_list = self.FULL_ADC_LIST
            bw_list  = self.FULL_BW_LIST
            fc_list  = self.FULL_FC_LIST
        else:
            pll_list = self.COMMON_PLL_LIST
            adc_list = self.COMMON_ADC_LIST
            bw_list  = self.COMMON_BW_LIST
            fc_list  = self.COMMON_FC_LIST

        self.__adc_list = adc_list
        self.__bw_list = bw_list
        self.__fc_list = fc_list
        self.__pll_list = filter(lambda opts: self._calc_pll(*opts) <= 2250 and
                                              self._calc_pll(*opts) >= 1200,
                                 [(n, a) for n in range(36, 79) for a in pll_list])

    # ==================================
    # Private Function
    # ==================================
    # convert reg(oam, ana) --> config
    # n: 0~255; a: [1, 2, 4]
    def _calc_pll(self, n, a):
        return (n + 12) * 25 /  a

    # n: [6, 8]
    def _calc_adc(self, pll, n):
        return pll / n

    # n: [1, 2, 4, 8]
    def _calc_bw(self, adc, n):
        theta = 1 + 2 ** -6
        return adc / (4 * n * theta)

    # n: 0x01 ~ 0x1f(31)
    def _calc_fc(self, adc, n):
        '''
        n = 0x01 ~ 0x1f
        [bit4, bit0]: [2 ** -2, 2 ** -6]
        '''
        def theta(n):
            nbit = ((n >> i) & 0x01 for i in range(5))
            theta = 0
            for i in nbit:
                theta = (theta / 2) + i * (2 ** -2)

            return theta
        return adc * theta(n)

    def _calc_range(self, bw, fc):
        # return (freqStart, freqEnd)
        fs = fc - (bw / 2)
        fe = fc + (bw / 2)
        return (fs, fe)

    def _get_pll(self):
        n = (self.__a08 >> 3) & 0xff
        a = (self.__a15 >> 4) & 0x3
        a = 2 ** a
        self.__pll = FreqResult(self._calc_pll(n, a), (n, a))

    def _get_adc(self):
        k = (self.__a08 >> 15) & 0x01
        if k == 1:
            k = 6
        else:
            k = 8
        pll = self.__pll.get_val()
        self.__adc = FreqResult(self._calc_adc(pll, k), k)

    def _get_fc(self):
        n = (self.__of9 >> 9) & 0x1f
        adc = self.__adc.get_val()
        self.__fc = FreqResult(self._calc_fc(adc, n), n)

    def _get_bw(self):
        ndict = {(0, 0, 0):1, (1, 0, 0):2, (1, 1, 0):4, (1, 1, 1):8}

        n2 = (self.__a13 >> 8) & 0x1
        n1 = (self.__a15 >> 1) & 0x1
        n0 = (self.__a15 >> 2) & 0x1

        n = ndict[(n2, n1, n0)]
        adc = self.__adc.get_val()
        self.__bw = FreqResult(self._calc_bw(adc, n), n)

    def _reg_to_cfg(self):
        self._get_pll()
        self._get_adc()
        self._get_bw()
        self._get_fc()

    # ------------------------
    # convert config --> reg(oam, ana)
    def _set_pll(self):
        n, a = self.__pll.get_opt()
        a = {1:0, 2:1, 4:2}[a]

        self.__a08 &= ~(0xff << 3)
        self.__a08 |= (n & 0xff) << 3

        self.__a15 &= ~(0x3 << 4)
        self.__a15 |= a << 4

    def _set_adc(self):
        k = self.__adc.get_opt()
        k = {6:1, 8:0}[k]

        self.__a08 &= ~(0x01 << 15)
        self.__a08 |= k << 15

    def _set_bd(self):
        ndict = {1:(0, 0, 0), 2:(1, 0, 0), 4:(1, 1, 0), 8:(1, 1, 1)}
        n = self.__bw.get_opt()
        n2, n1, n0 = ndict[n]

        self.__a13 &= ~(0x01 << 8)
        self.__a13 |= n2 << 8
        self.__a15 &= ~(0x03 << 1)
        self.__a15 |= n1 << 1
        self.__a15 |= n0 << 2

    def _set_fc(self):
        n = self.__fc.get_opt()
        self.__of9 &= ~(0x1f << 9)
        self.__of9 |= (n & 0x1f) << 9

    def _cfg_to_reg(self):
        self._set_pll()
        self._set_adc()
        self._set_bd()
        self._set_fc()

    # ------------------------
    # help function
    def __check_reg(self):
        return (self.__a08 and self.__a13 and self.__a15 and self.__of9)

    def __check_cfg(self):
        return (self.__pll and self.__adc and self.__fc and self.__bw)

    def __reset_dep_cfg(self, key):
        '''
        reset depended config
        key ::= all | pll | adc
        '''
        rst_pll = ["all"]
        rst_adc = ["all", "pll"]
        rst_bw  = ["all", "pll", "adc"]
        rst_fc  = ["all", "pll", "adc"]

        if key in rst_pll:
            self.__pll = None

        if key in rst_adc:
            self.__adc = None

        if key in rst_bw:
            self.__bw = None

        if key in rst_fc:
            self.__fc = None

    def __reset_reg(self):
        self.__a08 = 0x0000
        self.__a13 = 0x0000
        self.__a15 = 0x0000
        self.__of9 = 0x0000

    def __get_online_cfg(self):
        self.__reset_reg()
        self.__a08 = self.agent.get_ana(0x08)
        self.__a13 = self.agent.get_ana(0x13)
        self.__a15 = self.agent.get_ana(0x15)
        self.__of9 = self.agent.get_oam(0x7e, 0xf9)

    # ==================================
    # Public Function
    # ==================================
    def get_pll(self):
        return self.__pll

    def get_adc_clock(self):
        return self.__adc

    def get_bandwidth(self):
        return self.__bw

    def get_cent_freq(self):
        return self.__fc

    # -------------------------
    # helper
    def get_range(self):
        '''
        return (float(freq_start), float(freq_end))
        '''
        if not (self.__bw and self.__fc):
            return (None, None)
        bw = self.__bw.get_val()
        fc = self.__fc.get_val()
        return self._calc_range(bw, fc)

    # ------------------------
    # list items, [] or [....]
    def list_pll(self):
        return [FreqResult(self._calc_pll(*opts), opts)
                 for opts in self.__pll_list]

    def list_adc_clock(self):
        if not self.__pll:
            return []
        pll = self.__pll.get_val()
        return [FreqResult(self._calc_adc(pll, x), x)
                 for x in self.__adc_list]

    def list_adc_clock_by_pll(self, pll):
        '''
        helper function, usually for COMMON config
        list adc by input pll
        pll: getting from list_pll()
        '''
        pll = pll.get_val()
        return [FreqResult(self._calc_adc(pll, x), x)
                 for x in self.__adc_list]

    def list_adc_clock_all(self):
        '''
        helper function, usually for COMMON config
        list adc for all the pll
        return: [(pll, adc), ...]
        '''
        pll_list = self.list_pll()
        result = []
        for pll in pll_list:
            for adc in self.list_adc_clock_by_pll(pll):
                tmp = (pll, adc)
                result.append(tmp)
        return result

    def list_bandwidth(self):
        if not self.__adc:
            return []
        adc = self.__adc.get_val()
        return [FreqResult(self._calc_bw(adc, x), x)
                 for x in self.__bw_list]

    def list_cent_freq(self):
        if not self.__bw:
            return []
        adc = self.__adc.get_val()
        bw = self.__bw.get_val()
        full_list = [FreqResult(self._calc_fc(adc, x), x) for x in self.__fc_list]
        def check_range(fc_res):
            fc =  fc_res.get_val()
            fs, fe = self._calc_range(bw, fc)
            return fs > 0 and fe < adc / 2
        return filter(check_range, full_list)

    def set_pll(self, pll):
        if pll.get_opt() not in self.__pll_list:
            return False

        if pll != self.__pll:
            self.__reset_dep_cfg("pll")
        self.__pll = pll
        return True

    def set_adc_clock(self, adc_clk):
        if adc_clk.get_opt() not in self.__adc_list:
            return False

        if adc_clk != self.__adc:
            self.__reset_dep_cfg("adc")

        self.__adc = adc_clk
        return True

    def set_bandwitdth(self, bw):
        if bw.get_opt() not in self.__bw_list:
            return False

        self.__bw = bw
        return True

    def set_cent_freq(self, fc):
        if fc.get_opt() not in self.__fc_list:
            return False

        self.__fc = fc
        return True

    # ------------------------
    # online function
    # getting ALL the info
    def get_online_frequency(self):
        self.__get_online_cfg()
        if not self.__check_reg():
            return False

        # convert reg --> cfg
        self._reg_to_cfg()
        return True

    def apply_frequency(self):
        if not self.__check_cfg():
            return False

        self.__get_online_cfg()
        if not self.__check_reg():
            return False

        self._cfg_to_reg()

        # apply
        if not self.agent.set_ana(0x08, self.__a08):
            return False

        if not self.agent.set_ana(0x13, self.__a13):
            return False

        if not self.agent.set_ana(0x15, self.__a15):
            return False

        if not self.agent.set_oam(0x7e, 0xf9, self.__of9):
            return False
        return True

    # ------------------------
    # offline function
    # Config pakc & unpack
    Config = collections.namedtuple("Config", "a08 a13 a15 of9")
    Config.pattern = "HHHH"
    @classmethod
    def _pack_config(cls, cfg):
        return struct.pack(cls.Config.pattern, *cfg)

    @classmethod
    def _unpack_config(cls, packed_cfg):
        Config = cls.Config
        return Config(*struct.unpack(Config.pattern, packed_cfg))

    def set_offline_frequency(self, a08, a13, a15, of9):
        self.__reset_reg()
        self.__a08 = a08 & 0xffff
        self.__a13 = a13 & 0xffff
        self.__a15 = a15 & 0xffff
        self.__of9 = of9 & 0xffff
        if not self.__check_reg():
            return False

        self._reg_to_cfg()
        return True

    def dump_registers(self):
        return self.Config(
                a08 = self.__a08, a13 = self.__a13,
                a15 = self.__a15, of9 = self.__of9)

    def save_frequency(self, path):
        if not self.__check_cfg():
            return False

        self._cfg_to_reg()
        if not self.__check_reg():
            return False

        cfg = self.dump_registers()
        packed_cfg = self._pack_config(cfg)
        with open(path, "wb") as f:
            f.write(packed_cfg)
        return True

    def load_frequency(self, path):
        self.__reset_reg()
        with open(path, "rb") as f:
            cfg = self._unpack_config(f.read())

        if not cfg:
            return False
        self.set_offline_frequency(cfg.a08, cfg.a13, cfg.a15, cfg.of9)
        return True

if __name__ == "__main__":
    def dump_freq(freq):
        print "----- dump freq -----"
        pll = freq.get_pll()
        adc = freq.get_adc_clock()
        bw = freq.get_bandwidth()
        fc = freq.get_cent_freq()
        print("pll", pll)
        print("adc", adc)
        print("bw", bw)
        print("fc", fc)
        return (pll, adc, bw, fc)

    from c88xx_analyzer_base import C88xxAgentBase as AgentFactory
    mmp_agent = AgentFactory.get_agent("mmp://eth0")
    freq = C88xxFrequency(mmp_agent)

    print "========= Start offline config test =========="
    freq.set_offline_frequency(0x29e3, 0x5e60, 0x1, 0x1600)
    path = "/tmp/freq_save.log"
    info = dump_freq(freq)
    assert(freq.save_frequency(path))
    assert(freq.load_frequency(path))
    info2 = dump_freq(freq)
    assert(info == info2)

    print "========= Start online config test =========="
    assert(freq.get_online_frequency())
    print("test get frequency")
    dump_freq(freq)

    print("test list cfg")
    assert(freq.set_pll(pll))
    print("pll_list", len(freq.list_pll()))
    assert(freq.set_adc_clock(adc))
    print("adc_list", len(freq.list_adc_clock()))
    assert(freq.set_bandwitdth(bw))
    print("bw_list", len(freq.list_bandwidth()))
    assert(freq.set_cent_freq(fc))
    print("fc_list", len(freq.list_cent_freq()))

    print("test apply frequency")
    assert(freq.apply_frequency())
