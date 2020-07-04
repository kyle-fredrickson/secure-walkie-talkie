import base64
from datetime import datetime
import json
from random import randint

import CounterMode as cm
import DHKE as dh
import RSA as rsa
import SHA3 as hash
import UtilityBit as ub

### Constants ###

TYPE_BYTES = 1
LENGTH_BYTES = 8
HEADER_BYTES = TYPE_BYTES + LENGTH_BYTES

REQUEST_TYPE = "1"
RESPONSE_TYPE = "2"
HEADER_TYPE = "3"
DATA_TYPE = "D"

ALLOWED_TYPES = [REQUEST_TYPE, RESPONSE_TYPE, HEADER_TYPE, DATA_TYPE]

### Key Exchange ###

def generate_random_key(byte_len = 1000):
    entropy = []
    for i in range(byte_len):
        entropy += [randint(0,255)]

    b = bytes(entropy)
    return hash.sha3_256(b)


class KeyExchange:
    def __init__(self, config, name_o_r = None):
        self.config = config
        self.rsa_decrypt = rsa.RSA(config.rsa_n, config.rsa_pri)
        self.dhke = dh.DHKE(config.dh_p,config.dh_g)
        self.name_of_recipient = name_o_r

    def key_exchange(self, tod = None):
        # Session Key
        key = int(generate_random_key(), 16)

        if tod == None:
            tod = int(datetime.now().timestamp()) * 1000000
            sess_key = {"key": str(key), "ToD": str(tod)}
            sess_key_str = json.dumps(sess_key)
            sess_key_num = rsa.ascii_to_num(sess_key_str)
        else:
            sess_key = key
            sess_key_str = str(sess_key)
            sess_key_num = key

        rsa_nB = self.config.get_rsa_n(self.name_of_recipient)
        rsa_encrypt_b = rsa.RSA(rsa_nB, self.config.rsa_pub)

        if(sess_key_num >= rsa_nB):
            raise Exception("session key too large")

        enc_sess_key = rsa_encrypt_b.encrypt(sess_key_num)
        hash_sess_key = int(hash.sha3_256(sess_key_str.encode()), 16)

        # Agreement
        diffie_pub_key = self.dhke.X
        agree = {"hash_sess_key": str(hash_sess_key), "diffie_pub_k": str(diffie_pub_key)}
        agree_str = json.dumps(agree)

        hash_agree = int(hash.sha3_256(agree_str.encode()), 16)

        signature = self.rsa_decrypt.encrypt(hash_agree)
        payload = {"agreement_data": agree, "signature": str(signature)}
        payload_str = json.dumps(payload)

        c = cm.CounterMode(hex(key)[2:])
        enc_payload = c.encrypt(payload_str.encode(), tod)
        enc_payload_str = base64.b64encode(enc_payload).decode("utf-8")

        dhke_json = {"payload": enc_payload_str, "sess_key": str(enc_sess_key)}

        return (dhke_json, tod)

    # listener- after I decrypt it I know who it is
    def decrypt_message1(self, js):
        try:
            # Session Key
            enc_sess_key = int(js["sess_key"], 10)

            dec_sess_key = self.rsa_decrypt.encrypt(enc_sess_key)
            sess_key_str = rsa.num_to_ascii(dec_sess_key)
            sess_key = json.loads(sess_key_str)
            key = int(sess_key["key"], 10)
            tod = int(sess_key["ToD"], 10)

            hash_sess_key = hash.sha3_256(sess_key_str.encode())

            #decrypt payload

            enc_payload = base64.b64decode(js["payload"])
            c = cm.CounterMode(hex(key)[2:])
            payload = json.loads(c.decrypt(enc_payload, tod).decode("utf-8"))

            # Verify Session Key
            claimed_hash_sess_key = int(payload["agreement_data"]["hash_sess_key"], 10)

            if hash_sess_key != hash_sess_key:
                raise Exception("failed to verify session key")

            # Verify Signature
            agree_str = json.dumps(payload["agreement_data"])

            hash_agree = hash.sha3_256(agree_str.encode())
            sig = int(payload["signature"], 10)

            name = ""
            for i in self.config.get_contacts():
                rsa_n = self.config.get_rsa_n(i)
                rsa_verify = rsa.RSA(rsa_n, self.config.rsa_pub)
                if rsa_verify.encrypt(sig) == int(hash_agree, 16):
                    name = i

            if name == "":
                raise Exception("failed to verify signature")
            else:
                self.name_of_recipient = name

            return (int(payload["agreement_data"]["diffie_pub_k"], 10), tod, self.name_of_recipient)

        except:
            raise Exception("failed to decrypt or verify the session key")

    def decrypt_message2(self, js, tod):
        try:
            # Session Key
            enc_sess_key = int(js["sess_key"], 10)

            key = self.rsa_decrypt.encrypt(enc_sess_key)
            sess_key_str = str(key)

            hash_sess_key = hash.sha3_256(sess_key_str.encode())

            #Decrypt Payload
            enc_payload = base64.b64decode(js["payload"])
            c = cm.CounterMode(hex(key)[2:])
            payload = json.loads(c.decrypt(enc_payload, tod).decode("utf-8"))

            # Verify Session Key
            claimed_hash_sess_key = int(payload["agreement_data"]["hash_sess_key"], 10)

            if hash_sess_key != hash_sess_key:
                raise Exception("failed to verify session key")

            # Verify Signature
            agree_str = json.dumps(payload["agreement_data"])

            hash_agree = hash.sha3_256(agree_str.encode())
            sig = int(payload["signature"], 10)

            rsa_n = self.config.get_rsa_n(self.name_of_recipient)
            rsa_verify = rsa.RSA(rsa_n, self.config.rsa_pub)

            if rsa_verify.encrypt(sig) != int(hash_agree, 16):
                raise Exception("failed to verify signature")

            return int(payload["agreement_data"]["diffie_pub_k"], 10)

        except:
            raise Exception("failed to decrypt or verify the session key")


    def get_shared_secret(self, Y):
        ss = self.dhke.get_shared_secret(Y)
        ss = ub.num_to_bytes(ss)
        return hash.sha3_256(ss)

    def get_keys(self, ss):
        m1 = bytes([1]) + ss.encode()
        m2 = bytes([2]) + ss.encode()

        k1 = hash.sha3_256(m1)
        k2 = hash.sha3_256(m2)

        return (k1, k2)


### Functions for Sending ###

"""
Given a type (1,2,3,D-- from the protocol), and a string the function processes
it into byte array suitable for sending.

prepare_json : str, str -> byte array
"""
def prepare_json(type, payload):
    type = type.encode()
    payload = payload.encode()
    length = get_length(payload)

    return type + length + payload

"""
Given a type (1,2,3,D-- from the protocol), and a byte array the function processes
it into byte array suitable for sending.

prepare_data : str, byte array -> byte array
"""
def prepare_data(type, payload):
    type = type.encode()
    payload = payload
    length = get_length(payload)

    return type + length + payload


### Function for Receiving ###

"""
Given a byte array representing a header it processes the array into a type and length.

parse_header: byte array -> (str, int)
"""
def parse_header(byte_array):
    try:
        type = byte_array[:TYPE_BYTES].decode("utf-8")

        if not type in ALLOWED_TYPES:
            raise Exception("received invalid type")

        length = int(byte_array[TYPE_BYTES:].decode("utf-8"), base = 10)

        return (type, length)
    except Exception as e:
        raise Exception(str(e))

### Miscellaneous ###
"""
Given a byte array the function computes the length suitable for sending in the
protocol.

get_length: byte array -> byte array
"""
def get_length(data):
    length = str(len(data))
    if len(length) > LENGTH_BYTES:
        raise Exception("message exceeded " + ("9" * LENGTH_BYTES))
    length = ("0" * (LENGTH_BYTES - len(length)) + length).encode()

    return length

"""
Function to abstract the request type.

is_request_type: str -> bool
"""
def is_request_type(type):
    return type == REQUEST_TYPE

"""
Function to abstract the response type.

is_response_type: str -> bool
"""
def is_response_type(type):
    return type == RESPONSE_TYPE

"""
Function to abstract the header type.

is_header_type: str -> bool
"""
def is_header_type(type):
    return type == HEADER_TYPE

"""
Function to abstract the data type.

is_data_type: str -> bool
"""
def is_data_type(type):
    return type == DATA_TYPE
