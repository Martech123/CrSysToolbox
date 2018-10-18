import unittest
import os
import sys
import filecmp

sys.path.append("../")
from fw_gen import fw_gen

def bin_dir(file_name = ""):
    return "../bin/%s" % (file_name)

def build_dir(file_name = ""):
    return "../build/%s" % (file_name)

class TestCLTNICMode(unittest.TestCase):
    def setUp(self):
        build_path = build_dir()
        try:
            os.makedirs(build_path)
        except OSError, e:
            pass

    def test_set_nic_mode(self):
        nic_in_file  = bin_dir("clt_nic_force_100M_ori.bin")       # 1000M default
        nic_exp_file = bin_dir("clt_nic_force_100M_exp.bin")       # 100M default
        nic_out_file = build_dir("clt_nic_force_100M_pro.bin")

        in_file = nic_in_file
        out_file = nic_out_file
        exp_file = nic_exp_file

        fw = fw_gen()
        fw.load_fw(in_file)
        # print fw.get_force_nic_mode_default()
        fw.set_force_nic_mode_default(True) # set to 100M

        fw.set_csum()
        fw.save_fw(out_file, iscnu = False)
        self.assertTrue(filecmp.cmp(out_file, exp_file))

    def test_clt_band_modify(self):
        def dump_band(fw):
            print("============ dump sep ============")
            for reg in fw.get_band_reg_list():
                print(map(hex, reg))

            for freq in fw.get_band_range_list():
                print(freq)

        band_in_file  = bin_dir("clt_band_ori.bin")
        band_exp_file = bin_dir("clt_band_exp.bin")
        band_out_file = build_dir("clt_band_pro.bin")

        in_file = band_in_file
        out_file = band_out_file
        exp_file = band_exp_file

        fw = fw_gen()

        # get config from exp_file
        fw.load_fw(exp_file)
        reg_list = fw.get_band_reg_list()
        range_list = fw.get_band_range_list()
        # dump_band(fw) # for debug

        # rewrite ori firmware
        fw.load_fw(in_file)
        # dump_band(fw) # for debug
        for i, v in enumerate(reg_list):
            self.assertTrue(fw.set_band_reg(i, *v))

        for i, v in enumerate(range_list):
            self.assertTrue(fw.set_band_range(i, *v))

        # dump_band(fw) # for debug
        fw.set_csum()
        fw.save_fw(out_file, iscnu = False)
        self.assertTrue(filecmp.cmp(out_file, exp_file))

    def test_cnu_band_modify(self):
        def dump_band(fw):
            print("============ dump sep ============")
            for reg in fw.get_band_reg_list():
                print(map(hex, reg))

            for freq in fw.get_band_range_list():
                print(freq)

        band_in_file  = bin_dir("cnu_band_ori.bin")
        band_exp_file = bin_dir("cnu_band_exp.bin")
        band_out_file = build_dir("cnu_band_pro.bin")

        in_file = band_in_file
        out_file = band_out_file
        exp_file = band_exp_file

        fw = fw_gen()

        # get config from exp_file
        fw.load_fw(exp_file)
        reg_list = fw.get_band_reg_list()
        range_list = fw.get_band_range_list()
        # dump_band(fw) # for debug

        # rewrite ori firmware
        fw.load_fw(in_file)
        # dump_band(fw) # for debug
        for i, v in enumerate(reg_list):
            self.assertTrue(fw.set_band_reg(i, *v))

        for i, v in enumerate(range_list):
            self.assertTrue(fw.set_band_range(i, *v))

        # dump_band(fw) # for debug
        fw.set_csum()
        fw.save_fw(out_file, iscnu = True)
        self.assertTrue(filecmp.cmp(out_file, exp_file))

    def test_device_detect(self):
        fw_list = os.listdir(bin_dir())
        clt_fw = filter(lambda s: "clt" in s, fw_list)
        cnu_fw = filter(lambda s: "cnu" in s, fw_list)
        self.assertTrue(len(clt_fw) != 0)
        self.assertTrue(len(cnu_fw) != 0)

        fw = fw_gen()
        for filename in clt_fw:
            fw.load_fw(bin_dir(filename))
            self.assertTrue("clt" == fw.get_firmware_type())

        for filename in cnu_fw:
            fw.load_fw(bin_dir(filename))
            fw.load_fw(bin_dir(filename))
            self.assertTrue("cnu" == fw.get_firmware_type())

    def test_band_unsupport(self):
        old_version = bin_dir("clt_band_unsupport_ana15.bin")
        fw = fw_gen()
        fw.load_fw(old_version)
        success = None
        try:
            fw.get_band_reg_list()
            success = True
        except fw_gen.ErrorBandAna15Unsupported:
            success = False
        except:
            success = None

        self.assertTrue(success == False)

    @unittest.skip("demo for unittest.skip")
    def test_whatever(self):
        pass

if __name__ == '__main__':
     unittest.main()

# vim: filetype=python:expandtab:shiftwidth=4:tabstop=4:softtabstop=4:textwidth=80
