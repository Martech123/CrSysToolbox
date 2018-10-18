#!/usr/bin/env python

import os, sys
try:
    sys.path.insert(0, '../utils')
except:
    pass
import socket
import fw_cfg
import random

http_header_temp = '''HTTP/1.1 200 OK\r\n\
Content-Type: text/html\r\n\
Content-length: XXXXX\r\n\
Content-Encoding:     \r\n\
Cache-Control: private \r\n\
Set-Cookie: W=01:XX\r\n\
\r\n'''
#Set-Cookie: V=11111111111111111111111111111111\r\n\
def calc_md5(str):
    if sys.version_info[1] < 5:
        import md5
        m = md5.new(str)
        return m.digest()
    else:
        import hashlib
        m = hashlib.md5()
        m.update(str)
        return m.digest()

def arr2str(arr):
    str = ''
    for i in arr:
        str += chr(i)
    return str

IP  = (0x0004, 0x0004)
NM  = (0x0008, 0x0004)
GW  = (0x000c, 0x0004)

DC_IP   = (0x0704, 0x0004)
DC_NM   = (0x0708, 0x0004)
DC_GW   = (0x070c, 0x0004)

MAC     = (0x0010, 0x0006)
PWD     = (0x0020, 0x0016)

ROMR    = (0x0400, 0x0010)
FS  = (0x8000, 0x8000)

CNUID   = (0x0050, 0x0006)
class fw_gen:
    def __init__(self):
        self._path = None
        self.buf = []
        self.fw_no = 0
        self.cnuid_with_csum = []
        for i in range(0x20000):
            self.buf.append( 0xFF )

        for i in range(0x4):
            self.buf[i] = 0x0

        self.ori_head = ""
        self.ori_tail = ""

    def set_word(self, adr, dat):
        self.buf[adr + 0] = (dat & 0xFF000000) >> 24
        self.buf[adr + 1] = (dat & 0x00FF0000) >> 16
        self.buf[adr + 2] = (dat & 0x0000FF00) >> 8
        self.buf[adr + 3] = (dat & 0x000000FF) >> 0

    def set_short(self, adr, dat):
        self.buf[adr + 0] = (dat & 0xFF00) >> 8
        self.buf[adr + 1] = (dat & 0x00FF) >> 0

    def get_word(self, addr):
        word = 0
        for i in range(4):
            word = (word << 8) | self.buf[addr + i]
        return word & 0xFFFFFFFF

    def get_short(self, adr):
        return ((self.buf[adr + 0] << 8) | (self.buf[adr + 1])) & 0xFFFF
    def set_byte(self, adr, dat):
        self.buf[adr] = dat

    def get_byte(self, adr):
        return self.buf[adr]

    def set_str(self, adr, str):
        for i in range(len(str)):
            self.buf[adr + i] = ord(str[i])
    def get_str(self, adr, len):
        str = ''
        for i in range(len):
            str += chr(self.buf[adr + i])
        return str

    def _get_ip_addr(self, adr):
        return tuple(self.buf[adr:adr+4])

    def set_ip_addr(self, adr, ip):
        for i in range(4):
            self.buf[adr + i] = ip[i]

    def pprint(self):
        for i in range(0x10000):
            if((i & 0xF) == 0x0):
                print '\n%04X:' % i,
            print "%02X" % self.buf[i],
    def set_revision(self):
        rev = 0
        try:
            import time

            rev = int(time.strftime('%H%M'),16)
            self.set_short(0x16, rev)
            print 'REV=%04x' % rev
        except:
            print 'SVN err'
        return rev

    def set_ip(self, ip):
        self.set_str(IP[0], socket.inet_aton(ip))
        self.set_str(DC_IP[0], socket.inet_aton(ip))

    def get_clt_ip_default(self):
        return socket.inet_ntoa(self.get_str(DC_IP[0], DC_IP[1]))
    def set_netmask(self, nm):
        self.set_str(NM[0], socket.inet_aton(nm))
        self.set_str(DC_NM[0], socket.inet_aton(nm))

    def set_gateway(self, gw):
        self.set_str(GW[0], socket.inet_aton(gw))
        self.set_str(DC_GW[0], socket.inet_aton(gw))

    def get_ip(self):
        return socket.inet_ntoa(self.get_str(IP[0], IP[1]))

    def get_netmask(self):
        return socket.inet_ntoa(self.get_str(NM[0], NM[1]))

    def get_gateway(self):
        return socket.inet_ntoa(self.get_str(GW[0], GW[1]))

    def set_mac(self, mac):
        mstr = ''
        mint = int(mac, 16)
        for i in range(6):
            mstr = chr(mint & 0xFF) + mstr
            mint = mint >> 8
        self.set_str(MAC[0], mstr)

        self.set_str(0x780 + 0x10, mstr)


    def get_mac(self):
        mint = 0
        for i in range(6):
            mint = self.buf[MAC[0] + i] + (mint << 8)
        return '%012x' % mint
        # TODO: read from tfs

    def set_pwd(self, pwd):
        self.set_str(PWD[0], calc_md5(pwd + 'CredO2011~'))

    def set_web_pwd(self, pwd):
        self.set_str(0x780, calc_md5('admin' + pwd + '<'))

    def set_vlan_enable_default(self, enable):
        self.set_byte(0x804, (self.get_byte(0x804) & 0xFC) | (enable == True) | ((enable == True) << 1))

    def get_vlan_enable_default(self):
        return (self.get_byte(0x804) & 0x3) != 0

    def set_port_vlan_enable_default(self, enable):
        self.set_byte(0x804,  (self.get_byte(0x804) & 0xFB) | ((enable == True) << 2 ))

    def get_port_vlan_enable_default(self):
        return (self.get_byte(0x804) & (1 << 2)) != 0

    def set_vlan_id_default(self, vlan_id):
        self.set_short(0x809, vlan_id & 0xFFF)

    def get_vlan_id_default(self):
        return self.get_short(0x809)

    def set_port_vlan_id_default(self, port_vlan_ids):
        tfs_pos = 0
        for i in port_vlan_ids:
            self.set_short(0x810 + tfs_pos, i)
            tfs_pos += 2
            if(tfs_pos >= (2 * 4)) :
                break;

    def get_port_vlan_id_default(self):
        port_vlan_ids = tuple()
        for i in range(0, 8, 2):
            port_vlan_ids += (self.get_short(0x810 + i), )
        return port_vlan_ids
    def set_inet_allow(self, allow):
        self.set_byte(0x803, (allow == False) * 1)

    def get_inet_allow(self):
        return self.get_byte(0x803) == 0

    def set_vlan_default(self, vlan_tag_en, vlan_untag_en, vlan_id, port_vlan_en, igmp_en):
        #TODO: port vlanid argv
        self.set_byte(0x804,
            (vlan_tag_en == True) |
            ((vlan_untag_en == True) << 1) |
            ((port_vlan_en == True) << 2 ) |
            ((igmp_en == True) << 3 ) # 1:enable
        )
        self.set_byte(0x809, vlan_id & 0xFF)
        self.set_byte(0x80a, (vlan_id >> 8) & 0xF)

        self.set_short(0x810, 0x0123)
        self.set_short(0x812, 0x0124)
        self.set_short(0x814, 0x0125)
        self.set_short(0x816, 0x0126)
    def set_mac_limit_default(self, enable, limit_num):
        self.set_byte(0x818, (enable and 1 << 7 or 0) | (limit_num & 0x7F))

    def set_manage_vlan_id(self, manage_vlan_id):
        self.set_short(0x710, manage_vlan_id)

    def get_manage_vlan_id(self):
        return self.get_short(0x710)

    def set_prio_vlan_id(self, prio_vlan_ids):
        self.set_short(0x712, prio_vlan_ids[0])
        self.set_short(0x714, prio_vlan_ids[1])

    def get_prio_vlan_id(self):
        return (self.get_short(0x712), self.get_short(0x714))

    def set_prio_ip(self, prio_ips):
        self.set_ip_addr(0x71a, prio_ips[0])
        self.set_ip_addr(0x71e, prio_ips[1])

    def get_prio_ip(self):
        return (self._get_ip_addr(0x71a), self._get_ip_addr(0x71e))

    def set_prio_vlan_id(self, prio_vlan_id1, prio_vlan_id2):
        self.set_byte(0x712, (prio_vlan_id1 >> 8) & 0xFF)
        self.set_byte(0x713, (prio_vlan_id1) & 0xFF)
        self.set_byte(0x714, (prio_vlan_id2 >> 8) & 0xFF)
        self.set_byte(0x715, (prio_vlan_id2) & 0xFF)
    def set_prio_ip(self, prio_ip_1, prio_ip_2):
        for i in range(4):
            self.set_byte(0x71a + i, prio_ip_1[i])
            self.set_byte(0x71e + i, prio_ip_2[i])

    def get_qos_mode(self):
        return self.get_byte(0x729)

    def set_user_desc_default(self, desc):
        self.set_str(0x840, desc)
        for i in range(0x40 - len(desc)):
            self.set_byte(0x840 + len(desc) + i, 0x00)

    def get_user_desc_default(self):
        return self.get_str(0x840, 0x40)

    def set_speed_limit_default(self, uplimit, downlimit):
        self.set_byte(0x805, (uplimit >> 8) & 0xFF)
        self.set_byte(0x806, (uplimit & 0xFF))
        self.set_byte(0x807, (downlimit >> 8) & 0xFF)
        self.set_byte(0x808, (downlimit & 0xFF))

    def set_cir_default(self, upcir, downcir):
        self.set_byte(0x80c, (upcir >> 8) & 0xFF)
        self.set_byte(0x80d, (upcir & 0xFF))
        self.set_byte(0x80e, (downcir >> 8) & 0xFF)
        self.set_byte(0x80f, (downcir & 0xFF))


    def set_llid_binding_default(self, binding):
        self.set_byte(0x762, binding)


    def set_anti_noise_disable_default(self, mode):
        self.set_byte(0x763, 0xfe | (mode and 1));

    def set_mode_default(self, mode):
        self.set_byte(0x765, mode);

    def get_mode_default(self):
        return self.get_byte(0x765)

    def set_force_nic_mode_default(self, val):
        self.set_byte(0x766, (self.get_byte(0x766) & 0xfb) | (val and (1 << 2) ));

    def get_force_nic_mode_default(self):
        if (self.get_byte(0x766) & 4) != 0:
            return True
        else:
            return False

    def set_simple_isolate_default(self, val):
        self.set_byte(0x766, (self.get_byte(0x766) & 0xf7) | (val and (1 << 3) ));

    def set_get_dev_mac_default(self, val):
        self.set_byte(0x766, (self.get_byte(0x766) & 0xef) | (val and (1 << 4) ));

    def set_cnu_tx_power_auto_adj_default(self, val):
        self.set_byte(0x766, (self.get_byte(0x766) & 0xdf) | (val and (1 << 5) ));

    def set_clt_high_sensitivity_default(self, val):
        self.set_byte(0x766, (self.get_byte(0x766) & 0xbf) | (val and (1 << 6) ));

    def set_clt_tx_power_offset_default(self, val):
        self.set_byte(0x768, val);

    def set_clt_prio_buf_size(self, vlst = (0xff00, 0xcfc0, 0xbf00)):
        """ vlst order (OAM_DD, OAM_DE, OAM_DF) """
        for v in range(3):
            self.set_short(0x76d - v * 2, vlst[v])

    def set_clt_inverse_phy_clock_default(self, val):
        self.set_byte(0x774,  (self.get_byte(0x774) & 0xfe) | (val and (1) ));

    def set_cnu_loop_detect_en_default(self, val):
        self.set_byte(0x774,  (self.get_byte(0x774) & 0xfd) | (val and (2) ));
    def set_cnu_phy_cfg_en_default(self, val):
        self.set_byte(0x774,  (self.get_byte(0x774) & 0xf7) | (val and (8) ));

    def set_romr(self, romr):
        '''
        ROMR format:
            ((CMP0, REP0), (CMP1, REP1), ...)
        '''
        self.earse(0x400, 0x100)

        adr = 0x400
        for i in romr:
            self.set_word(adr + 0, 0x0001)
            self.set_word(adr + 4, i[0])
            self.set_word(adr + 8, i[1])
            adr += 0x10
    def attach_cnu_fw(self, path):
        self.earse(0x18000, 0x8000)
        f = open(path, 'rb')
        cnu_fw_data = f.read()
        self.set_str(0x18000, cnu_fw_data[0x20000:0x28000])
        f.close()

    def set_fs(self, path):
        self.earse(0x8000, 0xe000 - 0x380)
        f = open(path, 'rb')
        self.set_str(0x8000, f.read())
        f.close()

    def set_cfg(self, iscnu, bands_cfg = 'eoc'):
        cfg = fw_cfg.gen_cfg(iscnu, bands_cfg)
        # for firmware
        self.set_str(0x500, cfg[0])     # basic config for devie
        self.set_str(0x60, cfg[1])      # band reg list
        # for network management
        self.set_str(0x1e0, cfg[2])     # band range list
        self.set_str(0x1f4,cfg[3])      # Version info for Switch

    # TODO: get
    #   - default register info
    #   - default baseband info
    #   - default LO info
    #   - default soft mode id
    def get_cfg(self):
        pass

    def set_default_band(self, default_band):
        print "Default Band = %d" % default_band
        self.set_byte(0x764, default_band)

    def get_default_band(self):
        return self.get_byte(0x764)

    def set_fw(self, fw_path, fw_ext_path):
        self.earse(0x100, 0x20)

        f = open(fw_path, 'rb')
        fw = f.read()
        f.close()

        f = open(fw_ext_path, 'rb')
        fw_ext = f.read()
        f.close()

        self.set_str(0x1000, fw)
        self.set_word(0x100, len(fw))
        self.set_word(0x104, 0x0100a000)
        self.set_word(0x108, 0x1000)

        self.set_str(0x16000 - 0x380, fw_ext)
        self.set_word(0x110, len(fw_ext))
        self.set_word(0x114, 0x010044fc - 0x380)
        self.set_word(0x118, 0x16000 - 0x380)

    def set_csum(self):
        self.set_word(0, 0)
        csum = 0
        for i in range(0x10000 / 4):
            '''
            tmp = 0
            for j in range(4):
                tmp = (tmp << 8) | self.buf[(i << 2) | j]
            '''
            tmp = self.get_word(i << 2)
            csum += tmp
        csum = csum & 0xFFFFFFFF
        csum = (~csum + 1) & 0xFFFFFFFF
        self.set_word(0, csum)
        return csum

    def save_fw(self, path, iscnu, clone_head = True, clone_tail = True):
        f = open(path, 'wb')
        str = ''

        if clone_head:
            '''
            # clone head for customizing firmware
            with open(self._path, "rb") as old_file:
                old_fw = old_file.read()
                str += old_fw[:0x20000]
            '''
            str += self.ori_head
        elif(iscnu):
            # Gen Random Mac for cnu
            for i in range(2):
                str += arr2str(self.gen_cnuid('%012x' % int(random.random() * 0xFFFFFFFFFFFF))) #TODO
                str += chr(0xff) * (0x10000 - 8)
        else:
            # Gen blank TFS for clt
            str += chr(0xff) * (0x20000)

        if(iscnu):
            # current revision of clt
            for j in range(2):
                for i in self.buf[0:0x10000]:
                    str += chr(i)
        else:
            for j in range(4):
                for i in self.buf:
                    str += chr(i)
        str = str[0:0x90000]
        if clone_tail and self.ori_tail:
            str += self.ori_tail
        else:
            str += fw_cfg.support_hardware(iscnu)
        f.write(str)
        f.close()

    def load_fw(self, path):
        f = open(path, 'rb')
        fw = f.read()
        f.close()
        self._path = path

        iscnu = None

        if(len(fw) < 0x40000):
            return -1
        elif len(fw) < 0x50000:
            iscnu = True
        elif len(fw) > 0x90000:
            iscnu = False
        else:
            return -1

        self.iscnu = iscnu

        for i in range(0x20000):
            self.buf[i] = ord(fw[i + 0x20000]) & 0xFF

        # load cnu id whatever it is CLT or CNU.
        arr = []
        for i in range(6):
            arr += [ord(fw[i]) & 0xFF]
        self.set_cnuid(arr)

        if iscnu is False:
            # load factory info
            self.factory_info_str = fw[0x80120:0x80120 + 0xe0]
            self.tx_correction = self.factory_info_str[0xbd]
            self.rx_correction = self.factory_info_str[0xbe]

        self.ori_head = fw[:0x20000]
        if iscnu:
            self.ori_tail = fw[0x40000:]
        else: # clt
            self.ori_tail = fw[0x90000:]

        return 0
    def earse(self, adr, len):
        for i in range(len):
            self.buf[adr + i] = 0xFF

    def set_eoc_type(self, isclt):
        if isclt:
            self.buf[0x56] = 0xFF
        else:
            self.buf[0x56] = 1

    # ---------------------------------------------------------------------
    def set_speed_up_limit_default(self, uplimit):
        self.set_short(0x805, uplimit)

    def get_speed_up_limit_default(self):
        return self.get_short(0x805)

    def set_speed_down_limit_default(self, downlimit):
        self.set_short(0x807, downlimit)

    def get_speed_down_limit_default(self):
        return self.get_short(0x807)

    def get_llid_binding_default(self):
        return self.get_byte(0x762)

    def get_eoc_type(self):
        return self.buf[0x56] == 0xFF

    def gen_cnu_update_data(self):
        f = open('cnup.dat', 'w')
        for i in range(0x10000 / 2 / 64):
            allone = 1
            allzero = 1
            for j in range(64):
                if(self.buf[j + i * 64] != 0xFF):
                    allone = 0
                if(self.buf[j + i * 64] != 0xFF):
                    allzero = 0
            if allzero == 0:
                pass
            if allone == 0:
                f.write("%04x:" % (i * 64))
                for j in range(64):
                    f.write('%02x' % self.buf[j + i * 64] )
                f.write(':%04x\n' % 0xAA)

        f.close()

    def set_http_header_temp(self):
        self.set_str(0x200, http_header_temp)

    def set_cnuid(self, cnuid):
        arr = cnuid
        if(type(cnuid) == type('str')):
            cnuid = cnuid.replace(':', '')
            cnuid = cnuid.replace('-', '')
            arr = hex2arr(cnuid)
        self.cnuid = arr

    def get_cnuid(self):
        cint = 0
        for i in range(6):
            cint = self.buf[CNUID[0] + i] + (cint << 8)
        return '%012x' % cint

    def get_cnuid_str(self):
        s = str()
        for i in self.cnuid:
            s += '%02X' % i
        return s

    def check_cnuid(self, cnuid_hex):
        if(len(cnuid_hex) < 8):
            return false

        tmp = 0
        for i in range(8):
            tmp += cnuid_hex[i]
        if((tmp & 0xFF) != 0x00):
            return false

        if(cnuid_hex[6] != 0x87):
            return false

        return true

    def gen_cnuid(self, cnuid_str):
        arr = []
        csum = 0
        cint = int(cnuid_str, 16)
        for i in range(6):
            csum += (cint & 0xFF)
            arr = [(cint & 0xFF)] + arr
            cint = cint >> 8

        arr.append(0x87)
        csum += 0x87
        arr.append( ((~csum) + 1) & 0xFF)
        return arr

    def get_band_list_size(self):
        # XXX: detect from firmware, Now just on 5
        return 5

    # group the flat list to Matrix(n x size)
    @staticmethod
    def group_list(flat, size):
            return [flat[i:i+size] for i in range(0, len(flat), size)]

    class ErrorBandAna15Unsupported(Exception):
        pass

    class ErrorBandSize(Exception):
        pass

    def get_band_reg_list(self):
        '''
        return [(a08, a13, a15, of9), ...]
        '''
        address = 0x60      # This address can be found in self.set_cfg()
        end = [0x00, 0x00]  # config end with [chr(0), char(0)]
        reg_num = 3         # XXX, in current version A15 is not in firmware
        list_size = self.get_band_list_size()
        cfg_len = list_size * reg_num * 2  + len(end)

        # dump list from firmware
        reg_list = []
        for addr in range(address, address + cfg_len, 2):
            byte_h = self.get_byte(addr)
            byte_l = self.get_byte(addr + 1)
            if [byte_h, byte_l] == end:
                break

            reg_list.append((byte_h << 8) | byte_l)

        if len(reg_list) % reg_num != 0:
            print("Warning: error reg_list length")
            raise self.ErrorBandSize

        result = []
        reg_matrix = self.group_list(reg_list, reg_num) # format list
        for row in reg_matrix:
            '''
            the column mapping refer to
                - fw_cfg XXX_BANDS
                - fw_cfg gen_cfg
            '''
            a08 = row[0]
            a13 = row[1]
            a15 = row[2] & 0x00ff
            of9 = row[2] & 0xff00
            result.append((a08, a13, a15, of9))
            if a15 == 0x0000:
                raise self.ErrorBandAna15Unsupported

        return result

    def get_band_range_list(self):
        '''
        return [(FreqLow, FreqHigh), ...]
        '''
        # This address can be found in self.set_cfg()
        # address = base + tuner(2)
        address = 0x1e0 + 2
        num = 2             # low & high
        end = [0x00]
        list_size = self.get_band_list_size()
        cfg_len = list_size * num + len(end)

        # dump list from firmware
        freq_list = []
        for addr in range(address, address + cfg_len):
            freq = self.get_byte(addr)
            if [freq] == end:
                break
            freq_list.append(freq)

        if len(freq_list) % num != 0:
            print("Warning: error freq_list length")
            raise self.ErrorBandSize

        result = []
        freq_matrix = self.group_list(freq_list, num) # format list
        for row in freq_matrix:
            '''
            the column mapping refer to
                - fw_cfg XXX_BANDS
                - fw_cfg gen_cfg
            '''
            freq_low = row[0]
            freq_high = row[1]
            result.append((freq_low, freq_high))

        return result

    def _set_cnu_csum(self):
        '''
        gen check sum for clt's inner cnu
        refer to
        - self.attach_cnu_fw()
        - self.set_csum()
        NOTE:
            attach_cnu_fw only attach cnu_fw_data[0: 0x8000]
            cnu_fw_data[0x8000:] == 0xff
        '''
        cnu_start = 0x18000
        cnu_len = 0x8000
        self.set_word(cnu_start, 0)
        csum = 0
        for i in range(0x8000 / 4):
            csum += self.get_word(cnu_start + (i << 2))

        # append 0xff with other length
        for i in range((0x10000 - 0x8000) / 4):
            csum += 0xFFFFFFFF
        csum = csum & 0xFFFFFFFF
        csum = (~csum + 1) & 0xFFFFFFFF
        self.set_word(cnu_start, csum)
        return csum

    def set_band_reg(self, idx, a08, a13, a15, of9, isclt = True):
        max_size = self.get_band_list_size()
        if idx >= max_size:
            return None

        reg_num = 3
        of9a15 = (of9 & 0xff00) | (a15 & 0x00ff)
        reg_list = (a08, a13, of9a15)
        base_addr = 0x60 + idx * reg_num * 2
        addrs = [base_addr]
        if isclt: addrs.append(base_addr + 0x18000)

        for addr in addrs:
            for i, reg in enumerate(reg_list):
                self.set_short(addr + i * 2, reg)

        if isclt: self._set_cnu_csum()

        return True

    def set_band_range(self, idx, freq_low, freq_high, isclt = True):
        max_size = self.get_band_list_size()
        if idx >= max_size:
            return None
        num = 2
        freq_list = (freq_low & 0xff, freq_high & 0xff)
        base_addr = 0x1e0 + 2 + idx * num
        addrs = [base_addr]
        if isclt: addrs.append(base_addr + 0x18000)

        for addr in addrs:
            for i, freq in enumerate(freq_list):
                self.set_byte(addr + i, freq)

        if isclt: self._set_cnu_csum()

        return True

    def get_firmware_type(self):
        '''
        in general,
            len(clt) >= 0x8000;
            len(cnt) in [0x4000, 0x8000)
        '''
        return "cnu" if self.iscnu else "clt"
