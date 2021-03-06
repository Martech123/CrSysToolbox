import math
import numpy as np
from functools import partial
from c88xx_analyzer_base import C88xxAnalyzerBase

# ==================================
# Constant
# ==================================
# REG 2001 --> Trigger Clock Selection
TC_ADC = 0x00000000
TC_PHY = 0x00000010

# REG 2002 --> Trigger Event Selection
TE_BASE     = 0x0001 # ????
TE_TX_OV    = (0x8000 << 16) | TE_BASE
TE_RX_OV    = (0x4000 << 16) | TE_BASE
TE_OV       = (0x2000 << 16) | TE_BASE
TE_OV_PRE   = (0x1000 << 16) | TE_BASE
TE_LDPC_ERR = (0x0800 << 16) | TE_BASE
TE_CRX_DV   = (0x0400 << 16) | TE_BASE # after ldpc decode
TE_HD_RST   = (0x0200 << 16) | TE_BASE
TE_E1       = (0x0100 << 16) | TE_BASE
# E1 setting when trigger event is TE_E1
E1_FG_FFT       = 0
E1_FG_DSM       = 1
E1_FG_UP        = 2
E1_FG_DOWN      = 3
E1_FG_CRC_ERR   = 4
E1_FG_RX        = 5
E1_LDPC_OUT_ERR = 6
E1_CRX_DV       = 7

# REG 2004 --> Trigger Point Selection
TP_RX_ADC     = 1  << 24
TP_FFT_SEL_IN = 4  << 24  # befor RX select
TP_RX_FROUT   = 8  << 24
TP_RX_RFTFR   = 16 << 24
TP_TX_IFFT    = 4  << 16
TP_TX_IIR     = 8  << 16
TP_TX_FROUT   = 64 << 16
TP_SIZE_2048 = 0x000007ff # ADC only have 2048
TP_SIZE_8192 = 0x00001fff

# REG 2005 --> Trigger Mode Selection
TM_EN_DELAY  = 1 << 31
TM_EN_NORMAL = 0 << 31
TM_MODE_AUTO      = 0 << 29
TM_MODE_SINGLE    = 1 << 29
TM_MODE_TR_SINGLE = 2 << 29 # Trigger + Single
TM_MODE_TR_NORMAL = 3 << 29 # Trigger + Normal

'''
# Usage: C88xxDebugcoreEvent

## init event
### set with func(Recommend)
    event = C88xxDebugcoreEvent()
    func = "func_name" # which in func_list[]
    pre_points = None  # if ADC pre_points < 2047, ELSE pre_points < 8192
    event.set_func(func, pre_points)

### set with event
    event = C88xxDebugcoreEvent()
    trigger_event = "event" # which in TE[]
    trigger_point = "point" # which in TP[]
    trigger_mode  = "mode"  # which in TM[]
    event._set_event(trigger_event)
    event._set_point(trigger_point)
    event._set_mode(trigger_mode)

### set with E1
    event = C88xxDebugcoreEvent()
    trigger_event = "E1"
    event._set_event(trigger_event)

    event._set_e1_change(E1_FG_UP, "event") # only set E1 event
or
    event._set_e1_change(0x1102, "replace") # replace whole REG_e1

    event._set_point(trigger_point)
    trigger_mode  = "mode"  # which in TM[]

    trigger_point = "point" # which in TP[]
    event._set_mode(trigger_mode)


## trigger & formate
    def dosomething(xdata):
        # xdata is uint16[]
        do something
        if success:
            return list[]
        else:
            return None

    formater = dosomething  # or None
    analyzer.trigger(event, formater)
'''
class C88xxDebugcoreEvent(object):
    func_list = {
        # "func_name":(event, e1_value, e1_opt, point, mode,  pre_points),
        "rx_fftout_error":("LDPC_ERR", None,       None,      "RX_RFTFR",   "TRIGGER", 0x10ff),
        "rx_fftout":      ("OV_PRE",   None,       None,      "RX_RFTFR",   "TRIGGER", 0x800),
        "fgup_rx_iir":    ("E1",       E1_FG_UP,   "event",   "FFT_SEL_IN", "TRIGGER", 0x89f),
        "fgup_rx_adc":    ("E1",       0x1102,     "replace", "RX_ADC",     "TRIGGER", 0x500),
        "rx_adc"     :    ("OV_PRE",   None,       None,      "RX_ADC",     "NORMAL",  0x0000),
        "tx_iir"     :    ("OV_PRE",   None,       None,      "TX_IIR",     "TRIGGER", 0x500),
        "fg_dsm_rx_adc":  ("E1",       E1_FG_DSM,  "event",   "RX_ADC",     "TRIGGER", 0x500),
        "ldpc_err_rx_adc":("E1",       E1_LDPC_OUT_ERR, "event", "RX_ADC",  "TRIGGER", 0x500),
    }

    TE = {
        "TX_OV"    : TE_TX_OV,
        "RX_OV"    : TE_RX_OV,
        "OV"       : TE_OV,
        "OV_PRE"   : TE_OV_PRE,
        "LDPC_ERR" : TE_LDPC_ERR,
        "CRX_DV"   : TE_CRX_DV,
        "HD_RST"   : TE_HD_RST,
        "E1"       : TE_E1,
    }

    TP = {
        "RX_ADC"     : TP_RX_ADC,
        "FFT_SEL_IN" : TP_FFT_SEL_IN,
        "RX_FROUT"   : TP_RX_FROUT,
        "RX_RFTFR"   : TP_RX_RFTFR,
        "TX_IFFT"    : TP_TX_IFFT,
        "TX_IIR"     : TP_TX_IIR,
        "TX_FROUT"   : TP_TX_FROUT,
    }

    TM = {
        "NORMAL"  : TM_EN_NORMAL | TM_MODE_AUTO,
        "TRIGGER" : TM_EN_DELAY | TM_MODE_TR_SINGLE,
    }

    def __init__(self):
        self.__e1_change = None
        self.__tr_event = None
        self.__tr_clock = None
        self.__tr_point = None
        self.__tr_mode = None
        self.__tp_size = None
        pass

    def set_func(self, func, pre_points = None):
        info = self.func_list.get(func)
        assert(info is not None)
        event, e1_value, e1_opt, point, mode, default_pre_points = info
        self._set_event(event)
        if event == "E1":
            self._set_e1_change(e1_value, e1_opt)

        self._set_point(point)
        self._set_mode(mode, pre_points or default_pre_points)

    # setter
    def _set_event(self, event):
        self.__tr_event = self.TE[event]

    def _set_point(self, point):
        if point == "RX_ADC":
            tp_size = TP_SIZE_2048
            self.__tp_size = 2048
            self.__tr_clock = TC_ADC
        else:
            tp_size = TP_SIZE_8192
            self.__tp_size = 8192
            self.__tr_clock = TC_PHY

        self.__tr_point = self.TP[point] | tp_size

    def _set_mode(self, mode, pre_points):
        self.__tr_mode = self.TM[mode] | pre_points

    '''
    only be called when setting E1_event, and which is necessary
    '''
    def _set_e1_change(self, e1_value, opt = "event"):
        def e1_change(e1_ori):
            if opt == "replace":
                return e1_value
            elif opt == "event":
                return e1_ori & 0xfff0 | e1_value
            else:
                return 0x1006

        self.__e1_change = e1_change

    # getter
    def _get_max_size(self):
        return self.__tp_size

    def _get_clock(self):
        return self.__tr_clock

    def _get_event(self):
        return self.__tr_event

    def _get_point(self):
        return self.__tr_point

    def _get_mode(self):
        return self.__tr_mode

    def _is_e1_event(self):
        return self.__tr_event == self.TE["E1"]

    '''
    Only when trigger event is E1_event and e1_irq has been setting
    '''
    def _get_e1_change(self):
        return self.__e1_change

@C88xxAnalyzerBase.register("debugcore")
class C88xxAnalyzer(C88xxAnalyzerBase):
    def __init__(self, agent = None):
        C88xxAnalyzerBase.__init__(self, agent)

        # math deal
        self.last_amp = 0
        self.adc_input_table = [60,65,70,75,80,85,90,95]
        self.adc_output_table = [8.0, 12.7,21.4,37.0,66.0,117.0,205.0,358.0]
        self.dbgc_data_average = 0
        self.dbgc_data_db_average = 0
        self.dbgc_last_data = []


        self.formater = {
            # formater:(event, formater)
            "fgup_rx_iir":     ("fgup_rx_iir", None),
            "tx_iir":          ("tx_iir", None),

            # adc
            "rx_adc":          ("rx_adc", self.adc_data_transform),
            "fgup_rx_adc":     ("fgup_rx_adc", self.adc_data_transform),
            "fg_dsm_rx_adc":   ("fg_dsm_rx_adc", self.adc_data_transform),
            "ldpc_err_rx_adc": ("ldpc_err_rx_adc", self.adc_data_transform),

            # fft
            "online_frequency":("rx_fftout", partial(self.channel_formater, type = 2)),
            "online_frequency_error":
                              ("rx_fftout_error", partial(self.channel_formater, type = 2)),
            "online_eye":      ("rx_fftout", partial(self.channel_formater, type = 1)),
            "online_eye_error":("rx_fftout_error", partial(self.channel_formater, type = 1)),
        }
    # ==================================
    # Data Deal
    # ==================================
    # ---- for adc -----------
    def linear_interpolation(self, data):
        index = 0
        for i in range(len(self.adc_output_table)):
            if(self.adc_output_table[i]) <= data:
                index = i
        if self.adc_output_table[index-1] == data:
            return self.adc_output_table[index]
        else:
            if index == len(self.adc_output_table) - 1:
                index -= 1
            af = math.log((data/self.adc_output_table[index]),(self.adc_output_table[index + 1]/self.adc_output_table[index]))
            return af*(self.adc_input_table[index+1]-self.adc_input_table[index])+ self.adc_input_table[index]

    def get_agc_amp(self):
        agc_set = self.agent.get_oam( 0x7e, 0xdc)
        agc = self.agent.get_oam(0x7e, 0x85)
        gd = self.agent.get_oam(0x7e, 0x8a)
        agc_1 = 0
        agc_2 = 0
        if agc != None:
            agc_1 = agc & 0xf
            agc_2 = (agc >> 4)-1
        if agc_set != None:
            if (agc_set>>5) != 0:
                agc_1 = (agc_set>>5) & 0xf
            if agc_set & 0x1f != 0:
                agc_2 = agc_set & 0x1f
        # unit db
        self.last_amp = 26 - (agc_1)*3 - (agc_2)*2/3

    def agc_read_avg_2_dB(self, data):
        self.get_agc_amp()
        if data == 0:
            ret_db = 0
        else:
            ret_db = self.linear_interpolation(data)
            ret_db = ret_db + self.last_amp
        return ret_db

    def adc_data_transform(self, data):
        for i in range(len(data)):
            if data[i] > 0x400:
                data[i] = data[i] & 0x7fe
                data[i] = data[i] >> 1
                data[i] = data[i] - 0x400
            else:
                data[i] = data[i] >> 1
        if len(data) > 0:
            self.dbgc_data_average = math.sqrt((sum(map(lambda x:x *x,data)) - sum(data) * sum(data) / len(data))/len(data))
            self.dbgc_data_db_average = self.agc_read_avg_2_dB(self.dbgc_data_average)
        return data

    # ---- for fft -----------
    F = [
        [-0.339745580000000+0.237908360000000j,0.274224600000000-0.117975590000000j,1.00000000000000-0.205321280000000j,0.0566232880000000+0.0847366050000000j,0.00930407350000000-0.000809176510000000j,0.000187633220000000-0.00184485030000000j],
        [-0.362672940000000+0.382311160000000j,0.175071660000000-0.121615930000000j,1.00000000000000-0.426762800000000j,0.170290520000000+0.168751330000000j,0.0176702590000000-0.00522702820000000j,-0.000352281210000000-0.00352889540000000j],
        [-0.189454580000000+0.302064240000000j,-0.166383410000000+0.173384150000000j,1.00000000000000-0.687411110000000j,0.334890490000000+0.220365430000000j,0.0210620410000000-0.0111389720000000j,-0.00129618360000000-0.00421464770000000j],
        [0.0184387610000000-0.0484572160000000j,-0.539754220000000+0.845409030000000j,0.973532900000000-1.00000000000000j,0.530520360000000+0.215233520000000j,0.0173431030000000-0.0141124970000000j,-0.00185801890000000-0.00344233770000000j],
        [0.0412097800000000-0.240737600000000j,-0.392651150000000+1.00000000000000j,0.584238890000000-0.895782120000000j,0.758015330000000+0.146844990000000j,0.00936897050000000-0.0112669200000000j,-0.00151871260000000-0.00184385350000000j],
        [0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,1.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j],
        [0.000248602360000000+0.0435534360000000j,-0.00815400230000000+0.0406285960000000j,1.00000000000000-0.190775510000000j,-0.0269248330000000+0.0829619090000000j,0.0297979330000000+0.0163534250000000j,0.00529385930000000-0.00899492590000000j],
        [-0.0357672460000000-0.184694870000000j,-0.00486763040000000+0.389867630000000j,1.00000000000000-0.392576500000000j,-0.0209894750000000+0.162775500000000j,0.0545605310000000+0.0178600040000000j,0.00570462340000000-0.0158058180000000j],
        [-0.243650480000000-0.621005190000000j,0.171780550000000+1.00000000000000j,0.991371620000000-0.616985520000000j,0.0123093790000000+0.226197360000000j,0.0664346130000000+0.00893863510000000j,0.00291590790000000-0.0176460670000000j],
        [-0.361266600000000-0.584619380000000j,0.364736290000000+1.00000000000000j,0.819282070000000-0.742563710000000j,0.0782167860000000+0.328155280000000j,0.0947567500000000-0.00435023510000000j,-0.000398139520000000-0.0251048570000000j],
        [-0.506095560000000-0.565319400000000j,0.581098410000000+1.00000000000000j,0.632358220000000-0.818469020000000j,0.177358440000000+0.407341740000000j,0.111416410000000-0.0252122480000000j,-0.00563953940000000-0.0289303170000000j],
        [-0.701785890000000-0.552418700000000j,0.842562390000000+1.00000000000000j,0.447755700000000-0.851597350000000j,0.298880190000000+0.451833620000000j,0.112934270000000-0.0472554550000000j,-0.0108536200000000-0.0282952180000000j],
        [-0.802606160000000-0.434249130000000j,1.00000000000000+0.841805930000000j,0.260903480000000-0.805764970000000j,0.439667120000000+0.466941220000000j,0.105781510000000-0.0673875440000000j,-0.0153014270000000-0.0256898240000000j],
        [-0.774899780000000-0.263497680000000j,1.00000000000000+0.587998330000000j,0.100362140000000-0.687425630000000j,0.589755510000000+0.445830130000000j,0.0903214920000000-0.0817102010000000j,-0.0182146040000000-0.0213912100000000j],
        [-0.768282870000000-0.125762600000000j,1.00000000000000+0.383299290000000j,-0.0114228300000000-0.555822410000000j,0.724494460000000+0.378822060000000j,0.0641223900000000-0.0809546540000000j,-0.0171669580000000-0.0144569250000000j],
        [-0.774409180000000+0.000563058110000000j,1.00000000000000+0.205882830000000j,-0.0785679720000000-0.423277200000000j,0.831136390000000+0.274324010000000j,0.0341062230000000-0.0614183960000000j,-0.0115445500000000-0.00687205820000000j],
        [-0.503439550000000+0.0819072300000000j,0.656713640000000+0.0279209730000000j,-0.0818674370000000-0.228463520000000j,0.925161410000000+0.147637210000000j,0.0121731730000000-0.0337296900000000j,-0.00543664530000000-0.00214864640000000j],
        [0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,1.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j],
        [-0.0295233140000000+0.00822833750000000j,0.0453893670000000+0.0586790830000000j,0.968270640000000-0.152340890000000j,-0.00278606150000000+0.0868823650000000j,0.0275370760000000+0.00171158010000000j,0.000136964270000000-0.00676283290000000j],
        [-0.0510273530000000+0.0231425270000000j,0.0961163020000000+0.0910678300000000j,0.895451630000000-0.286869410000000j,0.0222754730000000+0.181796110000000j,0.0549238420000000-0.00506190790000000j,-0.00177144450000000-0.0131675080000000j],
        [-0.0630869460000000+0.0411348860000000j,0.143151090000000+0.0992894010000000j,0.789586280000000-0.393216900000000j,0.0773435300000000+0.275239910000000j,0.0786416410000000-0.0195719720000000j,-0.00539970320000000-0.0183797380000000j],
        [-0.0657304960000000+0.0585837290000000j,0.179369970000000+0.0880322790000000j,0.661138660000000-0.464267200000000j,0.161365880000000+0.357393440000000j,0.0956287530000000-0.0397663630000000j,-0.0101301810000000-0.0217480290000000j],
        [-0.0602454390000000+0.0723443680000000j,0.200105830000000+0.0636196670000000j,0.521802420000000-0.496585800000000j,0.270169090000000+0.419161320000000j,0.103716610000000-0.0625255790000000j,-0.0151431860000000-0.0228961080000000j],
        [-0.0488533840000000+0.0801103230000000j,0.203345960000000+0.0330325230000000j,0.383299980000000-0.490456660000000j,0.396864110000000+0.453112550000000j,0.101957660000000-0.0840291650000000j,-0.0195321420000000-0.0217763110000000j],
        [-0.0343121880000000+0.0806231170000000j,0.189608880000000+0.00299473560000000j,0.256284570000000-0.449564950000000j,0.532509870000000+0.454230760000000j,0.0908124030000000-0.100207780000000j,-0.0224289070000000-0.0186789150000000j],
        [-0.0195004330000000+0.0737282740000000j,0.161558150000000-0.0207940300000000j,0.149434920000000-0.380389760000000j,0.666959270000000+0.420415210000000j,0.0721790370000000-0.107231250000000j,-0.0231240130000000-0.0141974460000000j],
        [-0.00703321180000000+0.0602912810000000j,0.123427260000000-0.0342187920000000j,0.0688060810000000-0.291388710000000j,0.789801850000000+0.352698000000000j,0.0492645850000000-0.101981950000000j,-0.0211678530000000-0.00915463110000000j],
        [0.00105180420000000+0.0419994770000000j,0.0803372300000000-0.0350712570000000j,0.0174715190000000-0.192065020000000j,0.891314670000000+0.255169620000000j,0.0263113200000000-0.0824661610000000j,-0.0164412700000000-0.00449755910000000j],
        [0.00351101810000000+0.0210840090000000j,0.0375882730000000-0.0231276790000000j,-0.00453565940000000-0.0920089990000000j,0.963337680000000+0.134629480000000j,0.00820482180000000-0.0481229010000000j,-0.00918733340000000-0.00117354870000000j],
        [0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,1.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j],
        [-0.00556276980000000-0.00855059130000000j,-0.0221033580000000+0.0452872510000000j,0.970533440000000-0.0835773430000000j,0.0522782610000000+0.0723274970000000j,0.0114984810000000-0.0268239250000000j,-0.00756365520000000+0.00102726750000000j],
        [-0.0115658950000000-0.0148203250000000j,-0.0322036600000000+0.0834848500000000j,0.916114000000000-0.158960860000000j,0.122215820000000+0.141682100000000j,0.0182123940000000-0.0551297040000000j,-0.0145576260000000+0.00326902420000000j],
        [-0.0173357360000000-0.0186615970000000j,-0.0326537780000000+0.112601320000000j,0.840033540000000-0.221407350000000j,0.208217160000000+0.203168450000000j,0.0196335260000000-0.0826728920000000j,-0.0204280130000000+0.00647156450000000j],
        [-0.0222375990000000-0.0201549850000000j,-0.0261425640000000+0.131427550000000j,0.746654530000000-0.267157260000000j,0.307448200000000+0.252316220000000j,0.0158832340000000-0.107076060000000j,-0.0247161080000000+0.0102377470000000j],
        [-0.0257336180000000-0.0195793760000000j,-0.0154774700000000+0.139565030000000j,0.641116830000000-0.293653100000000j,0.415978860000000+0.285393560000000j,0.00774178230000000-0.126013050000000j,-0.0271005180000000+0.0140607030000000j],
        [-0.0274285070000000-0.0173689100000000j,-0.00337292890000000+0.137397890000000j,0.529002230000000-0.299676060000000j,0.529002230000000+0.299676060000000j,-0.00337292890000000-0.137397890000000j,-0.0274285070000000+0.0173689100000000j],
        [-0.0271005180000000-0.0140607030000000j,0.00774178230000000+0.126013050000000j,0.415978860000000-0.285393560000000j,0.641116830000000+0.293653100000000j,-0.0154774700000000-0.139565030000000j,-0.0257336180000000+0.0195793760000000j],
        [-0.0247161080000000-0.0102377470000000j,0.0158832340000000+0.107076060000000j,0.307448200000000-0.252316220000000j,0.746654530000000+0.267157260000000j,-0.0261425640000000-0.131427550000000j,-0.0222375990000000+0.0201549850000000j],
        [-0.0204280130000000-0.00647156450000000j,0.0196335260000000+0.0826728920000000j,0.208217160000000-0.203168450000000j,0.840033540000000+0.221407350000000j,-0.0326537780000000-0.112601320000000j,-0.0173357360000000+0.0186615970000000j],
        [-0.0145576260000000-0.00326902420000000j,0.0182123940000000+0.0551297040000000j,0.122215820000000-0.141682100000000j,0.916114000000000+0.158960860000000j,-0.0322036600000000-0.0834848500000000j,-0.0115658950000000+0.0148203250000000j],
        [-0.00756365520000000-0.00102726750000000j,0.0114984810000000+0.0268239250000000j,0.0522782610000000-0.0723274970000000j,0.970533440000000+0.0835773430000000j,-0.0221033580000000-0.0452872510000000j,-0.00556276980000000+0.00855059130000000j],
        [0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,1.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j],
        [-0.00918733340000000+0.00117354870000000j,0.00820482180000000+0.0481229010000000j,0.963337680000000-0.134629480000000j,-0.00453565940000000+0.0920089990000000j,0.0375882730000000+0.0231276790000000j,0.00351101810000000-0.0210840090000000j],
        [-0.0164412700000000+0.00449755910000000j,0.0263113200000000+0.0824661610000000j,0.891314670000000-0.255169620000000j,0.0174715190000000+0.192065020000000j,0.0803372300000000+0.0350712570000000j,0.00105180420000000-0.0419994770000000j],
        [-0.0211678530000000+0.00915463110000000j,0.0492645850000000+0.101981950000000j,0.789801850000000-0.352698000000000j,0.0688060810000000+0.291388710000000j,0.123427260000000+0.0342187920000000j,-0.00703321180000000-0.0602912810000000j],
        [-0.0231240130000000+0.0141974460000000j,0.0721790370000000+0.107231250000000j,0.666959270000000-0.420415210000000j,0.149434920000000+0.380389760000000j,0.161558150000000+0.0207940300000000j,-0.0195004330000000-0.0737282740000000j],
        [-0.0224289070000000+0.0186789150000000j,0.0908124030000000+0.100207780000000j,0.532509870000000-0.454230760000000j,0.256284570000000+0.449564950000000j,0.189608880000000-0.00299473560000000j,-0.0343121880000000-0.0806231170000000j],
        [-0.0195321420000000+0.0217763110000000j,0.101957660000000+0.0840291650000000j,0.396864110000000-0.453112550000000j,0.383299980000000+0.490456660000000j,0.203345960000000-0.0330325230000000j,-0.0488533840000000-0.0801103230000000j],
        [-0.0151431860000000+0.0228961080000000j,0.103716610000000+0.0625255790000000j,0.270169090000000-0.419161320000000j,0.521802420000000+0.496585800000000j,0.200105830000000-0.0636196670000000j,-0.0602454390000000-0.0723443680000000j],
        [-0.0101301810000000+0.0217480290000000j,0.0956287530000000+0.0397663630000000j,0.161365880000000-0.357393440000000j,0.661138660000000+0.464267200000000j,0.179369970000000-0.0880322790000000j,-0.0657304960000000-0.0585837290000000j],
        [-0.00539970320000000+0.0183797380000000j,0.0786416410000000+0.0195719720000000j,0.0773435300000000-0.275239910000000j,0.789586280000000+0.393216900000000j,0.143151090000000-0.0992894010000000j,-0.0630869460000000-0.0411348860000000j],
        [-0.00177144450000000+0.0131675080000000j,0.0549238420000000+0.00506190790000000j,0.0222754730000000-0.181796110000000j,0.895451630000000+0.286869410000000j,0.0961163020000000-0.0910678300000000j,-0.0510273530000000-0.0231425270000000j],
        [0.000136964270000000+0.00676283290000000j,0.0275370760000000-0.00171158010000000j,-0.00278606150000000-0.0868823650000000j,0.968270640000000+0.152340890000000j,0.0453893670000000-0.0586790830000000j,-0.0295233140000000-0.00822833750000000j],
        [0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,1.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j],
        [-0.00543664530000000+0.00214864640000000j,0.0121731730000000+0.0337296900000000j,0.925161410000000-0.147637210000000j,-0.0818674370000000+0.228463520000000j,0.656713640000000-0.0279209730000000j,-0.503439550000000-0.0819072300000000j],
        [-0.0115445500000000+0.00687205820000000j,0.0341062230000000+0.0614183960000000j,0.831136390000000-0.274324010000000j,-0.0785679720000000+0.423277200000000j,1.00000000000000-0.205882830000000j,-0.774409180000000-0.000563058110000000j],
        [-0.0171669580000000+0.0144569250000000j,0.0641223900000000+0.0809546540000000j,0.724494460000000-0.378822060000000j,-0.0114228300000000+0.555822410000000j,1.00000000000000-0.383299290000000j,-0.768282870000000+0.125762600000000j],
        [-0.0182146040000000+0.0213912100000000j,0.0903214920000000+0.0817102010000000j,0.589755510000000-0.445830130000000j,0.100362140000000+0.687425630000000j,1.00000000000000-0.587998330000000j,-0.774899780000000+0.263497680000000j],
        [-0.0153014270000000+0.0256898240000000j,0.105781510000000+0.0673875440000000j,0.439667120000000-0.466941220000000j,0.260903480000000+0.805764970000000j,1.00000000000000-0.841805930000000j,-0.802606160000000+0.434249130000000j],
        [-0.0108536200000000+0.0282952180000000j,0.112934270000000+0.0472554550000000j,0.298880190000000-0.451833620000000j,0.447755700000000+0.851597350000000j,0.842562390000000-1.00000000000000j,-0.701785890000000+0.552418700000000j],
        [-0.00563953940000000+0.0289303170000000j,0.111416410000000+0.0252122480000000j,0.177358440000000-0.407341740000000j,0.632358220000000+0.818469020000000j,0.581098410000000-1.00000000000000j,-0.506095560000000+0.565319400000000j],
        [-0.000398139520000000+0.0251048570000000j,0.0947567500000000+0.00435023510000000j,0.0782167860000000-0.328155280000000j,0.819282070000000+0.742563710000000j,0.364736290000000-1.00000000000000j,-0.361266600000000+0.584619380000000j],
        [0.00291590790000000+0.0176460670000000j,0.0664346130000000-0.00893863510000000j,0.0123093790000000-0.226197360000000j,0.991371620000000+0.616985520000000j,0.171780550000000-1.00000000000000j,-0.243650480000000+0.621005190000000j],
        [0.00570462340000000+0.0158058180000000j,0.0545605310000000-0.0178600040000000j,-0.0209894750000000-0.162775500000000j,1.00000000000000+0.392576500000000j,-0.00486763040000000-0.389867630000000j,-0.0357672460000000+0.184694870000000j],
        [0.00529385930000000+0.00899492590000000j,0.0297979330000000-0.0163534250000000j,-0.0269248330000000-0.0829619090000000j,1.00000000000000+0.190775510000000j,-0.00815400230000000-0.0406285960000000j,0.000248602360000000-0.0435534360000000j],
        [0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,1.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j,0.00000000000000+0.00000000000000j],
        [-0.00151871260000000+0.00184385340000000j,0.00936897050000000+0.0112669200000000j,0.758015330000000-0.146844990000000j,0.584238890000000+0.895782120000000j,-0.392651150000000-1.00000000000000j,0.0412097800000000+0.240737600000000j],
        [-0.00185801890000000+0.00344233770000000j,0.0173431030000000+0.0141124970000000j,0.530520360000000-0.215233520000000j,0.973532900000000+1.00000000000000j,-0.539754220000000-0.845409030000000j,0.0184387630000000+0.0484572210000000j],
        [-0.00129618360000000+0.00421464770000000j,0.0210620410000000+0.0111389720000000j,0.334890490000000-0.220365430000000j,1.00000000000000+0.687411110000000j,-0.166383410000000-0.173384140000000j,-0.189454580000000-0.302064240000000j],
        [-0.000352281210000000+0.00352889540000000j,0.0176702590000000+0.00522702820000000j,0.170290520000000-0.168751330000000j,0.999999990000000+0.426762800000000j,0.175071670000000+0.121615930000000j,-0.362672940000000-0.382311160000000j],
        [0.000187633220000000+0.00184485030000000j,0.00930407350000000+0.000809176510000000j,0.0566232880000000-0.0847366050000000j,1.00000000000000+0.205321280000000j,0.274224610000000+0.117975590000000j,-0.339745580000000-0.237908360000000j]
        ]

    def floor(self, data):
        if str(type(data)).find("complex") == -1:
            return np.floor(data)
        else:
            return complex(np.floor(data.real), np.floor(data.imag))

    # ori-name: channel_test2_tep
    # return None or [....]
    # kw["type"]
    #   1       format to eye diagram
    #   else    format to frequency response
    def channel_formater(self, xdata, **kw):
        ret_type = kw.get("type", 0)
        '''translate matlib channel_test2.m'''
        if (not xdata) or (xdata == []):
            return None

        ret = None

        try:
            fg_fftin = 0
            tring = 0
            fg_downst = 1
            P = 6
            fg_deinter = 0
            cp = 64
            NFFT = 1024
            fg_DEMAP = 0
            N = 1024
            ldpcsize = 1824
            if P == 6:
                ldpcsize = 2736
            JN = round(NFFT*912/1024*P/ldpcsize)
            datain = [0]*1024
            dvin = [0]*1024

            for i in xdata:
                xi = i>>16
                xi = (xi >= 0x8000)*(- 0x10000) + xi
                xq = i & 0xffff
                xq = (xq >= 0x8000) * (- 0x10000) + xq
                xq = xq/2.0
                datain.append(complex(xi ,xq))
                dvin.append(i&1)
            datain.append(0)
            dvin.append(0)

            tep = []
            tep_add = 0
            for i in dvin:
                tep.append(i-tep_add)
                tep_add = i
            tepp = [i for i in range(len(tep)) if tep[i] == 1]
            teppx = [i for i in range(len(tep)) if tep[i] == -1]
            if teppx[0] - tepp[0] != N:
                i = tepp[0]
                while(i <= teppx[0]):
                    dvin[i] = 0
                    i+=1
            if(len(dvin) - tepp[-1]) < N:
                i = tepp[-1]
                while(i < len(dvin)):
                    dvin[i] = 0
                    i+=1

            #FFT
            l_fft = N+cp
            fft_inj = datain
            dv_inj = dvin

            if len(dv_inj) < len(fft_inj):
                dv_inj.extend([0]*(len(fft_inj)-len(dv_inj)))
            else:
                fft_inj.extend([0]*(len(dv_inj)-len(fft_inj))) 
            fftout = []
            for i in fft_inj:
                fftout.append(i / (2.0**15)) #16.15
            dvfft=dv_inj
            P = 2**(P/2)
            tep=[i for i in range(len(dvfft)) if dvfft[i] != 0]
            fg_frame=[0]*len(dvfft)
            i = tep[0]
            while(i <= tep[-1]):
                fg_frame[i] = 1
                i+=1

            c = [0]*10
            c[0] = 1
            c[3] = 1
            reg = [0]*10
            reg[0] = 1
            index_pilot = range(14)
            index_pilot.extend(range(19,N-10+1,12))
            index_pilot.extend(range(N-15,N-1+1))
            start_data=14
            last_data=1008

            fg_pilot=[0]*len(fftout)
            fg_pilot_b=[0]*(len(fftout)+1)
            pilot=fg_pilot
            fftoutx=fftout
            i = 1
            ####
            for k in range(2,len(fftout)+1):
                if (dvfft[k-1-1]==0) & (dvfft[k-1]):
                    i = 1
                    reg = [0]*10
                    reg[0] = 1
                    kk = 0
                if dvfft[k-1] == 1:
                    temp_reg = 0
                    for x in range(len(reg)):
                        temp_reg += reg[x]*c[x]
                    reg = reg[1:]
                    reg.append(temp_reg & 1)
                    pilot[k-1] = 2*(reg[0]==1)-1
                    if kk == index_pilot[i-1]:
                        if fg_fftin==0:
                            fftoutx[k-1] = fftout[k-1]
                        else:
                            fftoutx[k-1] = fftout[k-1]/np.sign(pilot[k-1])
                        if fg_fftin == 1:
                            fftoutx[k-1] = fftoutx[k-1]/(1+1j)
                        fg_pilot[k-1] = 1
                        fg_pilot_b[kk+1-1] = 1
                        if N == 1024:
                            if (kk<(start_data -3)) | (kk > (last_data+3)):
                                fftoutx[k-1] = 0
                        else:
                            if (kk<(start_data -3)) | (kk > (last_data+3)):
                                fftoutx[k-1] = 0
                        i += 1
                    else:
                        fftoutx[k-1] = fftout[k-1]
                        fg_pilot[k-1] = 0
                    kk += 1
            ##end of pilot response
            ##load F_1024_comp
            start = start_data
            last = last_data + 3
            nseg = 41 * (N / 512)

            F = []
            for y in self.F:
                a = []
                for x in y:
                    x1 = self.floor(x * (2**14))/(2.0**14)
                    Fi = x1.imag
                    Fi = Fi*(abs(Fi)<1)+(1 - (2**-14))*np.sign(Fi)*(abs(Fi)>=1)
                    Fr = x1.real
                    Fr = Fr*(abs(Fr)<1)+(1 - (2**-14))*np.sign(Fr)*(abs(Fr)>=1)
                    a.append(complex(Fr, Fi))
                F.append(a)


            Hout = [1] * len(fftoutx)
            for kk in range(1, len(fftoutx)):
                if(dvfft[kk-1]==0)&(dvfft[kk]==1):
                    Y = fftoutx[kk:kk+N]
                    H = [0] * len(Y)
                    index_filter = 1
                    Q = 12*3
                    vec = [0] * 6
                    cnt1 = 0
                    cnt_buf = 0
                    buf = [0] * 6
                    for k in range(N+Q):
                        cnt1 = cnt1 + 1
                        if (k >=(start -3)):
                            if (k <=last):
                                if(fg_pilot_b[k] == 1):
                                    cnt_buf = cnt_buf + 1
                                    buf[cnt_buf - 1] = Y[k]
                            if k > 256:
                                if cnt1 ==12:
                                    vec = vec[1:]
                                    vec.append(buf[0])
                                    buf = buf[1:]
                                    buf.append(0)
                                    cnt_buf = cnt_buf - 1
                                    cnt1 = 0
                            elif cnt_buf > 0:
                                vec = vec[1:]
                                vec.append(buf[0])
                                buf = buf[1:]
                                buf.append(0)
                                cnt_buf = cnt_buf - 1
                                cnt1 = 0
                        if ((k) < start + Q ):
                            H[k] = Y[k]
                        else:
                            if (k-Q) > (last - 3):
                                H[k-Q] = Y[k-Q]
                            else:
                                stx1 = 29
                                if (index_filter > stx1):
                                    if (index_filter < 6+12*(nseg-2)):
                                        index_tep = ((index_filter-stx1-1)%12) + stx1 + 1
                                    else:
                                        index_tep = stx1+12+index_filter - (6 + 12 *(nseg -2)) + 1
                                else:
                                    index_tep = index_filter
                                if fg_pilot_b[k - Q] == 1:
                                    H[k - Q] = Y[k - Q]
                                else:
                                    H[k - Q] = 0
                                    for x in range(len(vec)):
                                        H[k - Q] += vec[x] * F[index_tep-1][x]
                                index_filter = index_filter + 1
                    for x in range(len(H)):
                        Hout[kk + x] = H[x]

            A_pilot = [1,2,4,8,16]
            for x in range(len(Hout)):
                Hout[x] = self.floor(Hout[x] * (2**11)) / (2.0**11)
            for x in range(len(fftoutx)):
                fftoutx[x] = self.floor(fftoutx[x] * (2**11)) / (2.0**11)
            B = A_pilot[int(math.log(P,2))]
            A = []
            YA = []
            for x in Hout:
                y = (x * x.conjugate()).real
                A.append(self.floor(y * (2**17))/(2.0 ** 17))
                YA.append(x.conjugate()*B)
            for x in range(len(YA)):
                YA[x] = YA[x]* fftoutx[x]
                YA[x] = self.floor(YA[x] * (2**13))/(2.0 ** 13)
                if A[x] == 0:
                    YA[x] = 0
                else:
                    YA[x] = (YA[x].real)/A[x]

            if ret_type == 0:
                ret = map(abs, Hout)
            elif ret_type == 1:
                ret = YA
            else:
                ret = map(abs, Hout)
        except Exception, e:
            # print("Exception", e)
            return None
        return ret

    def fft(self, dump_info):
        data = abs(np.fft.fft(dump_info))
        return map(lambda x:20 * math.log(x,10) + self.last_amp, data)

    # ==================================
    # Trigger Function
    # ==================================
    # return [] or None
    def trigger(self, dbgc_event, samples = None, formater = None):
        assert(isinstance(dbgc_event, C88xxDebugcoreEvent))
        tr_clock = dbgc_event._get_clock()
        tr_event = dbgc_event._get_event()
        tr_point = dbgc_event._get_point()
        tr_mode  = dbgc_event._get_mode()

        # e1 setting
        set_e1 = dbgc_event._is_e1_event()
        if set_e1:
            e1_change = dbgc_event._get_e1_change()
            e1_ori = self.agent.get_oam(0x7e, 0xe1)
            if type(e1_ori) != int:
                e1_ori = 0x1006
            self.agent.set_oam(0x7e, 0xe1, e1_change(e1_ori))

        # trigger
        rsp = self.agent.setup_dbgc(tr_clock, tr_event, tr_point, tr_mode)
        if not rsp:
            return None # timeout

        info = self.agent.dump_dbgc(samples or dbgc_event._get_max_size())

        # e1 recover
        if set_e1:
            self.agent.set_oam(0x7e, 0xe1, e1_ori)
        if not (info and formater):
            return info
        return formater(info)

    # return [] or None
    def trigger_func(self, func, points = None, pre_trigger = None):
        evnent_name, formater = self.formater[func]
        event = C88xxDebugcoreEvent()
        event.set_func(evnent_name, pre_trigger)
        return self.trigger(event, points, formater)

    def func_list(self):
        return [key for key in self.formater]

if __name__ == "__main__":
    from c88xx_analyzer_base import C88xxAgentBase as AgentFactory
    mmp_agent = AgentFactory.get_agent("mmp://eth0")

    analyzer = C88xxAnalyzer(mmp_agent)

    # func test
    for func in analyzer.func_list():
        print(func)
        dump_info = analyzer.trigger_func(func)
        if dump_info:
            print(len(dump_info))
        else:
            print("error")
