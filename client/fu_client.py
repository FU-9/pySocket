#!_*_coding:utf-8_*_
import optparse
import socket
import json
import os

class FTPClient:
    """Ftp Client"""

    MSG_SIZE = 1024

    def __init__(self):
        self.username = None
        self.terminal_display = None
        parser = optparse.OptionParser()
        parser.add_option("-s","--server",dest="server",help="ftp server ip_addr")
        parser.add_option("-P","--port",type="int",dest="port",help="ftp server port")
        parser.add_option("-u","--username",dest="username",help="username info")
        parser.add_option("-p","--password",dest="password",help="password info")
        self.option,self.args = parser.parse_args()

        self.argv_verification()

        self.make_connection()

    def argv_verification(self):
        """检测参数合法性"""
        if not self.option.server or not self.option.port:
            exit("Error: must supply server and port parameters")

    def make_connection(self):
        """建立socket链接"""
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((self.option.server,self.option.port))

    def get_response(self):
        data = self.sock.recv(self.MSG_SIZE)
        return json.loads(data.decode('utf-8'))

    def auth(self):
        """用户认证"""
        count = 0
        while count < 3 :
            username = input("username>>>:").strip()
            if not username:continue
            password = input("password>>>:").strip()
            self.send_msg('auth',username=username,password=password)
            response = self.get_response()
            if response.get('status_code') == 200:
                self.username = username
                self.terminal_display = "[%s]>>>:"%self.username
                return True
            else:
                print(response.get("status_msg"))
            count += 1

    def interactive(self):
        """处理与Ftpserver的交互"""
        if self.auth():
            while True:
                user_input = input(self.terminal_display).strip()
                if not user_input:continue

                cmd_list = user_input.split()
                if hasattr(self,"_%s"%cmd_list[0]):
                    func = getattr(self,"_%s"%cmd_list[0])
                    func(cmd_list[1:])

    def parameter_check(self,args,min_args=None,max_args=None,exact_args=None):
        if min_args:
            if len(args) < min_args:
                print("must provide at least %s parameters but %s received"%(min_args,len(args)))
                return False
        if max_args:
            if len(args) > max_args:
                print("need at most %s paramenters but %s received."%(max_args,len(args)))
                return False
        if exact_args:
            if len(args) != exact_args:
                print("need at most %s paramenters but %s received." % (exact_args, len(args)))
                return False
        return True

    def send_msg(self,action_type,**kwargs):
        """打包消息并发送到远程"""
        msg_data = {
            "action_type":action_type,
            "fill":""
        }
        msg_data.update(kwargs)
        bytes_msg = json.dumps(msg_data).encode('utf-8')
        if self.MSG_SIZE > len(bytes_msg):
            msg_data['fill'] = msg_data['fill'].zfill(self.MSG_SIZE - len(bytes_msg))
        self.sock.send(bytes_msg)

    def _ls(self, cmd_args):
        self.send_msg(action_type='ls')
        response = self.get_response()
        if response.get('status_code') == 302:
            cmd_result_size = response.get('cmd_result_size')
            received_size = 0
            cmd_result = b""
            while received_size < cmd_result_size:
                if cmd_result_size - received_size < 8192:
                    data = self.sock.recv(cmd_result_size - received_size)
                else:
                    data = self.sock.recv(8192)
                cmd_result += data
                received_size += len(data)
            else:
                print(cmd_result.decode('utf-8'))#mac

    def _cd(self,cmd_args):
        if self.parameter_check(cmd_args, exact_args=1):
            target_dir = cmd_args[0]
            self.send_msg('cd',target_dir=target_dir)
            response = self.get_response()
            if response.get('status_code') == 350:
                self.terminal_display = "[/%s]"%response.get('current_dir')

    def _get(self,cmd_args):
        """download file from ftp server"""
        if self.parameter_check(cmd_args,min_args=1):
            filename = cmd_args[0]
            self.send_msg(action_type='get',filename=filename)

            response = self.get_response()
            if response.get('status_code') == 301:
                file_size = response.get('file_size')
                received_size = 0
                with open(filename,'wb') as f:
                    while received_size < file_size:
                        if file_size - received_size < 8192:
                            data = self.sock.recv(file_size - received_size)
                        else:
                            data = self.sock.recv(8192)
                        received_size += len(data)
                        f.write(data)
                    else:
                        print("---file [%s] rece done, received size [%s]---"%(filename,file_size))
                        f.close()
            else:
                print(response.get('status_msg'))

    def _put(self,cmd_args):
        if self.parameter_check(cmd_args, min_args=1):
            local_file = cmd_args[0]
            if os.path.isfile(local_file):
                total_size = os.path.getsize(local_file)
                self.send_msg('put',file_size=total_size,filename=local_file)
                f = open(local_file,'rb')
                uploaded_size = 0
                last_percent = 0
                for line in f:
                    self.sock.send(line)
                    uploaded_size += len(line)
                    current_percent = int(uploaded_size / total_size * 100)
                    if current_percent > last_percent:
                        print('#'*int(current_percent/2) + "{percent}".format(percent=current_percent),end="\r")
                        last_percent = current_percent
                else:
                    print('\n')
                    print('file upload done'.center(50,'-'))
                    f.close()


if __name__ == "__main__":
    client = FTPClient()
    client.interactive()