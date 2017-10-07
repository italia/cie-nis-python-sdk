import copy
import random
import hashlib

def string_to_byte(s):
	return [int(x, 16) for x in map(''.join, zip(*[iter(s)]*2))]

def string_to_chars_values(s):
	return [ord(x) for x in list(s)]

def get_sha1(data):
	m = hashlib.sha1()
	m.update(bytearray(data))

	return [ord(i) for i in list(m.digest())]

def nfc_response_to_array(resp):
	return string_to_byte(resp.replace(' ', ''))

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

def byte_to_string(byte):
	hex_string = "".join("%02x" % b for b in byte)
	return hex_string

def checkdigit(data):
	tot = 0
	curval = 0
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
				else:
					raise Exception('Not a valid character')
		tot += curval * weight[i % 3]
	tot = tot % 10
	return ord('0') + tot

def getIsoPad(data):
	if len(data) & 0x7 == 0:
		padLen = len(data) + 8
	else:
		padLen = len(data) - (len(data) & 0x7) + 0x08
	padData = [None] * padLen
	for i in range(0, len(data)):
		padData[i] = data[i]
	#print len(padData)
	padData[len(data)] = 0x80
	for i in range(len(data) + 1, len(padData)):
		padData[i] = 0
	return padData

def getRandomBytes(size):
	random.seed()
	a = []
	for i in range(0, size):
		a.append(random.randint(0,255))
	return a

def stringXor(a, b):
	if len(a) != len(b):
		raise Exception("Lunghezze diverse in stringXor")
	data = []
	for i in range(0, len(a)):
		data.append(a[i] ^ b[i])
	return data

def lenToBytes(value):
	if (value<0x80):
		return [value]
	
	if (value<=0xff): 
		return [0x81,value]
	
	elif (value<=0xffff): 
		return [0x82,value >> 8,value & 0xff]
	
	elif (value<=0xffffff): 
		return [0x83, (value >> 16), ((value>> 8) & 0xff), (value & 0xff)]
	
	elif (value<=0xffffffff): 
		return [0x84, (value >>24), ((value>> 16) & 0xff), ((value>> 8) & 0xff), (value & 0xff)]
	
	raise Exception("Dati troppo lunghi")

def asn1Tag(array, tag): 
	_tag=  tagToByte(tag)
	_len= lenToBytes(len(array))
	data=[0] * (len(_tag)+len(_len)+len(array))

	data = _tag + _len + array
	return data;


def tagToByte(value):
	if (value<=0xff): 
		return [value]
	
	elif (value<=0xffff): 
		return [(value >> 8),(value & 0xff)]
	
	elif (value<=0xffffff): 
		return [(value>> 16), ((value>> 8) & 0xff), (value & 0xff)]
	
	elif (value<=0xffffffff): 
		return [(value>>24), ((value>> 16) & 0xff),((value>> 8) & 0xff), (value & 0xff)]
	
	raise Exception("tag troppo lungo")

def isoRemove(data):
	for i in range(len(data) - 1, -1, -1):
		if(data[i] == 0x80): 
			break
		if(data[i] != 0x00):
			raise Exception("Padding ISO non presente")
	return data[:i]