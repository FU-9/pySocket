#!_*_coding:utf-8_*_
import socket
import json
import os
import configparser
import hashlib
import subprocess
import time
from conf import settings


class FTPServer:
    """处理与客户端所有的交互的socket server"""

    STATUS_CODE = {
        200: "Passed authentication!",
        201: "Wrong username or password!",
        300: "File does not exist!",
        301: "File exist, and this msg include the file size!",
        302: "This msg include the msg size!",
        350: "Dir changed ",
        351: "Dir doesnt exist",
        360: "mkdir success",
        361: "directory already exists"
    }

    MSG_SIZE = 1024 #消息最长1024

    def __init__(self,management_instance):
        self.management_instance = management_instance
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((settings.HOST,settings.PORT))
        self.sock.listen(settings.MAX_SOCKET_LISTEN)
        self.accounts = self.load_accounts()
        self.user_obj = None
        self.user_current_dir = ""

    def run_forever(self):
        """启动"""
        print("starting server on %s:%s"%(settings.HOST,settings.PORT))
        while True:
            self.request, self.addr = self.sock.accept()
            print("got a new connection from %s:%s" % (self.addr))
            try:
                self.handle()
            except Exception as e:
                print('Error happend with client ,close connection',e)
                self.request.close()

    def handle(self):
        while True:
            raw_data = self.request.recv(self.MSG_SIZE)

            if not raw_data:
                print("connection %s:%s is lost .." %self.addr)
                del self.request,self.addr
                break

            data = json.loads(raw_data.decode('utf-8'))
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
                self.user_obj = self.accounts[username]
                self.user_obj['home'] = os.path.join(settings.USER_HOME_DIR,username)
                self.user_current_dir = self.user_obj['home']
                return True
            else:
                return False
        else:
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

    def _get(self,data):
        """client download file through this method"""
        filename = data.get('filename')
        full_path = os.path.join(self.user_current_dir,filename)
        print(full_path)
        if os.path.isfile(full_path):
            filesize = os.stat(full_path).st_size
            self.send_response(301,file_size=filesize)
            f = open(full_path,'rb')
            for line in f:
                self.request.send(line)
            else:
                print('file end done ..',full_path)
            f.close()
        else:
            self.send_response(300)

    def _ls(self,data):
        """run dir command and send result to client"""
        if os.name == 'nt':
            cmd_obj = subprocess.Popen('dir %s' % self.user_current_dir, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        elif os.name == 'posix':
            cmd_obj = subprocess.Popen('ls %s'%self.user_current_dir,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout = cmd_obj.stdout.read()
        stderr = cmd_obj.stderr.read()

        cmd_result = stdout + stderr
        if not cmd_result:
            cmd_result = b"current dir has no file at all."

        self.send_response(302,cmd_result_size=len(cmd_result))
        self.request.sendall(cmd_result)

    def _cd(self,data):
        target_dir = data.get('target_dir')
        full_path = os.path.abspath(os.path.join(self.user_current_dir,target_dir))
        if os.path.isdir(full_path):
            if full_path.startswith(self.user_obj['home']):
                self.user_current_dir = full_path
                relative_current_dir = self.user_current_dir.replace(self.user_obj['home'], "")
                self.send_response(350, current_dir=relative_current_dir)
            else:
                self.send_response(351)
        else:
            self.send_response(351)

    def _put(self,data):
        local_file = data.get('filename')
        full_path = os.path.join(self.user_current_dir,local_file)
        f = open(full_path,"wb")
        total_size = data.get('file_size')
        received_size = 0
        while received_size < total_size:
            if total_size - received_size < 8192:
                data = self.request.recv(total_size - received_size)
            else:
                data = self.request.recv(8192)
            received_size += len(data)
            f.write(data)
        else:
            f.close()

    def _mkdir(self,data):
        dir_name = data.get("dir_name")
        full_path = os.path.join(self.user_current_dir,dir_name)
        cmd_obj = subprocess.Popen('mkdir %s' % full_path, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout = cmd_obj.stdout.read()
        stderr = cmd_obj.stderr.read()
        cmd_result = stdout + stderr
        if not cmd_result:
            self.send_response(360)
        else:
            self.send_response(361,mkdir_msg="mkdir: %s: File exists"%dir_name)

    def _rm(self,data):
        rm_cmd = data.get("rm_cmd")
        full_path = os.path.abspath(os.path.join(self.user_current_dir, rm_cmd))
        cmd_obj = subprocess.Popen('rm -rf %s' % full_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = cmd_obj.stdout.read()
        stderr = cmd_obj.stderr.read()
        cmd_result = stdout + stderr
        if not cmd_result:
            self.send_response(350)
        else:
            self.send_response(351)


