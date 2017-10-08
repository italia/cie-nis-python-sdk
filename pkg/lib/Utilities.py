import copy
import hashlib
import random
import hashlib

__author__ = "Alekos Filini, Daniela Brozzoni"
__license__ = "BSD-3-Clause"
__version__ = "1.0"
__status__ = "Develop"

def string_to_byte(s):
    """
    Converts an hex string to the equivalent array of integer representing the parsed bytes
    :param s: The string to process
    :return: The array of integers
    """

    return [int(x, 16) for x in map(''.join, zip(*[iter(s)] * 2))]


def string_to_chars_values(s):
    """
    Converts a string to the equivalent array of integers representing the characters
    :param s: The string to process
    :return: The array of integers
    """

    return [ord(x) for x in list(s)]


def get_sha1(data):
    """
    Returns the SHA1 digest of `data` as an array of integers
    :param data: The data to hash
    :return: The digest in form of an array of integers
    """

    m = hashlib.sha1()
    m.update(bytearray(data))

    return [ord(i) for i in list(m.digest())]


def nfc_response_to_array(resp):
    """
    Converts a NFC response to the equivalent array of integers
    :param resp: The string returned by the NFC library
    :return: The equivalent array of integers
    """

    return string_to_byte(resp.replace(' ', ''))


def unsignedToBytes(b):
    """
    Clips an integer to fit it into a byte
    :param b: The integer to process
    :return: The byte
    """

    return b & 0xFF


def byte_to_string(byte):
    """
    Converts an array of integer containing bytes into the equivalent string version
    :param byte: The array to process
    :return: The calculated string
    """

    hex_string = "".join("%02x" % b for b in byte)
    return hex_string


def checkdigit(data):
    """
    Calculates a checksum used during the EAC authentication process
    :param data: The array of integer to process
    :return: The checksum value
    """

    tot = 0
    curval = 0
    weight = [7, 3, 1]
    for i in range(0, len(data)):
        ch = chr(data[i]).upper()
        if 'A' <= ch <= 'Z':
            curval = ord(ch) - ord('A') + 10
        else:
            if '0' <= ch <= '9':
                curval = ord(ch) - ord('0')
            else:
                if ch == '<':
                    curval = 0
                else:
                    raise Exception('Not a valid character')
        tot += curval * weight[i % 3]
    tot = tot % 10
    return ord('0') + tot


def getIsoPad(data):
    """
    Adds a padding at the end of an array
    :param data: The array of integers to process
    :return: The padd-ed array
    """

    if len(data) & 0x7 == 0:
        padLen = len(data) + 8
    else:
        padLen = len(data) - (len(data) & 0x7) + 0x08
    padData = [None] * padLen
    for i in range(0, len(data)):
        padData[i] = data[i]

    padData[len(data)] = 0x80
    for i in range(len(data) + 1, len(padData)):
        padData[i] = 0
    return padData


def getRandomBytes(size):
    """
    Returns an array of `size` random integers representing bytes
    :param size: The size of the array
    :return: The array of random integers
    """

    random.seed()
    a = []
    for i in range(0, size):
        a.append(random.randint(0, 255))
    return a


def stringXor(a, b):
    """
    Calculates the bitwise xor for every value of the arrays. The arrays need to be
    equally long
    :param a: The first array
    :param b: The second array
    :return: The calculated result
    """

    if len(a) != len(b):
        raise Exception("stringXor: the two arrays must have the same size")
    data = []
    for i in range(0, len(a)):
        data.append(a[i] ^ b[i])
    return data


def lenToBytes(value):
    """
    Calculates the array of bytes that must be included into an ASN1 Tag to correctly
    represent its length
    :param value: the size of the tag
    :return: the array of integers
    """

    if value < 0x80:
        return [value]

    if value <= 0xff:
        return [0x81, value]

    elif value <= 0xffff:
        return [0x82, value >> 8, value & 0xff]

    elif value <= 0xffffff:
        return [0x83, (value >> 16), ((value >> 8) & 0xff), (value & 0xff)]

    elif value <= 0xffffffff:
        return [0x84, (value >> 24), ((value >> 16) & 0xff), ((value >> 8) & 0xff), (value & 0xff)]

    raise Exception("lenToBytes: value is too big")


def asn1Tag(array, tag):
    """
    Creates an integer array representing an ASN1 Tag by concatenating together an
    existing tag and an array of integers
    :param array: The array of integers
    :param tag: The existing tag
    :return: The new tag
    """

    _tag = tagToByte(tag)
    _len = lenToBytes(len(array))
    data = _tag + _len + array
    return data


def tagToByte(value):
    """
    Converts an ASN1 Tag into the corresponding byte representation
    :param value: The tag to convert
    :return: The integer array
    """

    if value <= 0xff:
        return [value]

    elif value <= 0xffff:
        return [(value >> 8), (value & 0xff)]

    elif value <= 0xffffff:
        return [(value >> 16), ((value >> 8) & 0xff), (value & 0xff)]

    elif value <= 0xffffffff:
        return [(value >> 24), ((value >> 16) & 0xff), ((value >> 8) & 0xff), (value & 0xff)]

    raise Exception("tagToByte: tag is too big")


def isoRemove(data):
    """
    Removes the ISO padding from an array of integers
    :param data: The data to process
    :return: The processed data
    """

    i = 0
    for i in range(len(data) - 1, -1, -1):
        if data[i] == 0x80:
            break
        if data[i] != 0x00:
            raise Exception("isoRemove: ISO padding not found")

    return data[:i]
