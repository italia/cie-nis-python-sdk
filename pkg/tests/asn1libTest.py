import unittest

from pkg.lib.asn1lib import *


class TestAlgorithms(unittest.TestCase):
    def setUp(self):
        pass

    def test_ASN1_01(self):
        data = [0x04, 0x05, 0x12, 0x34, 0x56, 0x78, 0x90]
        parser = ASN1(data)
        self.assertEqual(4, parser.root['tag'])
        self.assertEqual(5, parser.root['length'])
        self.assertEqual([0x12, 0x34, 0x56, 0x78, 0x90], parser.root['bytes'])

    def test_ASN1_02(self):
        data = [0xdf, 0x82, 0x02, 0x05, 0x12, 0x34, 0x56, 0x78, 0x90]
        parser = ASN1(data)
        self.assertEqual(258, parser.root['tag'])
        self.assertEqual(5, parser.root['length'])
        self.assertEqual([0x12, 0x34, 0x56, 0x78, 0x90], parser.root['bytes'])

if __name__ == '__main__':
    unittest.main()
