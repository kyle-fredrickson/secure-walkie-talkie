from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
import struct
import socket
import select

SOCKS_VERSION = 5

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    pass

class SocksProxy(StreamRequestHandler):
    def handle(self):
        header = self.connection.recv(2)
        version, num_methods = struct.unpack("!BB", header)

        methods = self.get_available_methods(num_methods)

        self.connection.sendall(struct.pack("!BB", SOCKS_VERSION, 0))

        version, cmd, _, address_type = struct.unpack("!BBBB", self.connection.recv(4))

        if address_type == 1:  # IPv4
            address = socket.inet_ntoa(self.connection.recv(4))
        elif address_type == 3:  # Domain name
            domain_length = self.connection.recv(1)[0]
            address = socket.gethostbyname(self.connection.recv(domain_length))
        port = struct.unpack('!H', self.connection.recv(2))[0]

        try:
            if cmd == 1:  # CONNECT
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((address, port))
                bind_address = remote.getsockname()
                print('Connected to %s %s' % (address, port))
            else:
                self.server.close_request(self.request)

            addr = struct.unpack("!I", socket.inet_aton(bind_address[0]))[0]
            port = bind_address[1]
            reply = struct.pack("!BBBBIH", SOCKS_VERSION, 0, 0, 1, addr, port)
            print(addr, port)
        except Exception as err:
            print(err)
            reply = self.generate_failed_reply(address_type, 5)

        self.connection.sendall(reply)

        # establish data exchange
        if reply[1] == 0 and cmd == 1:
            self.exchange_loop(self.connection, remote)

        self.server.close_request(self.request)

        return (self.connection, remote)

    def get_available_methods(self, n):
        methods = []
        for i in range(n):
            methods.append(ord(self.connection.recv(1)))
        return methods

    def generate_failed_reply(self, address_type, error_number):
        return struct.pack("!BBBBIH", SOCKS_VERSION, error_number, 0, address_type, 0, 0)

    def exchange_loop(self, client, remote):
        while True:
            r, w, e = select.select([client, remote], [], [])

            if client in r:
                data = client.recv(4096)
                if remote.send(data) <= 0:
                    return

            if remote in r:
                data = remote.recv(4096)
                if client.send(data) <= 0:
                    return

if __name__ == '__main__':
    with ThreadingTCPServer(('127.0.0.1', 9050), SocksProxy) as server:
        server.serve_forever()
