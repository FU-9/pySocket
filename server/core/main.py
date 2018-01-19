#!_*_coding:utf-8_*_
import socket
import json
import configparser
import hashlib
from conf import settings


class FTPServer:
    """处理与客户端所有的交互的socket server"""

    STATUS_CODE = {
        200: "Passed authentication!",
        201: "Wrong username or password!",
        300: "File does not exist!"
    }

    MSG_SIZE = 1024 #消息最长1024

    def __init__(self,management_instance):
        self.management_instance = management_instance
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((settings.HOST,settings.PORT))
        self.sock.listen(settings.MAX_SOCKET_LISTEN)
        self.accounts = self.load_accounts()

    def run_forever(self):
        """启动"""
        print("starting server on %s:%s"%(settings.HOST,settings.PORT))
        while True:
            self.request, self.addr = self.sock.accept()
            print("got a new connection from %s:%s" % (self.addr))
            self.handle()

    def handle(self):
        while True:
            raw_data = self.request.recv(1024)

            if not raw_data:
                print("connection %s:%s is lost .." %self.addr)
                del self.request,self.addr
                break

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

        return config_obj

    def authenticate(self,username,password):
        """用户认证方法"""
        if username in self.accounts:
            _password = self.accounts[username]['password']
            md5_obj = hashlib.md5()
            md5_obj.update(password.encode('utf-8'))
            md5_pwd = md5_obj.hexdigest()
            if md5_pwd == _password:
                print("passed authentication")
                return True
            else:
                print("wrong username or password")
                return False
        else:
            print("user does not exist")
            return False

    def send_response(self,status_code,*args,**kwargs):

        data = kwargs
        data['status_code'] = status_code
        data['status_msg'] = self.STATUS_CODE[status_code]
        data['fill'] = ''
        bytes_data = json.dumps(data).encode('utf-8')

        if len(bytes_data) < self.MSG_SIZE:
            data['fill'] = data['fill'].zfill(self.MSG_SIZE - len(bytes_data))
            bytes_data = json.dumps(data).encode('utf-8')
        self.request.send(bytes_data)

    def _auth(self,data):
        """处理用户认证请求"""
        if self.authenticate(data.get('username'),data.get('password')):
            print('pass auth...')
            self.send_response(status_code=200)
        else:
            self.send_response(status_code=201)
