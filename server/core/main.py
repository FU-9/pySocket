#!_*_coding:utf-8_*_
import socket
import json
import configparser
import hashlib
from conf import settings


class FTPServer:
    """处理与客户端所有的交互的socket server"""

    def __init__(self,management_instance):
        self.management_instance = management_instance
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((settings.HOST,settings.PORT))
        self.sock.listen(settings.MAX_SOCKET_LISTEN)
        self.accounts = self.load_accounts()

    def run_forever(self):
        """启动"""
        print("starting server on %s:%s"%(settings.HOST,settings.PORT))
        self.request,self.addr = self.sock.accept()
        print("got a new connection from %s:%s" %(self.addr))
        self.handle()

    def handle(self):
        while True:
            raw_data = self.request.recv(1024)
            data = json.loads(raw_data)
            action_type = data.get('action_type')

            if action_type:
                if hasattr(self,"_%s"%action_type):
                    func = getattr(self,"_%s" % action_type)
                    func(data)
            else:
                print("invalid command")

    def load_accounts(self):
        """加载所有账户信息"""
        config_obj = configparser.ConfigParser()
        config_obj.read(settings.ACCOUNT_FILE)

        return config_obj.sections()

    def authenticate(self,username,password):
        """用户认证方法"""
        if username in self.accounts:
            _password = self.accounts[username]['password']
            md5
    def _auth(self,data):
        """处理用户认证请求"""
        pass
