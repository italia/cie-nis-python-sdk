def string_to_byte(s):
	return [int(x, 16) for x in map(''.join, zip(*[iter(s)]*2))]

def string_to_chars_values(s):
	return [ord(x) for x in list(s)]

def nfc_response_to_array(resp):
	return string_to_byte(resp.replace(' ', ''))

def toUint(dataB):
  return int(bytes.encode('hex'), 16)

def PadInt(value, size):
	sz = value[size:]
	print byte_to_string(sz)
	if len(sz) < size:
		return sz
	return fill(size - sz.size(), 0) + sz

def fill(size, content):
	a = []
	for i in range (0, size):
		a.append(content)
	return a

def unsignedToBytes(b):
	return b & 0xFF

def lenToBytes(value):
	pass

def byte_to_string(byte):
	hex_string = "".join("%02x" % b for b in byte)
	return hex_string

def checkdigit(data):
	tot = 0
	weight =  [7, 3, 1]
	for i in range(0, len(data)):
		ch = chr(data[i]).upper()
		#print ch
		if ch >= 'A' and ch <= 'Z':
			curval = ord(ch) - ord('A') + 10
		else:
			if ch >= '0' and ch <= '9':
				curval = ord(ch) - ord('0')
			else:
				if ch == '<':
					curval = 0
		tot += curval * weight[i % 3]
	tot = tot % 10
	return ord('0') + tot
