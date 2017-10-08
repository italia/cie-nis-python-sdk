import unittest

from pkg.lib.Algorithms import *


class TestAlgorithms(unittest.TestCase):
    def setUp(self):
        pass

    # ------- MAC ENC ----------

    def test_mac_enc_key_8(self):
        key = [0x22, 0x88, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
        data = [10, 20, 30, 40, 50, 60, 70, 80]

        result = macEnc(key, data)
        self.assertEqual([23, 178, 198, 248, 245, 165, 8, 101], result)

    def test_mac_enc_key_9(self):
        key = [0x22, 0x88, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00]
        data = [10, 20, 30, 40, 50, 60, 70, 80]

        result = macEnc(key, data)
        self.assertEqual([23, 178, 198, 248, 245, 165, 8, 101], result)

    def test_mac_enc_key_16(self):
        key = [0x22, 0x88, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00]
        data = [10, 20, 30, 40, 50, 60, 70, 80]

        result = macEnc(key, data)
        self.assertEqual([247, 80, 35, 172, 217, 38, 86, 53], result)

    def test_mac_enc_key_17(self):
        key = [0x22, 0x88, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11]
        data = [10, 20, 30, 40, 50, 60, 70, 80]

        result = macEnc(key, data)
        self.assertEqual([247, 80, 35, 172, 217, 38, 86, 53], result)

    # ------- DES ENC ----------

    def test_des_enc_key_8(self):
        key = [0x22, 0x88, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
        data = [10, 20, 30, 40, 50, 60, 70, 80, 10, 20, 30, 40, 50, 60, 70, 80, 10, 20, 30, 40, 50, 60, 70, 80]

        result = desEnc(key, data)
        self.assertEqual([23, 178, 198, 248, 245, 165, 8, 101, 165, 213, 156, 236, 227, 206, 48, 11, 109, 53, 186, 176, 219, 134, 34, 71], result)

    def test_des_enc_key_16(self):
        key = [0x22, 0x88, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00]
        data = [10, 20, 30, 40, 50, 60, 70, 80, 10, 20, 30, 40, 50, 60, 70, 80, 10, 20, 30, 40, 50, 60, 70, 80]

        result = desEnc(key, data)
        self.assertEqual([247, 80, 35, 172, 217, 38, 86, 53, 206, 1, 123, 91, 36, 118, 195, 248, 142, 69, 45, 123, 74, 67, 63, 61], result)

    # -------- DES DEC ----------

    def test_des_dec_key_8(self):
        encData = [23, 178, 198, 248, 245, 165, 8, 101, 165, 213, 156, 236, 227, 206, 48, 11, 109, 53, 186, 176, 219, 134, 34, 71]
        key = [0x22, 0x88, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]

        result = desDec(key, encData)
        self.assertEqual([10, 20, 30, 40, 50, 60, 70, 80, 10, 20, 30, 40, 50, 60, 70, 80, 10, 20, 30, 40, 50, 60, 70, 80], result)

    def test_des_dec_key_16(self):
        encData = [247, 80, 35, 172, 217, 38, 86, 53, 206, 1, 123, 91, 36, 118, 195, 248, 142, 69, 45, 123, 74, 67, 63, 61]
        key = [0x22, 0x88, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00]

        result = desDec(key, encData)
        self.assertEqual([10, 20, 30, 40, 50, 60, 70, 80, 10, 20, 30, 40, 50, 60, 70, 80, 10, 20, 30, 40, 50, 60, 70, 80], result)

if __name__ == '__main__':
    unittest.main()
