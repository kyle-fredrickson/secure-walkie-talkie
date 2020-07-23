import socket
import socks
import struct

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "localhost", 9050, True)
s = socks.socksocket()
s.connect(("localhost", 9050))
s.send(b'hello socks')
print("connected")
print("receiving...", s.recv(11))