# pySocket
##### 1、用户加密认证
##### 2、每个用户有自己的家目录，且只能访问自己的家目录
##### 3、允许用户在ftp server上随意切换目录
##### 4、允许用户查看当前目录下的文件
##### 5、允许上传和下载文件，并保证文件的一致性
##### 6、文件传输过程中显示进度条

>server端执行 python3 fu_server.py start

>client端执行 python3 fu_client.py -s localhost -P port


>ftp功能命令
```
    1、ls                        列出当前文件夹下的所有文件
    2、cd dir_name               切换目录
    3、mkdir dir_name            新建目录
    4、rm dir_name/file_name     删除目录或文件 深度删除
    5、get file                  下载文件
    6、put file                  上传文件
```

#在作业讲解的视频的进度一步步的做完，基础代码和视频中没有过多的差别，增加了 创建文件夹、删除文件夹、删除文件 放弃了 断点续传

没有新增用户功能
测试账号
username:race
password:alex