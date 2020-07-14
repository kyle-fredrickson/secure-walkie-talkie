import json
import socket

import DHKE as d
import RSA as rsa
import UtilityProtocol as up

class TcpListener:
    def __init__(self, config):
        self.config = config
        self.my_rsa_decrypt = rsa.RSA(config.rsa_n, config.rsa_pri)
        self.my_diffie = d.DHKE(config.dh_p, config.dh_g)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(config.ip_port)

        self.their_name = None
        self.their_rsa_encrypt = None

    def listen(self):
        self.sock.listen(1)
        (conn, addr) = self.sock.accept()

        (their_diffie_pub, tod) = self.receive_request(conn)
        self.send_response(conn, tod)
        tag = self.receive_header(conn)
        data = self.receive_data(conn, tag, their_diffie_pub, tod)

        conn.close()
        return data

    def receive_request(self, conn):
        header = conn.recv(up.HEADER_BYTES)
        (type, length) = up.process_header(header)

        if not up.is_request_type(type):
            raise Exception("unexpected response type")

        data = conn.recv(length)
        (their_diffie_pub, tod, name) = up.process_request(data, self.my_rsa_decrypt, self.config.contacts)
        self.set_name(name)

        return (their_diffie_pub, tod)

    def send_response(self, conn, tod):
        response = up.get_response(self.my_diffie.X, self.my_rsa_decrypt, self.their_rsa_encrypt, tod)
        conn.send(response)

    def receive_header(self, conn):
        header = conn.recv(up.HEADER_BYTES)
        (type, length) = up.process_header(header)

        if not up.is_header_type(type):
            raise Exception("unexpected response type")

        data = conn.recv(length)
        tag = up.process_tag(data)

        return tag

    def receive_data(self, conn, tag, their_diffie_pub, tod):
        header = conn.recv(up.HEADER_BYTES)
        (type, length) = up.process_header(header)

        if not up.is_data_type(type):
            raise Exception("unexpected response type")

        data = conn.recv(length)
        while len(data) < length:
            data = data + conn.recv(length)

        message = up.process_data(tag, data, self.my_diffie, their_diffie_pub, tod)
        return message

    def set_name(self, name):
        self.their_name = name

        rsa_n = self.config.get_rsa_n(name)
        rsa_pub = self.config.get_rsa_pub(name)
        self.their_rsa_encrypt = rsa.RSA(rsa_n, rsa_pub)