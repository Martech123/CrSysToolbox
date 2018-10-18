#!/usr/bin/env python

import sys

eoc_cfg_str = '''
PLL = 0x29e3
TX_PWR = 0x1306
CNU_FEQOFF = 0x0001
CNU_NO = 0
GMAC = 1

NONE    = (0x00)
OAM    = (0x01)
ANA    = (0x02)
PP    = (0x03)
ANA_PLL    = (0x04)
DELAY    = (0x05)

TIME_STARTUP     = (0x00)
TIME_STABLE     = (0x10)


# OAM, id, adr, dat
# ANA, adr, dat
# PP, trx, rule, addr, offset, data*6, mask*6

CNU_CFG = (
    (ANA,            0x08,    PLL         ), # pll
    (ANA,            0x13,    0x5EE0         ), # dac_clk inv

    (ANA,            0x15,    0x0001         ), # comp cal

    (OAM,            0x7e,    0xF9, 0x1800    ), #  # theta
    (OAM,            0x7e,    0xE1, TX_PWR    ), # tx power
    (OAM,            0x7e,    0xF1, 0x0104    ), # gd step
    (OAM,            0x7e,    0xF2, 0x0000    ), # fg up thre
    (OAM,            0x7e,    0xF3, 0x0000    ), # reset clock phase
#    (OAM,            0x7e,    0xF8, CNU_FEQOFF), # frequency offect
    (OAM,            0x7e,    0xC4, 0x093B    ), # agc setting
    (OAM,            0x7e,    0xE9, 0x0040    ), # flow ctrl dis
    (OAM,            0x7e,    0xC6, 0xf3FC    ), # gpio
    (OAM,            0x7e,    0xEF, 0x0300    ), # pp en
    (OAM,            0x7e,    0xFA, 0x0060    ), # ?
    (OAM,            0x7e,    0xDC, 0x0000    ), # ?
#    (OAM,            0x7e,    0xC9, CNU_NO    ), # mac_address
    (OAM,            0x7e,    0xDA, 0x0001    ), # memory size
    (OAM,            0x7e,    0x77, 0x0001    ), # fix ldpc err

#                TRX    RULE    ADDR    OFFSET    DATA[]                    MASK[]                    CTR
    (PP | TIME_STABLE,    0x0,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # PP TX Data
    (PP | TIME_STABLE,    0x1,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # PP RX Data
)

CNU_CFG_SEC = (
    (ANA,            0x08,    PLL         ), # pll
    (ANA,            0x13,    0x5EE0         ), # dac_clk inv

    (ANA,            0x15,    0x0001         ), # comp cal

    (OAM,            0x7e,    0xF9, 0x1800    ), #  # theta
    (OAM,            0x7e,    0xE1, TX_PWR    ), # tx power
    (OAM,            0x7e,    0xF1, 0x0104    ), # gd step
    (OAM,            0x7e,    0xF2, 0x0000    ), # fg up thre
    (OAM,            0x7e,    0xF3, 0x0000    ), # reset clock phase
    (OAM,            0x7e,    0xC4, 0x093B    ), # agc setting
    (OAM,            0x7e,    0xE9, 0x0040    ), # flow ctrl dis
    (OAM,            0x7e,    0xC6, 0xf3FC    ), # gpio
    (OAM,            0x7e,    0xEF, 0x0300    ), # pp en
    (OAM,            0x7e,    0xFA, 0x0060    ), # ?
    (OAM,            0x7e,    0xDC, 0x0000    ), # ?
    (OAM,            0x7e,    0xDA, 0x0000    ), # memory size
    (OAM,            0x7e,    0x77, 0x0001    ), # fix ldpc err

#                TRX    RULE    ADDR    OFFSET    DATA[]                    MASK[]                    CTR
    (PP | TIME_STABLE,    0x0,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # PP TX Data
    (PP | TIME_STABLE,    0x1,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # PP RX Data
)

CLT_CFG = (
    (ANA,            0x15, 0x0001            ), # comp cal

    (ANA,            0x08, PLL            ), # pll
    (ANA,            0x13, 0x5E60            ), # dac_clk inv

    (OAM,            0x7e, 0xF9, 0x1800), # theta
    (OAM,            0x7e, 0xE1, TX_PWR), # tx power
    (OAM,            0x7e, 0xF1, 0x0100), # gd step
#    (OAM,            0x7e, 0xD5, 0x0000), # max cnu
#    (OAM,            0x7e, 0xc5, 0x0020), # max cnu
    (OAM,            0x7e, 0xD5, 0x0010), # max cnu
    (OAM,            0x7e, 0xE9, 0x0050), # flow ctrl dis
    (OAM,            0x7e, 0xED, 0x00E8), # discover
    (OAM,            0x7e, 0xE2, 0x0001), # agc setting
    (OAM,            0x7e, 0xC4, 0x093B), # agc setting
    (OAM,            0x7e, 0xE2, 0x0001), # agc setting
    (OAM,            0x7e, 0xC6, 0x23FE), # gpio
    (OAM,            0x7e, 0xEF, 0x0300), # pp en
    (OAM,            0x7e, 0xDD, 0xFFD0), # prio queue percent (default:6.25%)
    (OAM,            0x7e, 0xDE, 0xCFC0), # prio queue percent (default:6.25%)
    (OAM,            0x7e, 0xDF, 0xBF00), # prio queue percent (default:87.5%)

    (OAM,            0x7e, 0xFA, 0x0060), # ?
    (OAM,            0x7e, 0xF2, 0x0000), # fg up thre
#smic    (OAM,            0x7e, 0xDA, 0x0002), # memory size
    (OAM,            0x7e,    0x77, 0x0001    ), # fix ldpc err

#                TRX    RULE    ADDR    OFFSET    DATA[]                    MASK[]                    CTR
    (PP | TIME_STABLE,    0x0,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # pp rx data
    (PP | TIME_STABLE,    0x1,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # pp tx data
#    (PP | TIME_STABLE,    0x0,    0x0,    0x6,    0x08,    0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0x2),    # cpu rx data
#    (PP | TIME_STABLE,    0x0,    0x0,    0x7,    0x2E,    0x01, 0x02, 0x03, 0xa0, 0x00, 0x00,    0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF,    0x2),    # arp rx data
)

CLT_CFG_SEC = (
    (ANA,            0x15, 0x0001            ), # comp cal

    (ANA,            0x08, PLL            ), # pll
    (ANA,            0x13, 0x5E60            ), # dac_clk inv

    (OAM,            0x7e, 0xF9, 0x1800), # theta
    (OAM,            0x7e, 0xE1, TX_PWR), # tx power
    (OAM,            0x7e, 0xF1, 0x0100), # gd step
    (OAM,            0x7e, 0xD5, 0x00c0), # max cnu
    (OAM,            0x7e, 0xE9, 0x0050), # flow ctrl dis
    (OAM,            0x7e, 0xED, 0x00C0), # discover
    (OAM,            0x7e, 0xE2, 0x0001), # agc setting
    (OAM,            0x7e, 0xC4, 0x093B), # agc setting
    (OAM,            0x7e, 0xE2, 0x0001), # agc setting
    (OAM,            0x7e, 0xC6, 0x23FE), # gpio
    (OAM,            0x7e, 0xEF, 0x0300), # pp en
    (OAM,            0x7e, 0xDD, 0xFFF0), # prio queue percent (default:6.25%)
    (OAM,            0x7e, 0xDE, 0xEFE0), # prio queue percent (default:6.25%)
    (OAM,            0x7e, 0xDF, 0xDF00), # prio queue percent (default:87.5%)

    (OAM,            0x7e, 0xFA, 0x0060), # ?
    (OAM,            0x7e, 0xF2, 0x0000), # fg up thre
#smic    (OAM,            0x7e, 0xDA, 0x0002), # memory size
    (OAM,            0x7e,    0x77, 0x0001    ), # fix ldpc err

#                TRX    RULE    ADDR    OFFSET    DATA[]                    MASK[]                    CTR
    (PP | TIME_STABLE,    0x0,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # pp rx data
    (PP | TIME_STABLE,    0x1,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # pp tx data
#    (PP | TIME_STABLE,    0x0,    0x0,    0x6,    0x08,    0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0x2),    # cpu rx data
#    (PP | TIME_STABLE,    0x0,    0x0,    0x7,    0x2E,    0x01, 0x02, 0x03, 0xa0, 0x00, 0x00,    0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF,    0x2),    # arp rx data
)
CLT_CFG_O2O = (
    (ANA,            0x15, 0x0001            ), # comp cal

    (ANA,            0x08, PLL            ), # pll
    (ANA,            0x13, 0x5E60            ), # dac_clk inv

    (OAM,            0x7e, 0xF9, 0x1800), # theta
    (OAM,            0x7e, 0xE1, TX_PWR), # tx power
    (OAM,            0x7e, 0xF1, 0x0100), # gd step
    (OAM,            0x7e, 0xD5, 0x00c0), # max cnu
    (OAM,            0x7e, 0xE9, 0x0050), # flow ctrl dis
    (OAM,            0x7e, 0xED, 0x0000), # discover
    (OAM,            0x7e, 0xE2, 0x0001), # agc setting
    (OAM,            0x7e, 0xC4, 0x093B), # agc setting
    (OAM,            0x7e, 0xE2, 0x0001), # agc setting
    (OAM,            0x7e, 0xC6, 0x23FE), # gpio
    (OAM,            0x7e, 0xEF, 0x0300), # pp en
    (OAM,            0x7e, 0xDD, 0xFFF0), # prio queue percent (default:6.25%)
    (OAM,            0x7e, 0xDE, 0xEFE0), # prio queue percent (default:6.25%)
    (OAM,            0x7e, 0xDF, 0xDF00), # prio queue percent (default:87.5%)

    (OAM,            0x7e, 0xFA, 0x0060), # ?
    (OAM,            0x7e, 0xF2, 0x0000), # fg up thre
    (OAM,            0x7e, 0x77, 0x0001), # fix ldpc err

#                TRX    RULE    ADDR    OFFSET    DATA[]                    MASK[]                    CTR
    (PP | TIME_STABLE,    0x0,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # pp rx data
    (PP | TIME_STABLE,    0x1,    0x0,    0x0,    0x08,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,    0x2),    # pp tx data
#    (PP | TIME_STABLE,    0x0,    0x0,    0x6,    0x08,    0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF,    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,    0x2),    # cpu rx data
#    (PP | TIME_STABLE,    0x0,    0x0,    0x7,    0x2E,    0x01, 0x02, 0x03, 0xa0, 0x00, 0x00,    0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF,    0x2),    # arp rx data
)


EOC_BANDS = (
#    ANA-08   ANA-13  OAM-F9
# Mainland ~
    (0x29E3, 0x5e60, 0x1601, "[11MHz~66.4MHz]",11,66), # FULL 11~66.4
    (0x296B, 0x5f60, 0x2601, "[42MHz~63MHz]",42,63), # HIGH 42~63
    (0x29c3, 0x5e60, 0x2401, "[33mhz~87mhz]",33,87),
    (0xa96B, 0x5f60, 0x1A01, "[34MHz~63MHz]",34,63), # HIGH(2) 34~63
    (0x2a33, 0x5ee0, 0x2201, "[36Mhz~100Mhz]",36,100), #
)
#    (0x2943, 0x5f60, 0x1800, "[25Mhz~35Mhz]"), # 25~35  ana15 = 0003
#    (0x294B, 0x5e60, 0x2200, "[24Mhz~64Mhz]"), # 24~64
#    (0x2993, 0x5f60, 0x0c00, "[6.24MHz~30MHz]"), # LOW 6.24~30

EOC_HIGHBAND=(
    EOC_BANDS[0],
    (0xa96B, 0x5e60, 0x2000, "[34MHz~90MHz]"), # HIGH(2) 34~90
    (0x296B, 0x5f60, 0x2600, "[45MHz~65MHz]"), # HIGH 45~65
    (0xa96B, 0x5f60, 0x1A00, "[34MHz~63MHz]"), # HIGH(2) 34~63
    (0x294B, 0x5e60, 0x2200, "[24Mhz~64Mhz]"), # 24~64
)

ONLAN_BANDS = (
    EOC_BANDS[0],
    (0x29c3, 0x5e60, 0x2400, "[33mhz~87mhz]"),
    (0x29a3, 0x5f60, 0x2800, "[50MHz~75MHz]"), # LOW 50~75
    (0xa96B, 0x5f60, 0x1A00, "[34MHz~63MHz]"),
    EOC_BANDS[1],
)

    #(0x2a33, 0x5ee0, 0x1200, "[5MHz~68MHz]"),
    #(0x2943, 0x5f60, 0x1800, "[25Mhz~35Mhz]"), # 25~35  ana15 = 0003
    #(0x29a3, 0x5e60, 0x2400, "[30MHz~80MHz]"), # HIGH 30~80MHz
    #(0x29f3, 0x5f60, 0x2400, "[50MHz~80MHz]"), # HIGH(2) 50~80MHz
    #(0x29e3, 0x5e60, 0x1e00, "[25MHz~80MHz]"), # HIGH 25~80MHz

RF_BANDS = (
     (0x2a13, 0x5f60, 0x2203, "[57MHz~72MHz]",57,72), # HIGH (also for RF 20MHz width)
     (0x29a3, 0x5f60, 0x2203, "[53MHz~65MHz]",53,65), # HIGH (also for RF 20MHz width)
     EOC_BANDS[3],
     EOC_BANDS[2],
     (0x2a2b, 0x5e60, 0x2001, "[32Mhz~94Mhz]",32,94), # 4~68
    #(0x0000, 0x0000, 0x0000, "NULL")
)
#    (0x2a03, 0x5e60, 0x2200, "[33mhz~93mhz]"),

SEC_BANDS = (
    EOC_BANDS[0],
    EOC_BANDS[1],
    (0x297B, 0x5fe0, 0x1600, "[5MHz~10MHz]"), # 5~10
    EOC_BANDS[3],
    (0x2943, 0x5fe0, 0x1000, "[5MHz~15MHz]"), # 5~15
)

LIANGYOU_BANDS = (
    (0x29E3, 0x5e60, 0x1600, "[11MHz~66.4MHz]"), # FULL 11~66.4
    (0x296B, 0x5f60, 0x2600, "[42MHz~63MHz]"), # HIGH 42~63
    (0x294B, 0x5f60, 0x2a00, "[45MHz~65MHz]"), # HIGH 45~65
    (0xa96B, 0x5f60, 0x1A00, "[34MHz~63MHz]"), # HIGH(2) 34~63
    (0x294B, 0x5e60, 0x2200, "[24Mhz~64Mhz]"), # 24~64
)

GX_BANDS = (
#    ANA-08   ANA-13  OAM-F9 | ANA-15
# Mainland ~
    EOC_BANDS[0],
    EOC_BANDS[1],
    (0x2a43, 0x5ee0, 0x1200, "[4MHz~68MHz]"), # 4~65
    EOC_BANDS[3],
    (0x29c3, 0x5e60, 0x2400, "[33MHz~87MHz]"),
)

    #(0x2a43, 0x5ee0, 0x1200, "[4Mhz~68Mhz]"), # 4~68

JT_BANDS = (
#    ANA-08   ANA-13  OAM-F9
# Mainland ~
    SEC_BANDS[4],
)

#    ANA-08   ANA-13  OAM-F9 | ANA-15
bands = {
    'eoc': EOC_BANDS,
    'one2one': EOC_BANDS,
    'onlan': ONLAN_BANDS,
    'rf': RF_BANDS,
    'eoc_rf': RF_BANDS,
    'sec': SEC_BANDS,
    'gxtech': GX_BANDS,
    'noiset': EOC_BANDS,
    'highband':EOC_HIGHBAND,
    'liangyou':LIANGYOU_BANDS,
    'dm': EOC_BANDS,
    'jt': JT_BANDS,
}
'''

MASK    = (0x0F)
END    = (0x00)
OAM    = (0x01)
ANA    = (0x02)
PP    = (0x03)
ANA_PLL    = (0x04)
DELAY    = (0x05)
MDIO    = (0x06)
TUNER = -637

def cfg2data(cfg):
    li = []
    for i in cfg:
        if (i[0] & MASK) == ANA:
            li += [i[0], i[1], i[2] >> 8, i[2] & 0xFF]
        elif (i[0] & MASK) == OAM:
            li += [i[0], i[1], i[2], i[3] >> 8, i[3] & 0xFF]
        elif (i[0] & MASK) == MDIO:
            # NOTE: 0x10 == TIMESTABLE
            li += [i[0] | 0x10, i[1], i[2], i[3] >> 8, i[3] & 0xFF]
        else:
            for j in i:
                li += [j]

    li += [END]

    return li

def cfg2band(cfg):
    li = []
    for i in cfg:
        for j in i[:3]:
            li += [j >> 8, j & 0xFF]
    li += [0x00, 0x00]
    return li

def gen_cfg(iscnu, bands_cfg = 'eoc'):
    ''' return cfg string data start from 0x500 '''
    buf = []
    soft_modeid = '000000000000'
    for i in range(0x200):
        buf.append(0xFF)

    exec(eoc_cfg_str)
    branch_set = bands_cfg
    bands_cfg = cfg2band(bands[bands_cfg])
    bands_list = []
    for i in bands[branch_set]:
        bands_list.extend(i[4:6])

    if iscnu:
        print "Load CNU Cfg"
        if branch_set == "sec":
            eoc_cfg = cfg2data(CNU_CFG_SEC)
        else:
            eoc_cfg = cfg2data(CNU_CFG)
        #soft_modeid = '1001FFFF0082'


    else:
        print "Load CLT Cfg"
        eoc_cfg = cfg2data(CLT_CFG)
        if branch_set == "sec":
            eoc_cfg = cfg2data(CLT_CFG_SEC)
        elif branch_set == "one2one":
            eoc_cfg = cfg2data(CLT_CFG_O2O)
        else:
            eoc_cfg = cfg2data(CLT_CFG)
        #soft_modeid = '2001FFFF0082'
    p = 0
    for i in range(len(eoc_cfg)):
        buf[p] = eoc_cfg[i]
        p += 1

    string = ''
    print "CFG LEN = 0x%X" % len(buf)
    for i in range(len(buf)):
        string += chr(buf[i])

    bands_str = ''
    for i in range(len(bands_cfg)):
        bands_str += chr(bands_cfg[i])
    bands_liststr = ''
    bands_liststr += chr((TUNER >> 8) &0xff)+chr(TUNER & 0xff)
    for i in bands_list:
        bands_liststr += chr(i)
    bands_liststr += chr(0)
    return (string, bands_str,bands_liststr,soft_modeid)

def support_hardware(iscnu):
    support_hardware_list=[]
    if iscnu:
        support_hardware_list=['CNU4009021B04001'
                               '0000000000000000']
    else:
        support_hardware_list=['CLT0208011A04001',
                           '0000000000000000']
    return ';'.join(support_hardware_list)



if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "fw_cfg.py input_file output_file"
        sys.exit(1)

    f = open("eoc.cfg", 'r')
    cfg = f.read()
    f.close()
    exec(cfg)

    def cfg2bin(cfg):
        li = []
        for i in cfg:
            if (i[0] & MASK) == ANA:
                li += [i[0], i[1], i[2] >> 8, i[2] & 0xFF]
            elif (i[0] & MASK) == OAM:
                li += [i[0], i[1], i[2], i[3] >> 8, i[3] & 0xFF]
            else:
                for j in i:
                    li += [j]

        li += [END]

        bin = ''
        for i in li:
            bin += '%c' % i
        return bin

    #print CLT_CFG
    #print CNU_CFG

    f = open("clt.cfg.bin", 'wb')
    f.write(cfg2bin(CLT_CFG))
    f.close()

    f = open("cnu.cfg.bin", 'wb')
    f.write(cfg2bin(CNU_CFG))
    f.close()
# vim: filetype=python:expandtab:shiftwidth=4:tabstop=4:softtabstop=4:textwidth=80
