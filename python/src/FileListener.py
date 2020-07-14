import json
import socket

import DHKE as d
import RSA as rsa
import UtilityConfig as uc
import UtilityFile as uf
import UtilityProtocol as up

class FileListener:
    def __init__(self, config, infile, outfile, vars):
        self.config = config
        self.my_rsa_decrypt = rsa.RSA(config.rsa_n, config.rsa_pri)
        self.my_diffie = None

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


    def listen(self, message_type):
        message = ""
        if up.is_request_type(message_type):
            (their_diffie_pub, tod) = self.receive_request()
            self.vars["their_diffie_pub"] = their_diffie_pub
            self.vars["tod"] = tod
        elif up.is_response_type(message_type):
            tod = self.vars["tod"]

            their_rsa_n = self.vars["their_rsa_n"]
            their_rsa_pub = self.vars["their_rsa_pub"]
            their_rsa_encrypt = rsa.RSA(their_rsa_n, their_rsa_pub)

            self.send_response(tod, their_rsa_encrypt)
        elif up.is_header_type(message_type):

            (tag, data) = self.receive_header()

            tod = self.vars["tod"]
            their_diffie_pub = self.vars["their_diffie_pub"]
            message = self.receive_data(data, tag, their_diffie_pub, tod)
            message = message.decode("utf-8")

        uf.write_json(self.varsfile, self.vars)
        return message

    def receive_request(self):
        (header, data) = uf.receive_message(self.infile)
        (type, length) = up.process_header(header)

        if not up.is_request_type(type):
            raise Exception("unexpected response type")

        (their_diffie_pub, tod, name) = up.process_request(data, self.my_rsa_decrypt, self.config.contacts)
        self.set_name(name)

        return (their_diffie_pub, tod)

    def send_response(self, tod, their_rsa_encrypt):
        response = up.get_response(self.my_diffie.X, self.my_rsa_decrypt, their_rsa_encrypt, tod)
        uf.send_message(self.outfile, response)

    def receive_header(self):
        (first_header, rest) = uf.receive_message(self.infile)
        (first_type, first_length) = up.process_header(first_header)

        if not up.is_header_type(first_type):
            raise Exception("unexpected response type")

        tag = up.process_tag(rest[:first_length])
        data = rest[first_length:]

        return (tag, data)

    def receive_data(self, data, tag, their_diffie_pub, tod):
        (header, data) = uf.receive_message(data)
        (type, length) = up.process_header(header)

        if not up.is_data_type(type):
            raise Exception("unexpected response type")

        message = up.process_data(tag, data, self.my_diffie, their_diffie_pub, tod)
        return message

    def set_name(self, name): # no good
        self.vars["their_name"] = name

        rsa_n = self.config.get_rsa_n(name)
        rsa_pub = self.config.get_rsa_pub(name)
        self.vars["their_rsa_n"] = rsa_n
        self.vars["their_rsa_pub"] = rsa_pub
