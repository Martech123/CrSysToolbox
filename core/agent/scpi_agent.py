import os
import time
import socket
import re
from c88xx_agent_base import C88xxAgentBase

import platform
current_os = platform.system()

if current_os == "Linux":
    import fcntl
    class NetUDPLinux(object):
        def open(self, uri):
            trsp = re.findall(r'(scpi):\/\/(\d+\.\d+\.\d+\.\d+):(\d+)', uri)
            if not trsp:
                raise Exception("Wrong or unsupport uri.")
            self.trsp_type = trsp[0][0]
            self.trsp = (trsp[0][1], int(trsp[0][2]))

            if self.trsp_type == 'scpi':
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                raise Exception("Unknown uri!")


        def close(self):
            self.sock.close()

        def send(self, sdata):
            self.sock.sendto(sdata, self.trsp)

        def recv(self, nbytes, timeout):
            self.sock.settimeout(timeout)
            rdata = []
            try:
                rdata = self.sock.recvfrom(nbytes)
            except socket.timeout:
                print("timeout")

            return rdata

        @staticmethod
        def list_resource():
            src = ["127.0.0.1:5024"]
            return dict(zip(src, src))

    NetUdp = NetUDPLinux
else:
    print("UNKNOW OS: %s" % current_os)
    raise NotImplementedError

@C88xxAgentBase.register("scpi")
class SCPIAgent(C88xxAgentBase):
    def __init__(self):
        self.net = NetUdp()
        self.timeout = 1 # sec
        self.retry = 3

    def _agent_send(self, info):
        return self.net.send(info)

    def _agent_recv(self):
        return self.net.recv(2048, self.timeout)

    """
    @return success: respond
            fail:    None
    """
    def scpi_send(self, buf):
        # send
        self._agent_send(buf)

        retry = self.retry
        while (retry >= 0):
            retry -= 1
            # recv
            rdata = self._agent_recv()
            if (not rdata) or len(rdata) == 0: break # timeout
            return rdata[0]
        return None

    @staticmethod
    def str2arr(s):
        return [ord(c) for c in s]

    # ======================================================
    # implement interface
    # ======================================================
    def open(self, uri):
        # URI: scpi://127.0.0.1:5024
        print(uri)
        self.net.open(uri)

    def close(self):
        self.net.close()

    def get_oam(self, inst, reg, dst = None):
        ret = self.scpi_send(":OAMR 0x%02x%02x"%(inst, reg))
        if ret :
            return int(ret, 16)
        else:
            return None;

    def set_oam(self, inst, reg, value, dst = None):
        ret = self.scpi_send(":OAMW 0x%02x%02x 0x%04x"%(inst, reg, value))
        if ret :
            return ret
        else:
            return None;

    def get_ana(self, reg, dst = None):
        ret = self.scpi_send(":ANAR 0x%04x"%(reg))
        if ret :
            return int(ret, 16)
        else:
            return None;

    def set_ana(self, reg, value, dst = None):
        ret = self.scpi_send(":ANAW 0x%04x 0x%04x"%(reg, value))
        if ret :
            return ret
        else:
            return None;

    def get_tuner(self, reg):
        ret = self.scpi_send(":TUNR 0x%02x"%(reg))
        if ret :
            return int(ret, 16)
        else:
            return None;

    def set_tuner(self, reg, data):
        ret = self.scpi_send(":TUNW 0x%02x 0x%02x"%(reg, data))
        if ret :
            return ret
        else:
            return None;

    def setup_dbgc(self, cs, tr_event, tp, tr_mode, dst = None):
        ret = self.scpi_send(":DBGC:SET 0x%08x 0x%08x 0x%08x 0x%08x"%(cs, tr_event, tp, tr_mode))
        if ret :
            return ret
        else:
            return None

    def dump_dbgc(self, samples = 2048, dst = None):
        wait_times = 3
        while (wait_times >= 0):
            ret = self.scpi_send(":DBGC:STAT?")
            if not ret:
                return None # timeout
            if ret in 'READY':
                break
            # not ready
            wait_times -= 1
            time.sleep(0.5)

            if wait_times == 0:
                return None

        start_addr = 0
        data = []
        while True:
            d = self.scpi_send(":DBGC:DUMP 0x%x" %(start_addr))
            if d is None:
                break

            d = self.str2arr(d)

            l = int(''.join(map(lambda x:"%02x"%x, d[0:4])), 16)
            print("--->", start_addr, l)

            if l == 0:
                break

            start_addr += l

            for x in range(0, l*4, 4):
                k = int(''.join(map(lambda x:"%02x"%x, d[x+4:x+8])), 16)
                data.append(k)

            if start_addr >= samples:
                break

        print("total len ->", len(data))
        return data

    def list_resource(self):
        return self.net.list_resource()

if __name__ == "__main__":
    c88xx = SCPIAgent()
    device_list = c88xx.list_resource()
    print(device_list)

    c88xx.open("scpi://127.0.0.1:5024")

    # oam test
    llid = 0x7e
    reg = 0x74

    print "set_oam"
    print(c88xx.set_oam(llid, reg, 0x55aa))

    print "get oam"
    print("OAM[%04x] = 0x%04x"%(((llid << 8 | reg), c88xx.get_oam(llid, reg))))

    print "set ana"
    print(c88xx.set_ana(0x0008, 0x1234))

    print "get_ana"
    print("ANA[%04x] = 0x%04x"%(0x0008, c88xx.get_ana(0x0008)))

    print "set_tuner"
    print(c88xx.set_tuner(0x03, 0x5a))

    print "get_tuner"
    print("TUNER[%02x] = 0x%02x"%(0x03, c88xx.get_tuner(0x03)))
