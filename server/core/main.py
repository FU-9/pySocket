#!_*_coding:utf-8_*_
import socket
from conf import settings

class FTPServer:
    """处理与客户端所有的交互的socket server"""

    def __init__(self,management_instance):
        self.management_instance = management_instance
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((settings.HOST,settings.PORT))
        self.sock.listen(settings.MAX_SOCKET_LISTEN)

    def run_forever(self):
        """启动"""
        print("starting server on %s:%s"%(settings.HOST,settings.PORT))
        self.request,self.addr = self.sock.accept()
        print("got a new connection from %s"%(self.addr))
        self.handle()

    def handle(self):
        data = self.request.recv(1024)
        print(data)