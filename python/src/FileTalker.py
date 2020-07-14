import json
import socket

import DHKE as d
import RSA as rsa
import UtilityConfig as uc
import UtilityFile as uf
import UtilityProtocol as up

class FileTalker:
    def __init__(self, config, recipient, infile, outfile, vars):
        self.config = config
        self.my_rsa_decrypt = rsa.RSA(config.rsa_n, config.rsa_pri)
        self.my_diffie = None

        their_rsa_n = config.get_rsa_n(recipient)
        their_rsa_pub = config.get_rsa_pub(recipient)
        self.their_rsa_encrypt = rsa.RSA(their_rsa_n, their_rsa_pub)

        self.infile = infile
        self.outfile = outfile
        self.varsfile = vars
        self.vars = uc._read_json(vars)

        try:
            p = self.vars["my_diffie_pri"]
            my_diffie_pri_exists = True
        except:
            my_diffie_pri_exists = False

        if not my_diffie_pri_exists:
            self.my_diffie = d.DHKE(config.dh_p, config.dh_g)
            self.vars["my_diffie_pri"] = self.my_diffie.x
        else:
            self.my_diffie = d.DHKE(config.dh_p, config.dh_g, self.vars["my_diffie_pri"])

    def talk(self, data, message_type):
        if up.is_request_type(message_type):
            tod = self.send_request()
            self.vars["tod"] = tod

        elif up.is_response_type(message_type):
            tod = self.vars["tod"]
            their_diffie_pub = self.receive_response(tod)
            self.vars["their_diffie_pub"] = their_diffie_pub

        elif up.is_header_type(message_type):
            tod = self.vars["tod"]
            their_diffie_pub = self.vars["their_diffie_pub"]
            self.send_header_data(data, their_diffie_pub, tod)

        uf.write_json(self.varsfile, self.vars)

    def send_request(self):
        (request, tod) = up.get_request(self.my_diffie.X, self.my_rsa_decrypt, self.their_rsa_encrypt)
        uf.send_message(self.outfile, request)

        return tod

    def receive_response(self, tod):
        (header, data) = uf.receive_message(self.infile)
        (type, length) = up.process_header(header)

        if not up.is_response_type(type):
            raise Exception("unexpected response type")

        their_diffie_pub = up.process_response(data, self.my_rsa_decrypt, self.their_rsa_encrypt, tod)
        return their_diffie_pub

    def send_header_data(self, data, their_diffie_pub, tod):
        (header, enc_data) = up.get_header_data(data, self.my_diffie, their_diffie_pub, tod)
        uf.send_message(self.outfile, header + enc_data)

