#!_*_coding:utf-8_*_
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = "localhost"
PORT = 8086
USER_HOME_DIR = os.path.join(BASE_DIR,'home')
ACCOUNT_FILE = "%s/conf/accounts.ini"%BASE_DIR
MAX_SOCKET_LISTEN = 5