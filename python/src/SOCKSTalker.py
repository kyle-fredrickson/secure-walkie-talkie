import json
import socket
import socks

import DHKE as d
import RSA as rsa
import UtilityProtocol as up

class SOCKSTalker:
    def __init__(self, config, name, proxy_ip, proxy_port):
        self.config = config
        self.my_rsa_decrypt = rsa.RSA(config.rsa_n, config.rsa_pri)
        self.my_diffie = d.DHKE(config.dh_p, config.dh_g)

        their_rsa_n = config.get_rsa_n(name)
        their_rsa_pub = config.get_rsa_pub(name)
        self.their_rsa_encrypt = rsa.RSA(their_rsa_n, their_rsa_pub)

        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_ip, proxy_port, True)
        self.socks = socks.socksocket()

        self.their_ip_port = config.get_ip_port(name)

    def talk(self, data):
        self.socks.connect((self.their_ip_port))

        tod = self.send_request()
        their_diffie_pub = self.receive_response(tod)
        self.send_header_data(data, their_diffie_pub, tod)

    def send_request(self):
        (request, tod) = up.get_request(self.my_diffie.X, self.my_rsa_decrypt, self.their_rsa_encrypt)
        self.socks.send(request)

        return tod

    def receive_response(self, tod):
        header = self.socks.recv(up.HEADER_BYTES)
        (type, length) = up.process_header(header)

        if not up.is_response_type(type):
            raise Exception("unexpected response type")

        data = self.socks.recv(length)
        while len(data) < length:
            data = data + self.socks.recv(length)

        their_diffie_pub = up.process_response(data, self.my_rsa_decrypt, self.their_rsa_encrypt, tod)

        return their_diffie_pub

    def send_header_data(self, data, their_diffie_pub, tod):
        (header, enc_data) = up.get_header_data(data, self.my_diffie, their_diffie_pub, tod)

        self.socks.send(header)
        self.socks.send(enc_data)