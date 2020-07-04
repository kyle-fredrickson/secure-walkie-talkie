import UtilityBit

class Simon128_256:
    ### Simon128/256 Constants ###
    word_size = 64
    rounds = 72
    m = 4

    z = 0b11110111001001010011000011101000000100011011010110011110001011
    z_len = 62
    c = (2 ** 64) - 4

    def __init__(self, key):
        self.key = self.key_schedule(UtilityBit.process(key, 64))

    '''
    Computes the key schedule from the integer key given.

    key_schedule: int -> array(int)
    '''
    def key_schedule(self, key):
        key_schedule = [0] * Simon128_256.rounds

        for i in range(4):
            mask = UtilityBit.mask64 << (64 * i)
            key_schedule[i] = (key & mask) >> (64 * i)

        for i in range(4,72):
            tmp = UtilityBit.rotate_r64(key_schedule[i-1], 3)
            tmp = tmp ^ key_schedule[i-3]
            tmp = tmp ^ UtilityBit.rotate_r64(tmp, 1)

            zi = (Simon128_256.z & (1 << ((i - 4) % Simon128_256.z_len))) >> ((i - 4) % Simon128_256.z_len)

            key_schedule[i] = Simon128_256.c ^ zi ^ key_schedule[i - Simon128_256.m] ^ tmp

        return key_schedule

    def encrypt(self, pt):
        (x, y) = Simon128_256.split(pt)

        for ki in self.key:
            (x,y) = Simon128_256.encrypt_round(x, y, ki)

        return (x << 64) + y

    def decrypt(self, ct):
        (x, y) = Simon128_256.split(ct)

        for ki in reversed(self.key):
            (x,y) = Simon128_256.decrypt_round(x,y,ki)


        return (x << 64) + y

    ### Static Functions Below ###

    def encrypt_round(x, y, key):
        return (y ^ Simon128_256.f(x) ^ key, x)

    def decrypt_round(x, y, key):
        return (y, x ^ Simon128_256.f(y) ^ key)

    def f(x):
        return (UtilityBit.rotate_l64(x,1) & UtilityBit.rotate_l64(x,8)) ^ UtilityBit.rotate_l64(x,2)


    '''
    Process the 128 bit string into a big endian integer, then splits it into
    two halves.

    process: str -> (int64, int64)
    '''
    def split(s):
        if isinstance(s, str):
            i = UtilityBit.process(s, 32)
        else:
            i = s

        x = (i & (UtilityBit.mask64 << 64)) >> 64
        y = i & UtilityBit.mask64

        return (y, x)
