#!_*_coding:utf-8_*_
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

if __name__ == "__main__":
    from core import management
    
    argv_parser = management.ManagementTool(sys.argv)
    argv_parser.execute()
