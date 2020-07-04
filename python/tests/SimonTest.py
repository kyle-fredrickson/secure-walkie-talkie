import sys

sys.path.append('../src/')
from Simon import Simon128_256
import UtilityBit as Utility

def main():
    #int_k = 0x1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100
    #int_p = 0x74206e69206d6f6f6d69732061207369
    #int_c = 0x8d2b5579afc8a3a03bf72a87efe7b868

    p = '69 73 20 61 20 73 69 6d 6f 6f 6d 20 69 6e 20 74'
    k = '00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f'
    c = '68 b8 e7 ef 87 2a f7 3b a0 a3 c8 af 79 55 2b 8d'

    s = Simon128_256(k)

    encrypted = s.encrypt(p)
    print('encrypt (passed):', encrypted == Utility.process(c))

    decrypted = s.decrypt(encrypted)
    print('decrypt (passed):', decrypted == Utility.process(p))

    print('Simon pad (passed):', Simon128_256('').encrypt(p) == Simon128_256('0'*64).encrypt(p))


if __name__ == "__main__":
    main()
