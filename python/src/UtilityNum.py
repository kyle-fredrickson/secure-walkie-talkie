from random import randint

import SHA3 as hash

def inverse(k, mod):
    k = k % mod
    (gcd, t, s) = extended_euclidian_algorithm(mod, k)

    if not gcd == 1:
        raise Exception("gcd in inverse was not 1")

    return (t + mod) % mod

def gcd(a, b):
    if a > b:
        (gcd , t, s) = extended_euclidian_algorithm(a, b)
    else:
        (gcd , t, s) = extended_euclidian_algorithm(b, a)
    return gcd

def extended_euclidian_algorithm(r0, r1):
    if not r0 > r1:
        raise Exception("parameter error")

    s = [1, 0]
    t = [0, 1]
    r = [r0, r1]
    q = []
    i = 1

    cond = True
    while cond:
        i = i + 1
        ri = r[i - 2] % r[i - 1]
        qi_1 = (r[i - 2] - ri) // r[i - 1]
        si = s[i - 2] - qi_1 * s[i - 1]
        ti = t[i - 2] - qi_1 * t[i - 1]
        r.extend([ri])
        q.extend([qi_1])
        s.extend([si])
        t.extend([ti])

        cond = (not r[i] == 0)

    return (r[i - 1], t[i - 1], s[i - 1])

def generate_random_key(byte_len = 1000):
    entropy = []
    for i in range(byte_len):
        entropy += [randint(0,255)]

    b = bytes(entropy)
    return hash.sha3_256(b)

def generate_safe_prime(bit_length):
    cond = True
    i = 0
    while cond:
        r = generate_prime(bit_length - 1)

        p = (2 * r) + 1

        cond = not (miller_rabin(p))
        print("Found candidate", i, ":", not cond)

        i += 1

    return p

def generate_prime(bit_length):
    start = pow(2, bit_length - 2)
    stop = pow(2, bit_length - 1) - 2

    seed = randint(start, stop)
    r0 = 2 * seed + 1

    while not miller_rabin(r0):
        r0 += 2

    return r0

## there's something wrong here (17 is false)
def miller_rabin(p_hat, s = 40):
    (u, r) = _compute_ur(p_hat)

    for i in range(s):
        a = randint(2, p_hat - 2)
        z = pow(a, r, p_hat)
        if (not z == 1) and (not z == (p_hat - 1)):
            for j in range(1,u):
                z = pow(z, 2, p_hat)
                if z == 1:
                    return False
            if not z == (p_hat - 1):
                return False
    return True

def _compute_ur(p_hat):
    r = p_hat - 1
    u = 0
    while r % 2 == 0:
        u += 1
        r = r // 2
    return (u, r)
