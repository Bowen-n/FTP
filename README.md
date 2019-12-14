# FTP
用Python实现的FTP，包含客户端和服务器端，客户端在windows10系统运行，服务器端在linux系统运行。

## Code structure
```
|-- GUI
|------ ClientGui.py       客户端界面设计
|------ LoginGui.py        登录界面设计
|-- icons                  客户端界面图标
|-- dialog.py              客户端登录、下载、上传等会话的实现
|-- utils.py               获取文件信息(名称、大小、修改时间)
|-- client.py              FTP客户端实现
|-- server.py              FTP服务器端实现
```
