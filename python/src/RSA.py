import UtilityNum as num

"""
Computes a key of a given bit length.

generate_key: int -> (num, num, num, num, num)
"""
def generate_key(bit_length):
    pub_key = 175518779140055473152055560377614473706321608372224849783176900881247706934619137654601067505752406128373059055605124458183451145791362200343650488212317096727334429680532770657934367823725527876116922402459932729312443746078826778556542555163434180837205316472641883453751693125237182677695830439753149390723

    modulus = 0
    priv_key = 0

    i = 0
    while True:

        print(i)
        i += 1
        p = num.generate_prime(bit_length//2)
        q = num.generate_prime(bit_length//2)

        modulus0 = p * q
        totient = (p - 1) * (q - 1)

        try:
            priv_key = num.inverse(pub_key, totient)
            modulus = modulus0
            break
        except:
            print("gcd not zero")
            pass

    return (modulus, pub_key, priv_key, p, q)

"""
Performs the RSA computation given a modulus and a key.
"""
class RSA:
    def __init__(self, mod, key):
        self.modulus = mod
        self.key = key

    """
    Raises pt to the self.key-th power mod self.modulus

    encrypt: num -> num
    """
    def encrypt(self, pt):
        return pow(pt, self.key, self.modulus)
