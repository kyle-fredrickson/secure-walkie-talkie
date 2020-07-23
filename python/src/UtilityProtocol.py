"""
This handles the construction and processing of messages sent and received.
"""

import base64
from datetime import datetime
import json
from random import randint

import CounterMode as cm
import DHKE as dh
import RSA as rsa
import SHA3 as hash
import UtilityBit as ub

### MESSAGE TYPES ###

TYPE_BYTES = 1
LENGTH_BYTES = 8
HEADER_BYTES = TYPE_BYTES + LENGTH_BYTES

REQUEST_TYPE = "1"
RESPONSE_TYPE = "2"
HEADER_TYPE = "3"
DATA_TYPE = "D"

ALLOWED_TYPES = [REQUEST_TYPE, RESPONSE_TYPE, HEADER_TYPE, DATA_TYPE]

def is_request_type(type):
    return type == REQUEST_TYPE

def is_response_type(type):
    return type == RESPONSE_TYPE

def is_header_type(type):
    return type == HEADER_TYPE

def is_data_type(type):
    return type == DATA_TYPE

def get_length(data):
    length = str(len(data))
    if len(length) > LENGTH_BYTES:
        raise Exception("message exceeded " + ("9" * LENGTH_BYTES))
    length = ("0" * (LENGTH_BYTES - len(length)) + length)

    return length

### Miscellaneous ###

def generate_random_key(byte_len = 1000):
    entropy = []
    for i in range(byte_len):
        entropy += [randint(0,255)]

    b = bytes(entropy)
    return hash.sha3_256(b)

def get_shared_secret(my_diffie, their_diffie_pub):
    ss = my_diffie.get_shared_secret(their_diffie_pub)
    ss = ub.num_to_bytes(ss)
    return hash.sha3_256(ss)

def get_keys(ss):
    m1 = bytes([1]) + ss.encode()
    m2 = bytes([2]) + ss.encode()

    k1 = hash.sha3_256(m1)
    k2 = hash.sha3_256(m2)

    return (k1, k2)

### Package Messages ###

def get_request(my_diffie_pub, my_rsa_decrypt, their_rsa_encrypt):
    (request, tod) = compute_request(my_diffie_pub, my_rsa_decrypt, their_rsa_encrypt)
    request = json.dumps(request)

    length = get_length(request)

    return (REQUEST_TYPE.encode() + length.encode() + request.encode(), tod)

def get_response(my_diffie_pub, my_rsa_decrypt, their_rsa_encrypt, tod):
    response = compute_response(my_diffie_pub, my_rsa_decrypt, their_rsa_encrypt, tod)
    response = json.dumps(response)

    length = get_length(response)

    return RESPONSE_TYPE.encode() + length.encode() + response.encode()

def get_header_data(data, my_diffie, their_diffie_pub, tod):
    (header, data) = compute_header_data(data, my_diffie, their_diffie_pub, tod)

    header = json.dumps(header)

    header_length = get_length(header)
    data_length = get_length(data)

    header_message = HEADER_TYPE.encode() + header_length.encode() + header.encode()
    data_message = DATA_TYPE.encode() + data_length.encode() + data

    return (header_message, data_message)


### Process Messages ###
def process_header(byte_array):
    try:
        type = byte_array[:TYPE_BYTES].decode("utf-8")

        if not type in ALLOWED_TYPES:
            raise Exception("received invalid type")

        length = int(byte_array[TYPE_BYTES:].decode("utf-8"), base = 10)

        return (type, length)
    except Exception as e:
        raise Exception(str(e))

def process_body(byte_array):
    body = byte_array.decode("utf-8")
    return json.loads(body)

def process_request(data, my_rsa_decrypt, contacts):
    js = process_body(data)
    return decrypt_request(js, my_rsa_decrypt, contacts)

def process_response(data, my_rsa_decrypt, their_rsa_encrypt, tod):
    js = process_body(data)
    return decrypt_response(js, my_rsa_decrypt, their_rsa_encrypt, tod)

def process_tag(tag):
    tag = process_body(tag)
    return tag["tag"]

def process_data(tag, enc_data, my_diffie, their_diffie_pub, tod):
    return decrypt_data(tag, enc_data, my_diffie, their_diffie_pub, tod)

### Compute Messages ###

def compute_request(my_diffie_pub, my_rsa_decrypt, their_rsa_encrypt):
    key = int(generate_random_key(), 16)

    tod = int(datetime.now().timestamp()) * 1000000
    sess_key = {"key": str(key), "ToD": str(tod)}
    sess_key_str = json.dumps(sess_key)
    sess_key_num = rsa.ascii_to_num(sess_key_str)


    if(sess_key_num >= their_rsa_encrypt.modulus):
        raise Exception("session key too large")

    enc_sess_key = base64.b64encode(str(their_rsa_encrypt.encrypt(sess_key_num)).encode()).decode("utf-8")
    hash_sess_key = int(hash.sha3_256(sess_key_str.encode()), 16)

    agree = {"hash_sess_key": str(hash_sess_key), "diffie_pub_k": str(my_diffie_pub)}
    agree_str = json.dumps(agree)

    hash_agree = int(hash.sha3_256(agree_str.encode()), 16)

    signature = my_rsa_decrypt.encrypt(hash_agree)
    payload = {"agreement_data": agree, "signature": str(signature)}
    payload_str = json.dumps(payload)

    c = cm.CounterMode(hex(key)[2:])
    enc_payload = c.encrypt(payload_str.encode(), tod)
    enc_payload_str = base64.b64encode(enc_payload).decode("utf-8")

    dhke_json = {"payload": enc_payload_str, "sess_key": str(enc_sess_key)}

    return (dhke_json, tod)

def compute_response(my_diffie_pub, my_rsa_decrypt, their_rsa_encrypt, tod):
    key = int(generate_random_key(), 16)

    sess_key = key
    sess_key_str = str(sess_key)
    sess_key_num = rsa.ascii_to_num(sess_key_str)

    if(sess_key_num >= their_rsa_encrypt.modulus):
        raise Exception("session key too large")

    enc_sess_key = base64.b64encode(str(their_rsa_encrypt.encrypt(sess_key_num)).encode()).decode("utf-8")
    hash_sess_key = int(hash.sha3_256(sess_key_str.encode()), 16)

    # Agreement
    agree = {"hash_sess_key": str(hash_sess_key), "diffie_pub_k": str(my_diffie_pub)}
    agree_str = json.dumps(agree)

    hash_agree = int(hash.sha3_256(agree_str.encode()), 16)

    signature = my_rsa_decrypt.encrypt(hash_agree)
    payload = {"agreement_data": agree, "signature": str(signature)}
    payload_str = json.dumps(payload)

    c = cm.CounterMode(hex(key)[2:])
    enc_payload = c.encrypt(payload_str.encode(), tod)
    enc_payload_str = base64.b64encode(enc_payload).decode("utf-8")

    dhke_json = {"payload": enc_payload_str, "sess_key": str(enc_sess_key)}

    return dhke_json

def compute_header_data(data, my_diffie, their_diffie_pub, tod):
    (k1, k2) = get_keys(get_shared_secret(my_diffie, their_diffie_pub))

    c = cm.CounterMode(k1)
    encrypted_data = c.encrypt(data, tod)

    m = k2.encode() + encrypted_data
    h = hash.sha3_256(m)
    header = {"tag" : h}

    return (header, encrypted_data)

### Decrypt Messages ###

def decrypt_request(js, my_rsa_decrypt, contacts):
    enc_sess_key = int(base64.b64decode(js["sess_key"]).decode("utf-8"), 10)

    dec_sess_key = my_rsa_decrypt.encrypt(enc_sess_key)
    sess_key_str = rsa.num_to_ascii(dec_sess_key)
    sess_key = json.loads(sess_key_str)
    key = int(sess_key["key"], 10)
    tod = int(sess_key["ToD"], 10)

    hash_sess_key = hash.sha3_256(sess_key_str.encode())

    #decrypt payload

    enc_payload = base64.b64decode(js["payload"])
    c = cm.CounterMode(hex(key)[2:])
    payload = json.loads(c.decrypt(enc_payload, tod).decode("utf-8")) # there's an error here occasionally

    claimed_hash_sess_key = hex(int(payload["agreement_data"]["hash_sess_key"], 10))[2:]

    if claimed_hash_sess_key != hash_sess_key:
        raise Exception("failed to verify session key")

    # Verify Signature
    agree_str = json.dumps(payload["agreement_data"])

    hash_agree = hash.sha3_256(agree_str.encode())
    sig = int(payload["signature"], 10)

    name = None

    for contact in contacts:
        rsa_n = int(contact["rsa_n"], 10)
        rsa_pub = int(contact["rsa_pub"], 10)
        rsa_encrypt = rsa.RSA(rsa_n, rsa_pub)

        if rsa_encrypt.encrypt(sig) == int(hash_agree, 16):
            name = contact["name"]
            break

    if name is None:
        raise Exception("Message sent by someone outside your contacts.")

    return (int(payload["agreement_data"]["diffie_pub_k"], 10), tod, name)

def decrypt_response(js, my_rsa_decrypt, their_rsa_encrypt, tod):
    enc_sess_key = int(base64.b64decode(js["sess_key"]).decode("utf-8"), 10)

    dec_sess_key = my_rsa_decrypt.encrypt(enc_sess_key)

    sess_key_str = rsa.num_to_ascii(dec_sess_key)
    key = int(sess_key_str, 10)

    hash_sess_key = hash.sha3_256(sess_key_str.encode())

    #decrypt payload

    enc_payload = base64.b64decode(js["payload"])
    c = cm.CounterMode(hex(key)[2:])
    payload = json.loads(c.decrypt(enc_payload, tod).decode("utf-8")) # this causes an error occasionally

    claimed_hash_sess_key = hex(int(payload["agreement_data"]["hash_sess_key"], 10))[2:]

    if claimed_hash_sess_key != hash_sess_key:
        raise Exception("failed to verify session key")

    # Verify Signature
    agree_str = json.dumps(payload["agreement_data"])

    hash_agree = hash.sha3_256(agree_str.encode())
    sig = int(payload["signature"], 10)

    if their_rsa_encrypt.encrypt(sig) != int(hash_agree, 16):
        raise Exception("Failed to verify signature.")

    return int(payload["agreement_data"]["diffie_pub_k"], 10)

def validate_data(tag, enc_data, k):
    m = k.encode() + enc_data
    h = hash.sha3_256(m)

    return tag == h

def decrypt_data(tag, enc_data, my_diffie, their_diffie_pub, tod):
    (k1, k2) = get_keys(get_shared_secret(my_diffie, their_diffie_pub))

    if(validate_data(tag, enc_data, k2)):
        c = cm.CounterMode(k1)
        data = c.decrypt(enc_data, tod)

        return data
    else:
        return None
