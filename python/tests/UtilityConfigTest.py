import sys

sys.path.append('../src/')
from UtilityConfig import UtilityConfig
from RSA import RSA as rsa

def main():
    uc = UtilityConfig("../config/test.json")
    print("Constructor passed:", uc != None)

    print("Name passed:", uc.name == "test")
    print("IP passed:", uc.ip == "localhost")
    print("Port passed:", uc.port == 8123)
    print("RSA_n passed:", type(uc.rsa_n) == int)
    print("RSA_pub passed:", type(uc.rsa_pub) == int)
    print("RSA_pri passed:", type(uc.rsa_pri) == int)
    print("DH_p passed:", type(uc.dh_p) == int)
    print("DH_g passed:", type(uc.dh_g) == int)
    print("Contacts passed:", uc.contacts != None and len(uc.contacts) > 0)

    test_crypto_vals = (uc.rsa_n != uc.rsa_pub and uc.rsa_n != uc.dh_p and uc.rsa_n != uc.dh_g and uc.rsa_n != uc.rsa_pri) #incomplete
    print("Crypto values passed:", test_crypto_vals)

    enc = rsa(uc.rsa_n, uc.rsa_pub)
    dec = rsa(uc.rsa_n, uc.rsa_pri)

    x = 12343478349570835789

    rsa_test = dec.encrypt(enc.encrypt(x)) == x

    print("RSA key passed:", rsa_test)

    try:
        non = uc.get_contact("A name I do not know")
        print("Get Unknown Contact passed:", False)
    except:
        print("Get Unknown Contact passed:", True)

    jim = uc.get_contact("Jim")
    print("Get Contact, Jim, passed:", jim != None)
    jim_rsa_n = uc.get_rsa_n("Jim")
    print("Get Jim's rsa_n passed:", type(jim_rsa_n) == int)

if __name__ == "__main__":
    main()
