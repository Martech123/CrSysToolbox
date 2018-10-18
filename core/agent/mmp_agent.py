import os
import time
import random
import socket
import struct
import netifaces
from c88xx_agent_base import C88xxAgentBase

import platform
current_os = platform.system()

def mac2arr(mac):
    if not mac:
        return None
    if ":" not in mac:
        if len(mac) != 12: return None
        mac_list = [mac[i: i + 2] for i in range(0, 12, 2)]
    else:
        mac_list = mac.split(":")

    if len(mac_list) != 6:
        return None
    return map(lambda x:int(x, 16), mac_list)

def str2arr(s):
    return [ord(c) for c in s]

def arr2str(arr):
    s = str()
    for i in arr:
        s += chr(i)
    return s

def bytes2int(bs):
    return int(''.join(map(lambda x: "%02x" % x, bs)), 16)

if current_os == "Linux":
    import fcntl
    class NetRawLinux(object):
        def open(self, dev, proto):
            self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, proto)
            self.sock.bind((dev, proto))
            info = fcntl.ioctl(self.sock.fileno(), 0x8927,  struct.pack('256s', dev[:15]))
            self.src_mac = [ord(char) for char in info[18:24]]

        def close(self):
            self.sock.close()

        # sbuf = str()
        def send(self, sdata):
            self.sock.send(sdata)

        def recv(self, nbytes, timeout):
            self.sock.settimeout(timeout)
            rdata = []
            try:
                rdata = self.sock.recv(nbytes)
            except socket.timeout:
                print("timeout")

            return rdata

        def get_hw_addr(self):
            return self.src_mac

        @staticmethod
        def list_resource():
            ifs = netifaces.interfaces()
            return dict(zip(ifs, ifs))

    NetRaw = NetRawLinux
elif current_os == "Windows":
    import fnmatch

    import ctypes
    from ctypes import POINTER, pointer

    '''
    for Windows

    Install
    =======
    ```
    pip install winpcapy
    ```

    Homepage
    ========
    https://github.com/orweis/winpcapy

    Note
    ====
    override WinPcap with winpcap_types
    reference: [winpcap c api](https://www.winpcap.org/docs/docs_412/html/main.html)
    '''
    import winpcapy
    from winpcapy import WinPcap
    from winpcapy import WinPcapDevices
    import winpcapy.winpcapy_types as wtypes

    class WinPcapOnce(WinPcap):
        def recv(self):
            pkthdr = wtypes.pcap_pkthdr()
            head = pointer(pkthdr)
            data = ctypes.create_string_buffer(2048)
            data = ctypes.cast(data, POINTER(ctypes.c_ubyte))
            wtypes.pcap_next_ex(self._handle, head, data)
            return ctypes.string_at(data, head.contents.len)
        def register_handle(self):
            assert self._handle is None
            self._handle = wtypes.pcap_open_live(
                                self._name, self._snap_length,
                                self._promiscuous, self._timeout,
                                self._err_buffer)

        def unregister_handle(self):
            if self._handle is not None:
                wtypes.pcap_close(self._handle)
            self._handle = None

    class NetRawWindows(object):
        class ErrorDevice(Exception):
            pass

        def _cmmp_check(self, rdata):
            if len(rdata) < 0:
                return False
            if rdata[12:14] != self._proto:
                return False
            if ord(rdata[0x10]) & 0x01 != 1:
                return False
            return True

        def open(self, dev, proto):
            self._dev = self.get_info_by_name(dev)[0]
            if not self._dev:
                raise self.ErrorDevice
            self._proto = chr(0xff & (proto >> 8)) + chr(0xff & proto)
            info = netifaces.ifaddresses(dev)[netifaces.AF_LINK][0]
            self._src_mac = mac2arr(str(info["addr"]))

            self._wincap = WinPcapOnce(self._dev, timeout = 1)
            self._wincap.register_handle()

        def close(self):
            self._wincap.unregister_handle()

        def send(self, sdata):
            self._wincap.send(sdata)

        def recv(self, nbytes, timeout):
            rdata = None
            capture = self._wincap
            start = time.time()
            now = start
            while now - start < timeout:
                rdata = capture.recv()
                # TODO filter with protocol
                if self._cmmp_check(rdata):
                    break
                now = time.time()
            else:
                print("timeout")
                rdata = ""
            return rdata

        def get_hw_addr(self):
            return self._src_mac

        @staticmethod
        def get_info_by_name(if_name):
            if_name = "*%s*" % (if_name)
            for name, desc in WinPcapDevices.list_devices().items():
                if fnmatch.fnmatch(name, if_name):
                    return name, desc
            return None, None

        @classmethod
        def list_resource(cls):
            res = {}
            ifs = netifaces.interfaces()
            for name in ifs:
                desc = cls.get_info_by_name(name)[1]
                if desc: res[name] = desc
            return res

    NetRaw = NetRawWindows
else:
    print("UNKNOW OS: %s" % current_os)
    raise NotImplementedError

@C88xxAgentBase.register("mmp")
class MMPAgent(C88xxAgentBase):
    mmp_cmd = {"get_oam":0x00a0,
               "set_oam":0x00a2,
               "get_ana":0x00a4,
               "set_ana":0x00a6,
               "get_debug_core":0x00b8,
               "set_debug_core":0x00ba,
               }

    @staticmethod
    def str2arr(s):
        return str2arr(s)

    @staticmethod
    def arr2str(arr):
        return arr2str(arr)

    @staticmethod
    def bytes2int(bs):
        return bytes2int(bs)

    @staticmethod
    def mac2arr(mac):
        return mac2arr(mac)

    def __init__(self):
        self.src_mac = []
        self.dst_mac = [0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff]
        self.vlan_extend = [0x81, 0x00]
        self.vlan_vid = [0x00, 0x00]
        self.package_ret = [0x88, 0xcc, 0xc0, 0xff]
        self.oui = [0x11, 0x22, 0x33]
        self.seq = 0
        self.proto = [0x80, 0x07]
        self.version = [0x20]
        self.func_dic = {"vlan":False, "reflet":False}

        # os detection
        self.net = NetRaw()
        self.timeout = 1 # sec
        self.retry = 3

    def _agent_send(self, info):
        return self.net.send(info)

    def _agent_recv(self):
        return self.net.recv(1000, self.timeout)

    # return xtag
    def _gen_seq(self):
        self.seq = random.randint(0, 0xffff)

    def _seq_check(self, buf):
        h = (self.seq >> 8) & 0xff
        l = self.seq & 0xff
        return h == buf[17] and l == buf[18]

    def _mmptype_check(self, buf, mmptype):
        return buf[16] == (mmptype & 0xff) + 1

    """
    @return success: respond
            fail:    None
    """
    def mmp_send(self, mmptype, buf, dst):
        mmptype = self.mmp_cmd[mmptype]

        # set sending buffer sequence number
        self._gen_seq()

        # combine buf
        sdata = []
        sdata.extend(dst or self.dst_mac)
        sdata.extend(self.src_mac)
        if self.func_dic["vlan"]:
            sdata.extend(self.vlan_extend)
            sdata.extend(self.vlan_vid)
        if self.func_dic["reflet"]:
            sdata.extend(self.package_ret)
        sdata.extend(self.proto)
        sdata.extend(self.version)
        sdata.extend([(mmptype & 0xff00) >>8, mmptype & 0xff])
        sdata.extend([0xff & (self.seq >> 8), 0xff & self.seq])
        sdata.extend(self.oui)
        sdata.extend(buf)
        if len(sdata) < 64:
            sdata.extend([0x00 for i in range(60)])

        # send
        self._agent_send(self.arr2str(sdata))

        retry = self.retry
        while (retry >= 0):
            retry -= 1
            # recv
            rdata = self._agent_recv()
            if (not rdata) or len(rdata) == 0: break # timeout
            # parse
            respond = self.str2arr(rdata)

            # respond check
            if not self._mmptype_check(respond, mmptype): continue
            if not self._seq_check(respond): continue
            # success
            return respond[22:len(rdata)]
        return None

    # ======================================================
    # implement interface
    # ======================================================
    def open(self, uri):
        # URI: mmp://eth?/mac_addr
        info = uri.partition("://")[-1].split("/")
        if not (info and info[0]):
            raise self.AgentOpenException
        mac = None
        if len(info) >= 2:
            mac = info[1]
        dev = info[0]

        proto = (self.bytes2int(self.proto))
        self.net.open(dev, proto)
        self.src_mac = self.net.get_hw_addr()
        dst_mac = self.mac2arr(mac)
        if not dst_mac: print("error dst mac input, using default dst mac")
        self.dst_mac = dst_mac or self.dst_mac

    def close(self):
        self.net.close()

    def get_oam(self, inst, reg, dst = None):
        buf = [inst & 0xff, reg & 0xff]
        ret = self.mmp_send("get_oam", buf, dst)
        if ret and ret[0] == 0:
            return (ret[1] << 8) + ret[2]
        else:
            return None;

    def set_oam(self, inst, reg, value, dst = None):
        buf = [inst & 0xff, reg & 0xff, (value >> 8) &0xff, value & 0xff]
        return self.mmp_send("set_oam", buf, dst)

    def get_ana(self, reg, dst = None):
        buf = [reg & 0xff]
        ret = self.mmp_send("get_ana", buf, dst)
        if ret and ret[0] == 0:
            return (ret[1] << 8) + ret[2]
        else:
            return None;

    def set_ana(self, reg, value, dst = None):
        buf = [reg & 0xff, (value >> 8) &0xff, value & 0xff]
        return self.mmp_send("set_ana", buf, dst)

    def __tuner_cfg(self, rw, addr, data = 0):
        reg = (addr & 0xff) << 8 | data & 0xff
        if rw == "read":
            o74_req = 0xf001
            o74_res = 0xf101
        else:
            o74_req = 0xf000
            o74_res = 0xf100

        if not self.set_oam(0x7e, 0x75, reg):
            print("tuner: error in set 0x75")
            return None
        if not self.set_oam(0x7e, 0x74, o74_req):
            print("tuner: error in set 0x74")
            return None

        max_retry = 10
        while max_retry >= 0:
            max_retry -= 1
            if self.get_oam(0x7e, 0x74) == o74_res: break
            time.sleep(0.2)
        else:
            print("tuner: error in get 0x74")
            return None

        return self.get_oam(0x7e, 0x75)

    def get_tuner(self, reg):
        return self.__tuner_cfg("read", reg)

    def set_tuner(self, reg, data):
        return self.__tuner_cfg("write", reg, data)

    def setup_dbgc(self, cs, tr_event, tp, tr_mode, dst = None):
        buf = []
        for i in (cs, tr_event, tp, tr_mode):
            buf.extend([(i >> 24) & 0xff, (i >> 16) & 0xff, (i >> 8) & 0xff, i & 0xff])
        res = self.mmp_send("set_debug_core", buf, dst)
        if (not res) or res[0] != 0:
            return None
        return res

    def dump_dbgc(self, samples = 2048, dst = None):
        # XXX??? add some value for progress bar
        # wait for debuf core ready
        wait_times = 3
        while (wait_times >= 0):
            data = self.mmp_send("get_debug_core", [1], dst)
            if not data:
                return None # timeout

            if data[0] != 4:
                break       # ready

            # not ready
            wait_times -= 1
            time.sleep(0.5)

        times = (samples + 127) / 128 # sample times
        dump_info = []
        for i in range(times):
            res = self.mmp_send("get_debug_core", [i], dst)
            if not res:
                dump_info = [] # timeout
                break
            if len(res) == 513:
                for x in range(1, 513, 4):
                    bs = res[x:x+4]
                    dump_info.append(self.bytes2int(bs))

        self.mmp_send("get_debug_core", [0xff], dst)
        return dump_info

    def list_resource(self):
        return self.net.list_resource()

    # ======================================================
    # something extra
    # ======================================================
    def set_vid(self, on, vid = 0):
        if on:
            self.vid = [(vid & 0xf000) >> 8, vid & 0xff]
        self.func_dic["vlan"] = on

    def set_reflet(self, on):
        self.func_dic["reflet"] = on

if __name__ == "__main__":
    c88xx = MMPAgent()
    device_list = c88xx.list_resource()
    print(device_list)


    if current_os == "Windows":
        device_name = device_list.keys()[2]
        c88xx.open("mmp://%s" % device_name)
    elif current_os == "Linux":
        c88xx.open("mmp://eth0")

    # oam test
    llid = 0x7e
    reg = 0xce
    val = 0x0001
    print "set oam"
    assert c88xx.set_oam(llid, reg, val) is not None
    print "get oam"
    print(c88xx.get_oam(llid, reg))

    # debug core test
    print "deubg core dump"
    set_list = [16, 268435457, 268443647, 1073741824] # copy from uav-link
    assert c88xx.setup_dbgc(*set_list) is not None
    print(c88xx.dump_dbgc())
