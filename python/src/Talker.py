import json
import socket
import time

import CounterMode as cm
import DHKE as dh
import RSA as rsa
import SHA3 as hash
import UtilityConfig as uc
import UtilityProtocol as up

class Talker:
    def __init__(self, config):
        self.config = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def talk(self, data, name):
        contact = self.config.get_contact(name)
        ip = contact["ip"]
        port = contact["port"]

        self.sock.connect((ip,port))
        ke = up.KeyExchange(self.config, name)

        tod = self.send_request(ke)
        dh_key = self.get_response(ke, tod)

        shared_secret = ke.get_shared_secret(dh_key)
        (k1, k2) = ke.get_keys(shared_secret)

        c = cm.CounterMode(k1)
        encrypted_data = c.encrypt(data, tod)

        self.send_header(encrypted_data, k2)
        self.send_data(encrypted_data)

        self.sock.close()

    ### Request ###

    def send_request(self, ke):
        (request, tod) = self.request(ke)
        self.sock.send(request)
        print("Sent Request:", request, end = "\n\n")
        return tod

    def request(self, ke):
        (request_dict, tod) = ke.key_exchange()
        request = up.prepare_json(up.REQUEST_TYPE, json.dumps(request_dict))
        return (request, tod)

    ### Request ###

    def get_response(self, ke, tod):
        (type, length) = up.parse_header(self.sock.recv(up.HEADER_BYTES)) # will need to parse
        if not up.is_response_type(type):
            raise Exception("unexpected response type")

        raw_data = self.sock.recv(length)

        print("Received:", length, "bytes\n")

        raw_json = json.loads(raw_data.decode())
        dh_pub_key = ke.decrypt_message2(raw_json, tod)

        return dh_pub_key

    ### Header ###

    def send_header(self, raw, k):
        header = self.header(raw, k)
        self.sock.send(header)
        print("Sent header:", header, end = "\n\n")

    def header(self, raw, k):
        m = k.encode() + raw
        h = hash.sha3_256(m)
        header_dict = {"tag" : h}
        print("tag:", json.dumps(header_dict))
        header = up.prepare_json(up.HEADER_TYPE, json.dumps(header_dict))
        return header

    ### Data ###

    def send_data(self, raw):
        data = self.data(raw)
        print("data:", data)
        self.sock.send(data)
        print("Sent:", len(data), "bytes", end = "\n\n")

    def data(self, raw):
        data = up.prepare_data(up.DATA_TYPE, raw)
        return data
