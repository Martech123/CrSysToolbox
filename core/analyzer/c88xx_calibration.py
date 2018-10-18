import visa
import time

import platform
from c88xx_analyzer_base import C88xxAnalyzerBase
from c89xx_tuner import PAInfo

# BACKEND pyvisa-py
_PYVISA_BACKEND = "@py"
_READ_TERMINATION = ""

class VisaLib(object):
    def __init__(self):
        self.rm = visa.ResourceManager(_PYVISA_BACKEND)
        self.instrument = None
        self.target = None

    def __del__(self):
        if self.instrument != None:
            self.instrument.close()
            self.instrument = None

    def opensource(self, target):
        self.target = target
        self.instrument = self.rm.open_resource(target)
        self.instrument.read_termination = _READ_TERMINATION

    def reconnect(self):
        time.sleep(0.5)
        if self.instrument != None:
            self.instrument.close()
        self.rm.close()
        self.rm = visa.ResourceManager()
        self.instrument = self.rm.open_resource(self.target)
        self.instrument.read_termination = _READ_TERMINATION

    def closesource(self):
        time.sleep(0.5)
        self.instrument.close()
        self.instrument = None

    def close(self):
        time.sleep(0.5)
        self.instrument.close()

    def reopen(self):
        self.instrument.open()
        self.instrument.read_termination = _READ_TERMINATION

    def write(self, data = ''):
        self.instrument.write(data)

    def query(self, data = ''):
        return self.instrument.query(data)


class N9344C(VisaLib):
    def opensource(self, target= 'TCPIP::192.168.36.109::inst0::INSTR'):
        super(N9344C, self).opensource(target)
        self.instrument.write_termination = '\n'

    def reset(self):
        #Clears the Analyzer
        self.write('*CLS')
        #Resets the Analyzer
        self.write('*RST')

    def setup(self):
        #Set Y-Axis units to dBm
        self.write('UNIT:POW DBM')
        #Set analyzer to continue sweep mode
        self.write('INIT:CONT 1')
        #Set the peak excursion
        self.write('CALC:MARK:PEAK:EXC %1fDB'%(0))
        #Set the peak thresold
        self.write('CALC:MARK:PEAK:THR -30')
        #Set continuous Peaking Maker
        self.write('CALC:MARK:CPEak ON')

    def set_freq(self, cent, span):
        #Set the analyzer center frequency to 30MHz
        self.write('SENS:FREQ:CENT %E' % cent)
        #Set th analyzer span to 50MHz
        self.write('SENS:FREQ:SPAN %E' % span)
        #Externally route the 50MHz Sgnal
        self.write('CAL:SOUR:STAT ON')
        time.sleep(1)

    def calc_peak(self):
        #Set the marker to the maximum peak
        self.write('CALC:MARK:MAX')

    def get_peak_x(self):
        #Query and read the maximum peak
        fre = float(self.query('CALC:MARK:X?'))
        return fre

    def get_peak_y(self):
        return float(self.query("CALC:MARK:Y?"))

    def get_attn(self):
        #query and read the marker amplitude
        attenulate = float(self.query('CALC:MARK:Y?'))
        return attenulate

    def set_bw(self,bw):
        #set band
        self.write('SENS:BANDwidth:RESolution %E' % bw)

    def set_sweep(self, time):
        #set sweep time (s)
        self.write('SENS:SWEep:TIME %E' % time)

    def set_refer_level(self, refval):
        #set reference level (dBm)
        self.write('DISPlay:WINDow:TRACe:Y:RLEVel %E' % refval)

    def set_refer_attenuation(self, refatt):
        #set reference Atten (dBm)
        self.write('SENS:POWer:ATTenuation %E' % refatt)

    def set_refer_attenuation_atuo(self, b):
        self.write("SENS:POWer:ATTenuation:AUTO %d" % b)

    def set_high_sensitivity(self, state):
        #set Hi-Sensitive state
        self.write('SENS:POWer:HSENsitive %E' % state)

class PAReport(object):
    class ReportItem(object):
        gain_cls = PAInfo
        def __init__(self, pa, peak):
            self.pa1, self.rfvga = pa
            self.peak = peak
            self.ref_reg = self.gain_cls.gen_pa_reg(pa)
            self.ref_gain = self.gain_cls.get_pa_gain(pa)

        @classmethod
        def _get_pa1_info(cls, pa1):
            pa_single = "b{:02b} ({:.2f}dB)"
            return pa_single.format(pa1, cls.gain_cls.GAIN_PA1[pa1])

        @classmethod
        def _get_rfvag_info(cls, rfvga):
            pa_single = "b{:02b} ({:.2f}dB)"
            return pa_single.format(rfvga, cls.gain_cls.GAIN_RFVGA[rfvga])

        # report return string
        def report(self):
            pa1_info = self._get_pa1_info(self.pa1)
            rfvag_info = self._get_rfvag_info(self.rfvga)
            return "0x%04x,\t%s,\t%s,\t%s,\t%s,\t" % (
              self.ref_reg, pa1_info, rfvag_info, self.ref_gain, self.peak)

        def report_diff(self, another):
            pa1_info = self._get_pa1_info(self.pa1)
            rfvag_info = self._get_rfvag_info(self.rfvga)
            return "0x%04x,\t%s,\t%s,\t%s,\t%s,\t" % (
                  self.ref_reg, pa1_info, rfvag_info,
                  self.ref_gain - another.ref_gain, self.peak - another.peak)

    def __init__(self):
        self._report_list = []
        self._report_dict = {}

    def add(self, pa_item, peak):
        item = self.ReportItem(pa_item, peak)
        self._report_list.append(item)
        self._report_dict[(item.pa1, item.rfvga)] = item

    def _get_report_by_idx(self, idx):
        if idx < 0:
            return None

        if idx > len(self._report_list) - 1:
            return None

        return self._report_list[idx]

    def _get_report_by_pa(self, p, r):
        pa = (p, r)
        return self._report_dict[pa]

    def report(self, idx = None):
        report_list = []
        if idx:
            report = self._get_report_by_idx(idx)
            if report: report_list.append(report)

        if not report_list:
            report_list = self._report_list

        result = ["[%d]\t%s" % (i, r.report()) for i, r in enumerate(report_list)]
        return reduce(lambda x, y: "%s\n%s" % (x, y), result)

    def count(self):
        return len(self._report_list)

    '''
    idx:  the reference data idx
    idxs: aim to diff list
    '''
    def report_diff(self, idx, idxs = None):
        report = self._get_report_by_idx(idx)
        if not report:
            return None

        report_list = self._report_list

        result = []
        for i, r in enumerate(report_list):
            if i == idx:
                head = "[*]\t"
            else:
                head = "[%d]\t" % i

            result.append("%s%s" % (head, r.report_diff(report)))
        return reduce(lambda x, y: "%s\n%s" % (x, y), result)

    def report_table(self, sort_by = "P"):
        pa1_list = sorted(PAInfo.GAIN_PA1)
        rfvga_list = sorted(PAInfo.GAIN_RFVGA)

        row = rfvga_list
        col = pa1_list
        info = "PA\\RFVGA"
        if sort_by != "P":
            row, col = col, row
            info = "RFVGA\\PA"

        result = []
        head = "{}\t{:02b}\t{:02b}\t{:02b}"
        body = "{:02b}      \t{:.2f}\t{:.2f}\t{:.2f}"

        result.append(head.format(info, *row))
        for c in col:
            l = []
            for r in row:
                if sort_by == "P":
                    pa = (c, r)
                else:
                    pa = (r, c)

                rpt = self._get_report_by_pa(*pa)
                l.append(rpt.peak)
            result.append(body.format(c, *l))
        return reduce(lambda x, y: "%s\n%s" % (x, y), result)

@C88xxAnalyzerBase.register("calibration")
class C88xxCalibrator(C88xxAnalyzerBase, PAInfo):
    # ------------------------------------------------------
    # constructor
    # ------------------------------------------------------
    def __init__(self, agent = None):
        C88xxAnalyzerBase.__init__(self, agent)
        self.visa_device = N9344C()
        self._device_on = False
        self.atten_db = 10

    # ------------------------------------------------------
    # private method
    # ------------------------------------------------------
    # for device
    def __reset_device(self):
        device = self.visa_device
        # device.set_high_sensitivity(0)
        device.set_freq(1.0155e9, 100e6)
        device.set_sweep(0.5)
        device.set_refer_attenuation_atuo(1)
        device.set_refer_level(40 - self.atten_db)

    # return Peak(dBm)
    def __get_peak(self):
        device = self.visa_device
        time.sleep(1)
        device.calc_peak()
        time.sleep(0.5)
        return device.get_peak_y()

    # ------------------------------------------------------
    # for c88xx
    def __reset_c88xx(self):
        agent = self.agent
        e1 = agent.get_oam(0x7e, 0xe1)
        if not e1:
            return False

        # setup single-frequency
        e1 &= ~0x00ff
        e1 |= 0x0060
        agent.set_oam(0x7e, 0xe1, e1)

    def __set_pa(self, pa_reg):
        reg = (pa_reg >> 8) & 0xff
        data = pa_reg & 0xff
        return self.agent.set_tuner(reg, data)

    # ------------------------------------------------------
    # public method
    # ------------------------------------------------------
    def set_attenuation(self, db):
        if db not in [10 , 20 , 30]:
            db = 10

        self.atten_db = db
    def get_attenuation(self):
        return self.atten_db

    def connet_device(self, ip):
        target = "TCPIP::%s::inst0::INSTR" % ip
        self.visa_device.opensource(target = target)
        self.visa_device.reset()
        self._device_on = True

    def disconnect_device(self):
        self.visa_device.closesource()
        self._device_on = False

    def is_device_available(self):
        return self._device_on

    '''
    pa: pa item, can be getted from get_pa_list
    '''
    def calibrate_pa(self, pa = None):
        self.__reset_c88xx()
        self.__reset_device()
        if pa:
            pa_list = []
            pa_list.append(pa)
        else:
            pa_list = self.get_pa_list()
        report = PAReport()
        for pa in pa_list:
            reg_pa = self.gen_pa_reg(pa)
            if not self.__set_pa(reg_pa):
                continue

            peak = self.__get_peak()
            if peak is None:
                continue
            report.add(pa, peak)

        return report

if __name__ == "__main__":
    from c88xx_analyzer_base import C88xxAgentBase as AgentFactory
    agent = AgentFactory.get_agent("mmp://eth0")

    calibrator = C88xxCalibrator(agent)
    calibrator.connet_device("192.168.36.109")

    reports = calibrator.calibrate_pa()
    print(reports.report())
    print("diff")
    print(reports.report_diff(0))
    print(reports.report_table("P"))
    print(reports.report_table("R"))
