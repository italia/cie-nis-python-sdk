def string_to_byte(a):
	return [int(x, 16) for x in map(''.join, zip(*[iter(a)]*2))]

#string_to_byte("A0A1")