#!_*_coding:utf-8_*_

class ManagementTool:
    """对用户的输入指令进行解析并调用相应的模块处理"""
    def __init__(self,sys_argv):
        self.sys_argv = sys_argv

    def verify_argv(self):
        """验证指令"""
        pass

    def execute(self):
        """解析执行命令"""
        pass
