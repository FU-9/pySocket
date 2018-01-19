#!_*_coding:utf-8_*_
import optparse
import socket
import json

class FTPClient:
    """Ftp Client"""

    MSG_SIZE = 1024

    def __init__(self):
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

            cmd = {
                'action_type':'auth',
                'username':username,
                'password':password
            }

            self.sock.send(json.dumps(cmd).encode("utf-8"))
            response = self.get_response()
            print(response)
            if response.get('status_code') == 200:
                return True
            else:
                print(response.get("status_msg"))
            count += 1


    def interactive(self):
        """处理与Ftpserver的交互"""
        if self.auth():
            pass

if __name__ == "__main__":
    client = FTPClient()
    client.interactive()