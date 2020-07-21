import socket
import socks
import struct

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "localhost", 9050, True)
s = socks.socksocket()
s.connect(("localhost", 9050))
s.send(b'100000000')
print("connected")
print("receiving...", s.recv(9))