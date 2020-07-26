import base64

#

def bytes_to_bint(b):
    r = 0x0

    for i in b:
        r = r << 8
        r = r + i

    return r

def bint_to_bytes(n):
    return bytes.fromhex(hex(n)[2:])

#

def ascii_to_bint(s):
    return bytes_to_bint(s.encode())

def bint_to_ascii(n):
    return bint_to_bytes(n).decode('ascii')

#

def bint_to_b64_string(n):
    return base64.b64encode(str(n).encode()).decode("utf-8")

def b64_string_to_bint(s):
    return int(base64.b64decode(s).decode("utf-8"), 10)

#

def bytes_to_b64_string(b):
    return base64.b64encode(b).decode("utf-8")

def b64_string_to_bytes(s):
    return base64.b64decode(s)