mask64 = (2 ** 64) - 1
mask8 = (2 ** 8) - 1

'''
Converts a number into a string, using ascii by default.

num_to_text: number, string (optional) -> string
'''
def num_to_text(n, mode = "ascii"):
    num = hex(n)[2:]
    # python drops preceding 0
    if (len(num) % 2 != 0):
        num = '0' + num
    return bytes.fromhex(num).decode(mode)

def num_to_bytes(n):

    num = hex(n)[2:]
    # python drops preceding 0
    if (len(num) % 2 != 0):
        num = '0' + num
    return bytes.fromhex(num)

'''
Reads a string of bytes into an array of ints, each of which corresponds to
a byte in the string

process_bytes: str -> array(int)
'''
def hex_string_to_bytes(s, pad = 0):
    s = s.replace(' ', '')
    if pad != 0:
        pad_len = pad - len(s)
    else:
        pad_len = len(s) % 2

    s = '0' * pad_len + s

    r = [0] * int(len(s)/2)

    for i in range(len(r)):
        r[i] = int(s[2*i:(2*i) + 2],16)

    return r

'''
Converts an array of bytes into a single integer

bytes_to_int: array(byte), bool -> int
'''
def bytes_to_int(bytes, big_endian = True):
    r = 0x0

    if (big_endian):
        bytes = bytes[::-1]

    for i in bytes:
        r = r << 8
        r = r + i

    return r

'''
Rotates a 64 bit integer x, n bits to the left.

rotate_l64: int, int -> int
'''
def rotate_l64(x, n):
    left_n_bits = ((-1 << 64) & (x << n)) >> 64
    x_shift = mask64 & (x << n)
    return x_shift + left_n_bits

'''
Process the bit string into an integer.

process: str, bool -> int
'''
def process(str, pad = 0, big_endian = True):
    return bytes_to_int(hex_string_to_bytes(str, pad), big_endian)

'''
Rotates a 64 bit integer x, n bits to the right.

rotate_r64: int, int -> int
'''
def rotate_r64(x, n):
    right_n_bits = (x & ((2 ** n) - 1)) << (64 - n)
    x_shift = x >> n
    return x_shift + right_n_bits
