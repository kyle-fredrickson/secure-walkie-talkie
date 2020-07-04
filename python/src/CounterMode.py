from Simon import Simon128_256
from datetime import datetime
import math

'''
Computes CounterMode encryption using the Simon128/256 algorithm.
'''
class CounterMode:
	def __init__(self, simon_key):
		self.simon = Simon128_256(simon_key)


	# Params types, int, int
	# returns array of hex strings
	def key_stream(self, nonce, length):
		ks = []
		x = math.ceil((length + 15) / 16)
		for i in range(1,x + 1):
			inp = (nonce << 64) + i
			enc = self.simon.encrypt(inp)
			ks.append(enc)

		ret_ks = []
		for j in range(len(ks)):
			ks_1 = format(ks[j], 'x')

			# python drops preceding 0
			if (len(ks_1) % 2 != 0):
				ks_1 = '0' + ks_1

			ba = bytearray.fromhex(ks_1)
			ba.reverse()
			s = ''.join(format(x, '02x') for x in ba)
			ret_ks.append(int(s, 16))
		return ret_ks

	# iterate through input array and keystream and xor to get result
	def encrypt_ks(self, enc_array, ks):
		ret_bytes = bytes()
		for i in range(len(enc_array)):
			if i == len(enc_array) - 1:
				ks[i] = hex(ks[i])[2:len(enc_array[i]) + 2]

				xor_result = hex(int(ks[i], 16) ^ int(enc_array[i], 16))[2:]

				# python drops preceding 0
				if (len(xor_result) % 2 != 0):
					xor_result = '0' + xor_result

				xor_result = bytes.fromhex(xor_result)

				ret_bytes += xor_result
			else:
				xor_result = hex(ks[i] ^ int(enc_array[i], 16))[2:]

				# python drops many preceding 0's
				if (len(xor_result) != 32):
					while len(xor_result) != 32:
						xor_result = '0' + xor_result

				ret_bytes += bytes.fromhex(xor_result)
		return ret_bytes

	# Param types: bytes,  int
	# Returns bytes
	def encrypt(self, pt_bytes, nonce):
		ks = self.key_stream(nonce, len(pt_bytes))
		enc_array = string_to_array(pt_bytes.hex(), 32)

		return self.encrypt_ks(enc_array, ks)

	# Param types: bytes, int
	# Returns bytes
	def decrypt(self, ct_bytes, nonce):
		ks = self.key_stream(nonce, len(ct_bytes))
		enc_array = string_to_array(ct_bytes.hex(), 32)

		return self.encrypt_ks(enc_array, ks)

def string_to_array(input, length):
	return [input[i:i+length] for i in range(0, len(input), length)]
