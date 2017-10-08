__author__ = "Alekos Filini, Daniela Brozzoni"
__license__ = "BSD-3-Clause"
__version__ = "1.0"
__status__ = "Develop"

class ASN1:
    """
    A tiny ASN1 parser which supports the BER format.
    """

    def __init__(self, data):
        """
        Default constructor, immediately parses the data sent
        :param data: the array of integer representing a BER encoded tag
        """

        self.data = data

        self.root, _ = self.parse()

    def get_class(self, offset):
        """
        Applies a bitmask to isolate the class
        :param offset: offset of the object
        :return: the extracted class
        """

        return self.data[offset] & 0b11000000

    def get_type(self, offset):
        """
        Applies a bitmask to isolate the type
        :param offset: offset of the object
        :return: the extracted object type
        """

        return self.data[offset] & 0b00100000

    def get_tag(self, offset):
        """
        Parses the tag value starting from offset
        :param offset: offset of the object
        :return: a tuple containing the tag value and the new offset
        """

        if self.data[offset] & 31 == 31:
            return self.get_next_bytes_tag(offset)

        return self.data[offset] & 31, offset + 1

    def get_next_bytes_tag(self, offsetStart):
        """
        Parses the tag in the "extended" form
        :param offsetStart: initial offset
        :return: a tuple containing the parsed tag value and the new offset
        """

        tag = 0
        count = 1
        while True:
            tag = tag | (self.data[offsetStart + count] & 0b01111111)

            if (self.data[offsetStart + count] & 0b10000000) == 0:
                break

            tag = tag << 7
            count += 1

        return tag, offsetStart + count + 1

    def parse_length(self, offset):
        """
        Extracts the length from the BER-encoded buffer
        :param offset: initial offset
        :return: a tuple containing the parsed length and the new offset
        """

        if self.data[offset] == 0x80: # unknown length
            count = 0
            while self.data[offset + count] != 0x00 and self.data[offset + count + 1] != 0x00:
                count += 1

            return count, offset + 1

        if self.data[offset] < 128:
            return self.data[offset], offset + 1

        lenBytes = self.data[offset] - 128
        len = 0

        for i in range(lenBytes):
            len = len << 8
            len = len | self.data[offset + i + 1]

        return len, offset + lenBytes + 1

    def get_bytes(self, offset, num):
        """
        Returns `num` bytes starting from `offset`
        :param offset: initial offset
        :param num: number of bytes
        :return: a tuple containing the bytes extracted and the new offset
        """

        return self.data[offset:offset + num], offset + num

    def parse(self, offset=0):
        """
        Parses the content of the buffer
        :param offset: initial offset, defaults to zero
        :return: a tuple containing the parsed buffer and the new offset
        """

        type = self.get_type(offset)
        tag, newOffset = self.get_tag(offset)
        length, newOffset = self.parse_length(newOffset)
        bytes, lastOffset = self.get_bytes(newOffset, length)

        children = []

        if type != 0: # structured
            childrenBytes = 0
            while childrenBytes < length:
                data, newChildrenOffset = self.parse(newOffset + childrenBytes)
                children.append(data)

                childrenBytes = newChildrenOffset - newOffset

        ans = {
            'tag': tag,
            'length': length,
            'bytes': bytes,
            'children': children,
            'verify': lambda d: d == bytes
        }

        return ans, lastOffset

    def pretty_print(self, obj=None, indent=0):
        """
        Recursively prints the content of the tag
        :param obj: Entry point, defaults to self.root
        :param indent: Initial intendation level, defaults to 0
        """

        if obj is None:
            return self.pretty_print(self.root)

        print('  ' * indent + ('[{}]: {}'.format(obj['tag'], obj['bytes'])))
        for c in obj['children']:
            self.pretty_print(c, indent + 1)