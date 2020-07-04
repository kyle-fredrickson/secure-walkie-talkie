import sys

sys.path.append('../src/')
import UtilityBit as Utility

def main():
    byte_string = '00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f'
    true_array = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
    big_endian = 0x1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100
    little_endian = 0x102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
    byte_array = Utility.hex_string_to_bytes(byte_string)
    be_int = Utility.bytes_to_int(byte_array)
    le_int = Utility.bytes_to_int(byte_array, big_endian = False)

    print('hex_string_to_bytes passed:', byte_array == true_array)
    print('bytes_to_int (big endian) passed:', be_int == big_endian)
    print('bytes_to_int (little endian) passed:',  le_int == little_endian)

    #i = 0x12345678abcdef
    #print(i)
    #print(Utility.int_to_bytes(i))
    #print("int_to_bytes:", Utility.bytes_to_int(Utility.int_to_bytes(i)) == i)

    ltest = 0xc000000000000000
    ltrue = 3
    rtest = 3
    rtrue = 0xc000000000000000
    print('rotate_l64 passed:', Utility.rotate_l64(ltest,2) == ltrue)
    print('rotate_r64 passed:', Utility.rotate_r64(rtest,2) == rtrue)


if __name__ == "__main__":
    main()
