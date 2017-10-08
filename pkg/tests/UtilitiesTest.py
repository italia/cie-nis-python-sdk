#!/usr/bin/env python
import unittest

from pkg.lib.Utilities import *

__author__ = "Alekos Filini, Daniela Brozzoni"
__license__ = "BSD-3-Clause"
__version__ = "1.0"
__status__ = "Develop"

class TestUtilities(unittest.TestCase):
	def setUp(self):
		pass

	def test_string_to_byte(self):
		s = "009028493813940293"
		result = string_to_byte(s)
		self.assertEqual([0, 144, 40, 73, 56, 19, 148, 2, 147], result)

	def test_string_to_chars_values(self):
		s = "90328594"
		result = string_to_chars_values(s)
		self.assertEqual([57, 48, 51, 50, 56, 53, 57, 52], result)

	def test_get_sha1(self):
		data = 123456789
		result = get_sha1(data)
		self.assertEqual([148, 204, 15, 207, 109, 66, 124, 61, 160, 230, 107, 169, 134, 204, 97, 5, 107, 229, 117, 24], result)

	def test_nfc_response_to_array(self):
		resp = "09 08 23 45 56 90"
		result = nfc_response_to_array(resp)
		self.assertEqual([9, 8, 35, 69, 86, 144], result)

	def test_unsignedToBytes(self):
		b = 90
		result = unsignedToBytes(b)
		self.assertEqual(90, result)

	def test_byte_to_string(self):
		byte = [0, 34, 78, 9, 95]
		result = byte_to_string(byte)
		self.assertEqual("00224e095f", result)

	def test_checkdigit(self):
		data = [ord('A'), ord('B'), ord('<')]
		result = checkdigit(data)
		self.assertEqual(51, result)

	def test_getIsoPad(self):
		data = [23, 54, 9, 123]
		result = getIsoPad(data)
		self.assertEqual([23, 54, 9, 123, 128, 0, 0, 0], result)

	def test_stringXor(self):
		a = [0, 1, 2, 3, 4]
		b = [5, 6, 7, 8, 9]
		result = stringXor(a, b)
		self.assertEqual([5, 7, 5, 11, 13], result)

	def test_lenToBytes(self):
		value = 180
		result = lenToBytes(value)
		self.assertEqual([129, 180], result)

	def test_asn1Tag(self):
		array = [1, 2, 3, 4]
		tag = 19
		result = asn1Tag(array, tag)
		self.assertEqual([19, 4, 1, 2, 3, 4], result)

	def test_tagToByte(self):
		value = 1530
		result = tagToByte(value)
		self.assertEqual([5, 250], result)

	def test_isoRemove(self):
		data = [0x01, 0x02, 0x03, 0x04, 0x80, 0x00, 0x00, 0x00]
		result = isoRemove(data)
		self.assertEqual([1, 2, 3, 4], result)


if __name__ == '__main__':
    unittest.main()
