#!/usr/bin/env python3

import argparse
import getpass
import json
import os
import subprocess
import sys

sys.path.append("../src")

import DHKE as d
import RSA as rsa
import UtilityConfig as uc
import UtilityProtocol as p

def main():
    bob_config = uc.UtilityConfig("../config/Bob.json")

    bob_rsa_n = bob_config.rsa_n
    bob_rsa_pri = bob_config.rsa_pri
    bob_rsa_pub = bob_config.rsa_pub

    bob_rsa_decrypt = rsa.RSA(bob_rsa_n, bob_rsa_pri)
    bob_rsa_encrypt = rsa.RSA(bob_rsa_n, bob_rsa_pub)

    bob_diffie = d.DHKE(bob_config.dh_p, bob_config.dh_g)
    bob_diffie_pub = bob_diffie.X

    alice_config = uc.UtilityConfig("../config/Alice.json")

    alice_rsa_n = alice_config.rsa_n
    alice_rsa_pri = alice_config.rsa_pri
    alice_rsa_pub = alice_config.rsa_pub

    alice_rsa_decrypt = rsa.RSA(alice_rsa_n, alice_rsa_pri)
    alice_rsa_encrypt = rsa.RSA(alice_rsa_n, alice_rsa_pub)

    alice_diffie = d.DHKE(alice_config.dh_p, alice_config.dh_g)
    alice_diffie_pub = alice_diffie.X

    # Bob sends request to Alice
    (b_request_enc, b_tod) = p.compute_request(bob_diffie_pub, bob_rsa_decrypt, alice_rsa_encrypt)

    # Alice receives a request from someone
    (a_bob_diffie_pub, a_tod, name) = p.decrypt_request(b_request_enc, alice_rsa_decrypt, alice_config.contacts)

    a_their_rsa_encrypt = rsa.RSA(alice_config.get_rsa_n(name), alice_config.get_rsa_pub(name))

    print("Bob's diffie_pub successfully communicated:", a_bob_diffie_pub == bob_diffie_pub)
    print("ToD successfully communicated:", b_tod == a_tod)

    # Alice sends a response to Bob
    a_response_enc = p.compute_response(alice_diffie_pub, alice_rsa_decrypt, a_their_rsa_encrypt, a_tod)

    # Bob recieves a response from Alice
    b_alice_diffie_pub = p.decrypt_response(a_response_enc, bob_rsa_decrypt, alice_rsa_encrypt, b_tod)

    print("Alice's diffie_pub successfully communicated:",b_alice_diffie_pub == alice_diffie_pub)

    # Check shared secret
    bob_ss = p.get_shared_secret(bob_diffie, b_alice_diffie_pub)
    alice_ss = p.get_shared_secret(alice_diffie, a_bob_diffie_pub)

    print("Shared secret is in common:", bob_ss == alice_ss)

    # Bob computes Header/Data
    message = b"Well bon jour world! I don't know where I'm at!"
    b_header, b_message_enc = p.compute_header_data(message, bob_diffie, b_alice_diffie_pub, b_tod)

    # Alice verifies/decrypts data
    a_message = p.decrypt_data(b_header["tag"], b_message_enc, alice_diffie, a_bob_diffie_pub, a_tod)

    print("Message successfully communicated:", message == a_message)
    print(a_message)

if __name__ == "__main__":
    main()
