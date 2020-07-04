import sys

sys.path.append('../src/')
from CounterMode import CounterMode

def main():
    simon_k = '0' * 32
    c = CounterMode(simon_k)
    ks = c.key_stream(1234, 19)
    ks_string = hex(ks[0])[2:] + hex(ks[1])[2:]

    text = b"cool stuff it's true"
    ct = c.encrypt(text, 1234)
    pt = c.decrypt(ct, 1234)
    print(pt)

    """
    # Key Stream Test
    print("key_stream test passed: ", ks_string == "3b0dc3ef4b6dc4630d4a0e23770eedc5841a55d4947ebc07439587b1d878706d")


    enc_string = "5562b4cf221ee417652f2e571e6388e5e27527f4f512d02724fae8d5f8151503defa5a225db5015237159d4dd05180b9ede464d70f07786630d062ad394481812103ff95"
    input_string = "now is the time for all good men to come to the aid of their country"


    encrypt = c.encrypt(input_string.encode('utf-8'), 1234)
    print(encrypt.hex())
    print(enc_string.encode("utf-8"))

    # encryption test
    print("encryption test passed: ", encrypt == enc_string.encode("utf-8"))


    decrypt = c.decrypt(bytes.fromhex(enc_string), 1234)

    #decryption test
    print("decryption test passed: ", decrypt.decode('utf-8', 'replace') == input_string)


    # James encrypted recording
    recording_enc_bytes = open("recording_data/recording.encrypted", "rb").read()

    # James recording
    recording_bytes = open("recording_data/recording.m4a", "rb").read()

    # our encryption of his recording
    my_enc_rec = c.encrypt(recording_bytes, 1234)

    # test lengths of encryption
    print("Length of James Encrypted and Our Encrypted Test: ", len(recording_enc_bytes) == len(my_enc_rec))

    # decrypt our own encryption and save to file
    my_dec_rec = c.decrypt(my_enc_rec, 1234)
    f = open('recording_data/test_full_path.m4a', 'wb')
    f.write(my_dec_rec)
    f.close()

    # decrypt James encryption and save to file
    dec_rec = c.decrypt(recording_enc_bytes, 1234)
    f = open('recording_data/test_encrypted_file.m4a', 'wb')
    f.write(dec_rec)
    f.close()
    """

if __name__ == "__main__":
    main()
