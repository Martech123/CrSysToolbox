import collections
from c88xx_analyzer_base import C88xxAnalyzerBase

_PA = collections.namedtuple("_PA", "pa1 rfvga")
class PAInfo(object):
    # Gain PA1: {value(bit4, bit3): dB}
    GAIN_PA1 = {3:12.5, 2:9, 1:3.1}
    # Gain RFVGA: {value(bit2, bit1): dB}
    GAIN_RFVGA = {2:11.2, 1:8.5, 0:5.7}

    class PA(_PA):
        def __init__(self, *args, **kw):
            _PA.__init__(self, *args, **kw)
            self.value = PAInfo.get_pa_gain(self)

        def __str__(self):
            return "pa1:%s, rfvga:%s, Gain:%s" % (
                    bin(self.pa1), bin(self.rfvga), self.value)

    @classmethod
    def gen_pa_reg(cls, pa_item):
        pa1, rfvga = pa_item
        pa = 0x0200
        pa |= pa1 << 3
        pa |= rfvga << 1
        return pa

    @classmethod
    def gen_pa_item(cls, pa_reg):
        pa1 = (pa_reg >> 3) & 0x3
        rfvga = (pa_reg >> 1) & 0x3

        if cls.GAIN_PA1.has_key(pa1) and cls.GAIN_RFVGA.has_key(rfvga):
            return cls.PA(pa1 = pa1, rfvga = rfvga)
        else:
            return None

    @classmethod
    def get_pa_gain(cls, pa_item):
        pa1, rfvga = pa_item
        return cls.GAIN_PA1[pa1] + cls.GAIN_RFVGA[rfvga]

    @classmethod
    def get_pa_list(cls):
        '''
        PAList = [PA(...), ...]
        '''
        return [cls.PA(x, y) for x in cls.GAIN_PA1 for y in cls.GAIN_RFVGA]

_LNA = collections.namedtuple("_LNA", "lna1 lna2")
class LNAInfo(object):
    # Gain LNA1: {value(bit6): dB}
    GAIN_LNA1 = {0:-6, 1:18}
    # Gain LNA2: {value(bit5): dB}
    GAIN_LNA2 = {0:-6, 1:14}

    class LNA(_LNA):
        def __init__(self, *args, **kw):
            _LNA.__init__(self, *args, **kw)
            self.value = LNAInfo.get_lna_gain(self)

        def __str__(self):
            return "lna1:%s, lna2:%s, Gain:%s" % (
                    bin(self.lna1), bin(self.lna2), self.value)

    @classmethod
    def gen_lna_reg(cls, lna_item):
        lna1, lna2 = lna_item
        lna = 0x0200
        lna |= (lna1 & 0x1) << 6
        lna |= (lna2 & 0x1) << 5
        return lna

    @classmethod
    def gen_lna_item(cls, lna_reg):
        lna1 = (lna_reg >> 6) & 0x1
        lna2 = (lna_reg >> 5) & 0x1
        return cls.LNA(lna1 = lna1, lna2 = lna2)

    @classmethod
    def get_lna_gain(cls, lna_item):
        lna1, lna2 = lna_item
        return cls.GAIN_LNA1[lna1] + cls.GAIN_LNA2[lna2]

    @classmethod
    def get_lna_list(cls):
        '''
        LNAList  = [LNA(...), ...]
        '''
        return [cls.LNA(x, y) for x in cls.GAIN_LNA1 for y in cls.GAIN_LNA2]

'''
lo = LO()
# append value
lo.value = None | freq(MHz)
lo.r0 = None | r0
lo.r1 = None | r1
lo.r2 = None | r2
'''
_LO = collections.namedtuple("_LO", "div n")
class LOInfo(object):
    # Div list
    # LO_DIV: {reg: div}
    LO_DIV = {0:12, 1:8, 2:6, 3:4, 6:3, 7:2}
    # LO_DIV: {div:(freqStart(MHz), freqEnd(MHz))}
    LO_DIV_LIMIT = {
        2:(2300, 2700),
        3:(1300, 2700),
        4:(925, 1300),
        6:(700, 900),
        8:(425, 700),
        12:(320, 640),
    }

    class LO(_LO):
        def __init__(self, *args, **kw):
            _LO.__init__(self, *args, **kw)
            self.value = LOInfo.get_lo_freq(self)
            self.r0 = None
            self.r1 = None
            self.r2 = None

        def __str__(self):
            return "(div:%s, n:%d): %s" % (bin(self.div), self.n, self.value)

    @classmethod
    def get_lo_freq(cls, lo_item):
        div_reg, n = lo_item
        return 25.0 * (n & 0xff) / cls.LO_DIV[div_reg]

    @classmethod
    def get_lo_n_range(cls, div_reg):
        '''
        return (n_min, n_max)
        '''
        div = cls.LO_DIV[div_reg]
        limit = map(lambda f: int(f * div / 25), cls.LO_DIV_LIMIT[div])
        limit[1] = min(0xff, limit[1])
        return tuple(limit)

@C88xxAnalyzerBase.register("tuner")
class C89xxTuner(C88xxAnalyzerBase, PAInfo, LNAInfo, LOInfo):
    @staticmethod
    def between(start, end, aim):
        '''
        start = None or -inf
        end   = None or +inf
        between(None, None, freq) --> true
        '''
        if start and aim < start:
            return False
        if end and aim > end:
            return False
        return True

    def tuner_get(self, reg):
        return self.agent.get_tuner(reg)

    def tuner_set(self, reg, data):
        return self.agent.set_tuner(reg, data)

    def tuner_reset(self):
        return self.tuner_set(4, 0) and self.tuner_set(4, 1 << 7)

    def set_pa(self, pa_item):
        pa1, rfvga = pa_item
        ori_reg = self.tuner_get(2)
        if ori_reg is None:
            return None
        pa_item = (pa1, rfvga)
        pa_reg = self.gen_pa_reg(pa_item)

        mask = 0xf << 1
        ori_reg &= ~mask
        pa_reg &= mask
        return self.tuner_set(2, ori_reg | pa_reg)

    def get_pa(self):
        reg = self.tuner_get(2)
        if reg is None: return None
        return self.gen_pa_item(reg)

    def set_lna(self, lna_item):
        ori_reg = self.tuner_get(2)
        if ori_reg is None:
            return None

        lna_reg = self.gen_lna_reg(lna_item)

        mask = 0x3 << 5
        ori_reg &= ~mask
        lna_reg &= mask
        return self.tuner_set(2, ori_reg | lna_reg)

    def get_lna(self):
        reg = self.tuner_get(2)
        if reg is None: return None
        return self.gen_lna_item(reg)

    def get_lo(self):
        r0 = self.tuner_get(0)
        r1 = self.tuner_get(1)
        r2 = self.tuner_get(2)

        if None in (r0, r1, r2):
            return None
        n = (r1 & 0x7f) << 1 | (r2 & 0x80) >> 7
        div = (r0 >> 3) & 0x7
        # FIXME lo reg patch
        if div == 5:
            div = 3
        elif div == 4:
            div = 2
        lo = self.LO(div = div, n = n)
        lo.r0 = r0
        lo.r1 = r1
        lo.r2 = r2
        return lo

    def set_lo(self, lo_item):
        div, n = lo_item
        r0 = self.tuner_get(0) or 0xac
        r1 = self.tuner_get(1) or 0x50
        r2 = self.tuner_get(2) or 0x74

        r0_maks = 0x7 << 3
        r0 &= ~r0_maks
        r0 |= (div << 3) & r0_maks

        r1_mask = 0x7f
        r1 &= ~r1_mask
        r1 |= r1_mask & (n >> 1)

        r2_mask = 0x80
        r2 &= ~r2_mask
        r2 |= r2_mask & (n << 7)

        return self.tuner_set(0, r0) and \
            self.tuner_set(1, r1) and    \
            self.tuner_set(2, r2)

    def list_lo(self, freq_start = None, freq_end = None):
        '''
        return [LO(), ...]
        '''
        results = []
        # search list increase
        for reg, div in self.LO_DIV.iteritems():
            fs, fe = self.LO_DIV_LIMIT[div]
            # range check
            if not self.between(None, freq_end, fs):
                continue   # freq_end lower than fs
            if not self.between(freq_start, None, fe):
                continue # freq_star higher then fe

            n_min, n_max = self.get_lo_n_range(reg)
            for n in range(n_min, n_max + 1):
                result = self.LO(div = reg, n = n)
                if not self.between(freq_start, freq_end, result.value):
                    continue
                results.append(result)
        return results

if __name__ == "__main__":
    def assertNotNone(value):
        assert(value is not None)

    from c88xx_analyzer_base import C88xxAgentBase as AgentFactory
    agent = AgentFactory.get_agent("mmp://eth0")
    assertNotNone(agent)

    tuner = C89xxTuner(agent)
    tuner.tuner_reset()

    def get_set_test(tag, getter, setter):
        print "===== %s set/get =====" % tag
        ori = getter()
        print(tag + ":", str(ori))
        assertNotNone(ori)
        assertNotNone(setter(ori))
        now = getter()
        print(tag + "2:", str(now))
        assert(ori == now)

    from functools import partial
    get_set_test("reg",
            partial(tuner.tuner_get, 2),
            partial(tuner.tuner_set, 2))

    get_set_test("pa", tuner.get_pa, tuner.set_pa)
    assert(tuner.get_pa_list())

    get_set_test("lna", tuner.get_lna, tuner.set_lna)
    assert(tuner.get_lna_list())

    get_set_test("lo", tuner.get_lo, tuner.set_lo)
    print "===== lo list test ======"
    def test_list_lo(start, end):
        for lo in tuner.list_lo(start, end):
            div, n = lo
            value = lo.value
            # print(div, n, value)
            if not tuner.between(start, end, value):
                print(start, end, value)
                return False

            assert(n > 0)
            assert(n <= 0xff)
        return True

    assert(test_list_lo(None, None))
    assert(test_list_lo(400, None))
    assert(test_list_lo(None, 600))

    print "===== lo sortd demo ====="
    lo_list = tuner.list_lo(425, 640)
    for lo in sorted(lo_list, key = lambda lo: lo.value):
        div, n = lo
