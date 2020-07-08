#!/usr/bin/env python3

import json
import socket

import DHKE as d
import RSA as rsa
import UtilityProtocol as up

class TcpTalker:
    def __init__(self, config, name):
        self.config = config
        self.my_rsa_decrypt = rsa.RSA(config.rsa_n, config.rsa_pri)
        self.my_diffie = d.DHKE(config.dh_p, config.dh_g)

        their_rsa_n = config.get_rsa_n(name)
        their_rsa_pub = config.get_rsa_pub(name)
        self.their_rsa_encrypt = rsa.RSA(their_rsa_n, their_rsa_pub)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.their_ip_port = config.get_ip_port(name)

    def talk(self, data):
        self.sock.connect(self.their_ip_port)

        tod = self.send_request()
        their_diffie_pub = self.receive_response(tod)
        self.send_header_data(data, their_diffie_pub, tod)

    def send_request(self):
        (request, tod) = up.get_request(self.my_diffie.X, self.my_rsa_decrypt, self.their_rsa_encrypt)
        self.sock.send(request)

        return tod

    def receive_response(self, tod):
        header = self.sock.recv(up.HEADER_BYTES)
        (type, length) = up.process_header(header)

        if not up.is_response_type(type):
            raise Exception("unexpected response type")

        data = self.sock.recv(length)
        their_diffie_pub = up.process_response(data, self.my_rsa_decrypt, self.their_rsa_encrypt, tod)

        return their_diffie_pub

    def send_header_data(self, data, their_diffie_pub, tod):
        (header, enc_data) = up.get_header_data(data, self.my_diffie, their_diffie_pub, tod)

        self.sock.send(header)
        self.sock.send(enc_data)

### delete below here
import UtilityConfig as uc

def main():
    b = TcpTalker(uc.UtilityConfig("../config/Alice.json"), "Bob")
    b.talk(b"hello")

if __name__ == "__main__":
    main()
