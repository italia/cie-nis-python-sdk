class ASN1:
    def __init__(self, data):
        self.data = data

        self.root, _ = self.parse()

    def get_class(self, offset):
        return self.data[offset] & 0b11000000

    def get_type(self, offset):
        return self.data[offset] & 0b00100000

    def get_tag(self, offset):
        if self.data[offset] & 31 == 31:
            return self.get_next_bytes_tag(offset)

        return self.data[offset] & 31, offset + 1

    def get_next_bytes_tag(self, offsetStart):
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
        if self.data[offset] == 0x80: # unknown length
            count = 0
            while self.data[offset + count] != 0x00 and self.data[offset + count + 1] != 0x00:
                count += 1

            return count + 1, offset + 1

        if self.data[offset] < 128:
            return self.data[offset], offset + 1

        lenBytes = self.data[offset] - 128
        len = 0

        for i in range(lenBytes):
            len = len << 8
            len = len | self.data[offset + i + 1]

        return len, offset + lenBytes + 1

    def get_bytes(self, offset, num):
        return self.data[offset:offset + num], offset + num

    def parse(self, offset=0):
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
            'children': children
        }

        return ans, lastOffset

    def pretty_print(self, obj=None, indent=0):
        if obj is None:
            return self.pretty_print(self.root)

        print('  ' * indent + ('[{}]: {}'.format(obj['tag'], obj['bytes'])))
        for c in obj['children']:
            self.pretty_print(c, indent + 1)