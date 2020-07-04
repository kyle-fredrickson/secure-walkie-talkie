import json
import socket
import time

import CounterMode as cm
import DHKE as dh
import RSA as rsa
import SHA3 as hash
import UtilityConfig as uc
import UtilityProtocol as up

class Listener:
    def __init__(self, config):
        self.config = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.config.ip, self.config.port))

    def listen(self):
        self.sock.listen(1)
        conn, addr = self.sock.accept()

        ke = up.KeyExchange(self.config)

        # Request
        (dh_key, tod, name) = self.get_request(conn, ke)
        print("Received request from", name + ".\n")

        # Response
        self.send_response(conn, ke, tod)

        shared_secret = ke.get_shared_secret(dh_key)
        (k1, k2) = ke.get_keys(shared_secret)

        # Header
        tag = json.loads(self.get_header(conn).decode("utf-8"))["tag"]
        # Validate header

        # Data
        enc_data = self.get_data(conn)

        if self.validate_data(tag, enc_data, k2):
            print("Data validated.\n")
            print("Decrypting...\n")
            c = cm.CounterMode(k1)
            data = c.decrypt(enc_data, tod)

            conn.close()
            return data
        else:
            conn.close()
            raise Exception("failed to validate header")

    ### Request ###

    # returns dh public key
    def get_request(self, conn, ke):
        (type, length) = up.parse_header(conn.recv(up.HEADER_BYTES))
        if not up.is_request_type(type):
            raise Exception("unexpected response type")

        raw_data = conn.recv(length)

        print("Received Request:", length, "bytes\n")

        raw_json = json.loads(raw_data.decode())
        (dh_pub_key, tod, name) = ke.decrypt_message1(raw_json)

        return (dh_pub_key, tod, name)

    ### Response ###

    def send_response(self, conn, ke, tod):
        response = self.response(ke, tod)
        conn.send(response)

        print("Sent Response:", response, "\n")

    def response(self, ke, tod):
        (response_dict, tod) = ke.key_exchange(tod)
        response = up.prepare_json(up.RESPONSE_TYPE, json.dumps(response_dict))
        return response

    ### Header ###

    def get_header(self, conn):
        (type, length) = up.parse_header(conn.recv(up.HEADER_BYTES))
        if not up.is_header_type(type):
            raise Exception("unexpected response type")

        header = conn.recv(length)

        print("Received Header:", length, "bytes\n")

        return header

    ### Data ###

    def get_data(self, conn):
        (type, length) = up.parse_header(conn.recv(up.HEADER_BYTES))
        if not up.is_data_type(type):
            raise Exception("unexpected response type")

        data = b""
        while len(data) < length:
            new_data = conn.recv(length)
            data = data + new_data

        print("Received Data:", len(data), "of", length, "bytes\n")

        return data

    ### Validate Header ###

    def validate_data(self, tag, enc_data, k):
        m = k.encode() + enc_data
        h = hash.sha3_256(m)

        return tag == h
