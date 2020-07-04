import sys
import base64

sys.path.append('../src/')
import UtilityNum as num
import RSA as rsa

def main():
    ### generate_key test ###
    """
    (mod, pub, pri, p, q) = rsa.generate_key(4096)
    prime_test = num.miller_rabin(p) and num.miller_rabin(q)
    mod_test = mod == p * q
    key_test = (pub * pri) % ((p - 1) * (q -1)) == 1
    print("generate_key (passed):", prime_test and mod_test and key_test)

    m = str(mod) + "\n\n" + str(pub) + "\n\n" + str(pri)
    with open("n.txt", "w") as f:
        f.write(m)

    ### encrypt test ###
    original = "hello, world!"
    m = int.from_bytes(str.encode(original), "big")

    e = rsa.RSA(mod, pub)
    d = rsa.RSA(mod, pri)

    ct = e.encrypt(m)
    pt = d.encrypt(ct)

    print("Encrypt/decrypt (passed):", bytes.fromhex(hex(pt)[2:]).decode() == original)
    """

    test1 = "a".encode()
    test2 = "ab".encode()
    test3 = "hello".encode()

    print(base64.b64encode(test1).decode("utf-8"))
    print(base64.b64encode(test2).decode("utf-8"))
    print(base64.b64encode(test3).decode("utf-8"))

if __name__ == "__main__":
    main()
