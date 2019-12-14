import os
import sys
from ftplib import FTP
from threading import Thread

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QInputDialog, QLineEdit,
                             QMainWindow, QMessageBox, QTreeWidgetItem,
                             QWidget)
from win32gui import *

from dialog import *
from GUI.ClientGui import Ui_Form
from utils import fileProperty

app_icon_path = os.path.join(os.path.dirname(__file__), 'icons')
qIcon = lambda name: QIcon(os.path.join(app_icon_path, name))

class MyMainGui(QWidget,Ui_Form):
    def __init__(self,parent=None):
        super(MyMainGui,self).__init__(parent)
        self.ftp=FTP()
        self.downloads=[]
        self.setupUi(self)
        self.Remote_Home.clicked.connect(self.cdToRemoteHomeDirectory)
        self.Remote_Filelist.itemDoubleClicked.connect(self.cdToRemoteDirectory)
        self.Remote_Filelist.itemClicked.connect(lambda: self.Remote_Download.setEnabled(True))
        self.Remote_Return.clicked.connect(self.cdToRemoteBackDirectory)
        self.Remote_Next.clicked.connect(self.cdToRemoteNextDirectory)
        self.Remote_Download.clicked.connect(self.download)

        self.Local_Home.clicked.connect(self.cdToLocalHomeDirectory)
        self.Local_Filelist.itemDoubleClicked.connect(self.cdToLocalDirectory)
        self.Local_Filelist.itemClicked.connect(lambda: self.Local_Upload.setEnabled(True))
        self.Local_Return.clicked.connect(self.cdToLocalBackDirectory)
        self.Local_Next.clicked.connect(self.cdToLocalNextDirectory)
        self.Local_Upload.clicked.connect(lambda: Thread(target=self.upload).start())
        self.Local_Connect.clicked.connect(self.connect)

        #right mouse button menu
        self.Local_Filelist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Local_Filelist.customContextMenuRequested.connect(self.local_right_menu)
        self.Remote_Filelist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Remote_Filelist.customContextMenuRequested.connect(self.remote_right_menu)

        # completer for path edit
        Remote_completer = QCompleter()
        self.Remote_completerModel = QStringListModel()
        Remote_completer.setModel(self.Remote_completerModel)
        self.Remote_path.setCompleter(Remote_completer)
        self.Remote_path.returnPressed.connect(self.cdToRemotePath)

        Local_completer = QCompleter()
        self.Local_completerModel = QStringListModel()
        Local_completer.setModel(self.Local_completerModel)
        self.Local_path.setCompleter(Local_completer)
        self.Local_path.returnPressed.connect(self.cdToLocalPath)

        #set button state by default
        self.Local_Home.setEnabled(False)
        self.Local_Return.setEnabled(False)
        self.Local_Next.setEnabled(False)
        self.Local_Upload.setEnabled(False)
        
        self.Remote_Home.setEnabled(False)
        self.Remote_Return.setEnabled(False)
        self.Remote_Next.setEnabled(False)
        self.Remote_Download.setEnabled(False)

        self.progressDialog = ProgressDialog(self)

    def _set_current_item(self, list_type, filename):
        '''
        list_type - 'local' or 'remote'
        '''

        file_list = self.Local_Filelist if list_type == 'local' else self.Remote_Filelist
        total_file = file_list.topLevelItemCount()
        for i in range(total_file):
            if(file_list.topLevelItem(i).text(0) == filename):
                file_list.setCurrentItem(file_list.topLevelItem(i))
                break   

    def local_right_menu(self, pos):
   
        item = self.Local_Filelist.currentItem()
        # item.setFlags(Qt.ItemIsEditable)
        menu = QMenu(self.Local_Filelist)
        refresh = menu.addAction("刷新")
        mkdir = menu.addAction("新建文件夹")
        newfile = menu.addAction("新建文件")
        rename = menu.addAction("重命名")
        remove = menu.addAction("删除文件")
        action = menu.exec_(self.Local_Filelist.mapToGlobal(pos))

        # refresh
        if action == refresh:
            self.updateLocalFileList()
            return

        # mkdir
        elif action == mkdir:
            try:
                dir_name = QInputDialog.getText(self, '创建文件夹', '请输出文件夹名称', QLineEdit.Normal)
                if not dir_name[1]:
                    return
                # os.mkdir(os.path.join(self.local_pwd, dir_name[0]))
                os.mkdir(self.local_pwd+'./'+dir_name[0])
                self.updateLocalFileList()
                self._set_current_item('local', dir_name[0])

            except FileExistsError:
                message = QMessageBox.information(self,'文件夹已存在','文件夹名称已存在，请修改文件名称后再创建')

        # remove 
        elif action == remove:

            topCount = self.Local_Filelist.topLevelItemCount()
            for i in range(topCount):
                item_chosen = self.Local_Filelist.topLevelItem(i)
                if (item_chosen == item):
                    break

            import shutil
            pathname = os.path.join(self.local_pwd, str(item.text(0)))
            # pathname = pathname.replace('\\', '/')
            if (os.path.isdir(pathname)):
                shutil.rmtree(pathname)
            else:
                os.remove(pathname)
            self.updateLocalFileList()
            self.Local_Filelist.setCurrentItem(self.Local_Filelist.topLevelItem(i))

        # rename
        elif action == rename:
            rename = QInputDialog.getText(self, '重命名', '请输出文件名', QLineEdit.Normal)
            if not rename[1]:
                return
            pathname = os.path.join(self.local_pwd, str(item.text(0)))
            # pathname = pathname.replace('\\', '/')
            os.rename(pathname,os.path.join(self.local_pwd, str(rename[0])))
            self.updateLocalFileList()
            self._set_current_item('local', rename[0])

        # new file
        elif action == newfile:
            file_name = QInputDialog.getText(self, '创建文件', '请输出文件名', QLineEdit.Normal)
            if not file_name[1]:
                return
            try:
                open(self.local_pwd+'./'+file_name[0], mode='x')
                import webbrowser
                webbrowser.open(self.local_pwd+'./'+file_name[0])
                self.updateLocalFileList()
                self._set_current_item('local', file_name[0])

            except FileExistsError:
                message = QMessageBox.information(self,'文件已存在','文件名已存在，请重新创建')

        else:
            return

    def remote_right_menu(self, pos):
        
        item = self.Remote_Filelist.currentItem()
        # item.setFlags(Qt.ItemIsEditable)
        menu = QMenu(self.Remote_Filelist)
        refresh = menu.addAction("刷新")
        newfile = menu.addAction("新建文件")
        mkdir = menu.addAction("新建文件夹")
        rename = menu.addAction("重命名")
        edit = menu.addAction("编辑")
        remove = menu.addAction("删除文件")
        
        action = menu.exec_(self.Remote_Filelist.mapToGlobal(pos))

        
        # refresh
        if action == refresh:
            self.updateRemoteFileList()
            return
        
        elif action == mkdir:
            try:
                dir_name = QInputDialog.getText(self, '创建文件夹', '请输出文件夹名称', QLineEdit.Normal)
                if not dir_name[1]:
                    return
                
                for i in range(self.Remote_Filelist.topLevelItemCount()):
                    if(str(self.Remote_Filelist.topLevelItem(i).text(0)) == dir_name[0]):
                        message = QMessageBox.information(self,'文件已存在','文件名已存在，请重新创建')
                        return

                pathname = os.path.join(self.pwd, dir_name[0]).replace('\\', '/')
                self.ftp.mkd(pathname)
                self.updateRemoteFileList()
                self._set_current_item('remote', dir_name[0])

            except:
                message = QMessageBox.information(self,'无权限','对不起，您没有此操作的权限')

        
        elif action == remove:
            for i in range(self.Remote_Filelist.topLevelItemCount()):
                if(self.Remote_Filelist.topLevelItem(i) == item):
                    break

            pathname = os.path.join(self.pwd, str(item.text(0))).replace('\\', '/')
            
            try:
                self.ftp.delete(pathname)
                self.updateRemoteFileList()
                self.Remote_Filelist.setCurrentItem(self.Remote_Filelist.topLevelItem(i))
            except:
                try:
                    self.ftp.rmd(pathname)
                    self.updateRemoteFileList()
                    self.Remote_Filelist.setCurrentItem(self.Remote_Filelist.topLevelItem(i))
                except:
                    message = QMessageBox.information(self, '无权限','对不起，您没有此操作的权限')

        elif action == rename:
            rename = QInputDialog.getText(self, '重命名', '请输出文件名', QLineEdit.Normal)
            if not rename[1]:
                return
            try:
                old_path = os.path.join(self.pwd, str(item.text(0))).replace('\\', '/')
                new_path = os.path.join(self.pwd, str(rename[0])).replace('\\', '/')
                self.ftp.rename(old_path, new_path)
                self.updateRemoteFileList()
                self._set_current_item('remote', rename[0])
            except:
                message = QMessageBox.information(self, '无权限','对不起，您没有此操作的权限')
        
        elif action == newfile:
            file_name = QInputDialog.getText(self, '创建文件', '请输出文件名', QLineEdit.Normal)
            if not file_name[1]:
                return
            
            for i in range(self.Remote_Filelist.topLevelItemCount()):
                if(str(self.Remote_Filelist.topLevelItem(i).text(0)) == file_name[0]):
                    message = QMessageBox.information(self,'文件已存在','文件名已存在，请重新创建')
                    return

            def _remote_newfile():
                try:
                    tmp_file = os.path.join(self.local_pwd, '##tmp##.txt')
                    open(tmp_file, mode='x')
                    m_time = os.stat(tmp_file).st_mtime

                    import webbrowser
                    webbrowser.open(tmp_file)
                    while os.stat(tmp_file).st_mtime == m_time:
                        pass
                    
                    dst_file = os.path.join(self.pwd, file_name[0]).replace('\\', '/')

                    file = open(tmp_file, 'rb')
                    fp = FTP()
                    fp.connect(host=self.ftp.host, port=self.ftp.port, timeout=self.ftp.timeout)
                    fp.login(user=self.ftp.user, passwd=self.ftp.passwd)
                    fp.set_pasv(0)
                    fp.cwd(self.pwd)
                    fp.storbinary(cmd='STOR '+dst_file, fp=file)
                    fp.quit()

                    # message = QMessageBox.information(self,'上传成功','文件上传成功')
                    print('上传成功\n')
                    file.close()
                    os.remove(tmp_file)

                    # self.updateRemoteFileList()
                    # self._set_current_item('remote', file_name[0])
                except:
                    # message = QMessageBox.information(self, '无权限','对不起，您没有此操作的权限')
                    file.close()
                    os.remove(tmp_file)
                    print('对不起，您没有此操作的权限')
            
            Thread(target=_remote_newfile).start()
        
        elif action == edit:
            pathname = os.path.join(self.pwd, str(item.text(0))).replace('\\', '/')
            tmp = item.text(0).split('.')
            file_name = ''

            if(len(tmp)) == 2:
                file_extend = tmp[1]
                file_name = '##tmp##.{}'.format(file_extend)
                tmp_file = os.path.join(self.local_pwd, file_name)
            else:
                file_name = '##tmp##.txt'
                tmp_file = os.path.join(self.local_pwd, file_name)


            def _edit_remotefile():

                try:

                    # download to a temporal file
                    def _callback(data):
                            file.write(data)
                    file = open(tmp_file, 'wb')
                    fp = FTP()
                    fp.connect(host=self.ftp.host, port=self.ftp.port, timeout=self.ftp.timeout)
                    fp.login(user=self.ftp.user, passwd=self.ftp.passwd)
                    fp.set_pasv(0)
                    fp.cwd(self.pwd)
                    fp.retrbinary(cmd='RETR '+pathname, callback=_callback)
                    fp.quit()
                    file.close()
                    print('download success \n')

                    # open the file
                    import webbrowser
                    webbrowser.open(tmp_file)
                    
                    def __window_filter(hwnd, mouse):
                        if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
                            window_names.append(GetWindowText(hwnd))

                    # judge if the window is opened
                    tmp_file_opened = False
                    while not tmp_file_opened:
                        window_names = []
                        EnumWindows(__window_filter, 0)
                        window_names = [elem for elem in window_names if elem != '']
                        for name in window_names:
                            if file_name in name:
                                tmp_file_opened = True
                                break

                    # judge if the window is closed
                    tmp_file_closed = False
                    while not tmp_file_closed:
                        window_names = []
                        tmp_file_closed = True
                        EnumWindows(__window_filter, 0)
                        window_names = [elem for elem in window_names if elem != '']
                        for name in window_names:
                            if file_name in name:
                                tmp_file_closed = False

                    # upload
                    file = open(tmp_file, 'rb')
                    fp = FTP()
                    fp.connect(host=self.ftp.host, port=self.ftp.port, timeout=self.ftp.timeout)
                    fp.login(user=self.ftp.user, passwd=self.ftp.passwd)
                    fp.set_pasv(0)
                    fp.cwd(self.pwd)
                    fp.storbinary(cmd='STOR '+pathname, fp=file)
                    fp.quit()

                    print('修改成功\n')
                    file.close()
                    os.remove(tmp_file)
                    print('success')           

                
                except:
                    file.close()
                    os.remove(tmp_file)
                    print('对不起，您没有此操作的权限')
                
            
            Thread(target=_edit_remotefile).start()


    def initialize(self):
        self.ftp.set_pasv(0)
        self.localBrowseRec    = []
        self.remoteBrowseRec   = []
        self.pwd               = self.ftp.pwd()
        ### considering Windows / Linux
        self.local_pwd = os.getenv('HOME') if os.name == 'posix' else 'D:\\'
        self.remoteOriginPath  = self.pwd
        self.localOriginPath   = self.local_pwd
        self.localBrowseRec.append(self.local_pwd)
        self.remoteBrowseRec.append(self.pwd)
        self.downloadToRemoteFileList()
        self.loadToLocaFileList()
        #set button state by default
        self.Local_Upload.setEnabled(True)
        self.Remote_Download.setEnabled(True)
        

    def connect(self):
        print('connecting....')
        try:
            from urlparse import urlparse
        except ImportError:
            from urllib.parse import urlparse

        result = QInputDialog.getText(self, 'Connect To Host', 'Host Address', QLineEdit.Normal)
        if not result[1]:
            return
        try:
            host = str(result[0].toUtf8())
        except AttributeError:
            host = str(result[0])

        try:
            if urlparse(host).hostname:
                self.ftp.connect(host=urlparse(host).hostname, port=21, timeout=10)
            else:
                self.ftp.connect(host=host, port=21, timeout=10)
            self.login()
        except:
            message = QMessageBox.information(self,'地址错误','输入地址无响应，请重新输入')
            self.connect()
        
    def login(self):
        ask = loginDialog(self)
        if not ask:
            return
        else:
            user, passwd = ask[:2]
        self.ftp.user   = user
        self.ftp.passwd = passwd
        try:
            self.ftp.login(user=user, passwd=passwd)
        except:
            message = QMessageBox.information(self,'登陆错误','账号密码错误，请重新输入')
            self.login_again()
        self.initialize( )

    def login_again(self):
        ask = loginDialog(self)
        if not ask:
            return
        else:
            user, passwd = ask[:2]
        self.ftp.user   = user
        self.ftp.passwd = passwd
        try:
            self.ftp.login(user=user, passwd=passwd)
        except:
            message=QMessageBox.information(self,'登陆错误','账号密码错误，请重新输入')
            self.login_again()


    def downloadToRemoteFileList(self):
        """
        download file and directory list from FTP Server
        """
        self.remoteWordList = []
        self.remoteDir      = {}
        self.ftp.dir('.', self.addItemToRemoteFileList)
        self.Remote_completerModel.setStringList(self.remoteWordList)

    def addItemToRemoteFileList(self, content):
        mode, num, owner, group, size, date, filename = self.parseFileInfo(content)
        if content.startswith('d'):
            icon     = qIcon('folder.png')
            pathname = os.path.join(self.pwd, filename) 
            pathname = pathname.replace('\\', '/')
            self.remoteDir[ pathname] = True
            self.remoteWordList.append(filename)

        else:
            icon = qIcon('file.png')

        item = QTreeWidgetItem()
        item.setIcon(0, icon)
        for n, i in enumerate((filename, size, date)):
            item.setText(n, i)

        self.Remote_Filelist.addTopLevelItem(item)
        if not self.Remote_Filelist.currentItem():
            self.Remote_Filelist.setCurrentItem(self.Remote_Filelist.topLevelItem(0))
            self.Remote_Filelist.setEnabled(True)

    def parseFileInfo(self, file):
        """
        parse files information "drwxr-xr-x 2 root wheel 1024 Nov 17 1993 lib" result like follower
                                "drwxr-xr-x", "2", "root", "wheel", "1024", "Nov 17 1993", "lib"
        """
        # FileMode, FilesNumber, User, Group, Size, Date, Filename
        item = [f for f in file.split(' ') if f != '']
        # if windows, item = ftype, num, size, date, filename
        # if linux, item = mode,num,owner,group,size,date,filename

        if item[0] == 'folder' or item[0] == 'file': # windows
            ftype, num, size, date, filename = (item[0], item[1], item[2], ' '.join(item[3:6]), ' '.join(item[6:]))
            return (ftype, num, size, date, filename)

        else: # linux
            mode, num, owner, group, size, date, filename = (
                item[0], item[1], item[2], item[3], item[4], ' '.join(item[5:8]), ' '.join(item[8:]))
            return (mode, num, owner, group, size, date, filename)



    def loadToLocaFileList(self):
        """
        load file and directory list from local computer
        """
        self.localWordList = []
        self.localDir      = {}
        for f in os.listdir(self.local_pwd):
            pathname = os.path.join(self.local_pwd, f)
            self.addItemToLocalFileList(fileProperty(pathname))
        self.Local_completerModel.setStringList(self.localWordList)

    def addItemToLocalFileList(self, content):

        # mode, num, owner, group, size, date, filename = self.parseFileInfo(content)
        ftype, num, size, date, filename = self.parseFileInfo(content)

        if ftype == 'folder':
            icon     = qIcon('folder.png')
            pathname = os.path.join(self.local_pwd, filename)
            self.localDir[ pathname ] = True
            self.localWordList.append(filename)

        else:
            icon = qIcon('file.png')

        item  = QTreeWidgetItem()
        item.setIcon(0, icon)
        for n, i in enumerate((filename, size, date)):
            #print((filename, size, owner, group, date, mode))
            item.setText(n, i)
        self.Local_Filelist.addTopLevelItem(item)
        if not self.Local_Filelist.currentItem():
            self.Local_Filelist.setCurrentItem(self.Local_Filelist.topLevelItem(0))
            self.Local_Filelist.setEnabled(True)

    #--------------------------#
    ## for remote file system ##
    #--------------------------#
    def cdToRemotePath(self):
        try:
            pathname = str(self.Remote_path.text().toUtf8())
        except AttributeError:
            pathname = str(self.Remote_path.text())
        try:
            self.ftp.cwd(pathname)
        except:
            return

        if self.remoteBrowseRec[self.remoteBrowseRec.index(self.pwd)]:
            self.remoteBrowseRec = self.remoteBrowseRec [:self.remoteBrowseRec.index(self.pwd)+1]

        self.pwd = pathname.startswith(os.path.sep) and pathname or os.path.join(self.pwd, pathname)
        self.pwd = self.pwd.replace('\\', '/')
        self.updateRemoteFileList()
        self.Remote_Return.setEnabled(True)

        self.remoteBrowseRec.append(self.pwd)

        if os.path.abspath(pathname) != self.remoteOriginPath:
            self.Remote_Home.setEnabled(True)
        else:
            self.Remote_Home.setEnabled(False)
        self.Remote_Next.setEnabled(False)

    def cdToRemoteDirectory(self, item, column):  #Trigger condition:Filelist_Doubleclicked
        if self.remoteBrowseRec[self.remoteBrowseRec.index(self.pwd)]:
            self.remoteBrowseRec = self.remoteBrowseRec [:self.remoteBrowseRec.index(self.pwd)+1]
        pathname = os.path.join(self.pwd, str(item.text(0)))
        pathname = pathname.replace('\\', '/')
        # print(pathname)
        if not self.isRemoteDir(pathname):
            print("No Dir Found")
            return
        self.remoteBrowseRec.append(pathname)
        self.ftp.cwd(pathname)
        self.pwd = self.ftp.pwd()
        self.updateRemoteFileList()
        self.Remote_Return.setEnabled(True)
        if pathname != self.remoteOriginPath:
            self.Remote_Home.setEnabled(True)
        self.Remote_Next.setEnabled(False)
        

    def cdToRemoteBackDirectory(self):  #Trigger condition:Click ← Button
        pathname = self.remoteBrowseRec[self.remoteBrowseRec.index(self.pwd)-1]
        if pathname != self.remoteBrowseRec[0]:
            self.Remote_Return.setEnabled(True)
        else:
            self.Remote_Return.setEnabled(False)

        if pathname != self.remoteOriginPath:
            self.Remote_Home.setEnabled(True)
        else:
            self.Remote_Home.setEnabled(False)
        self.Remote_Next.setEnabled(True)
        self.pwd = pathname
        self.ftp.cwd(pathname)
        self.updateRemoteFileList()

    def cdToRemoteNextDirectory(self):   #Trigger condition:Click → Button
        pathname = self.remoteBrowseRec[self.remoteBrowseRec.index(self.pwd)+1]
        if pathname != self.remoteBrowseRec[-1]:
            self.Remote_Next.setEnabled(True)
        else:
            self.Remote_Next.setEnabled(False)
        if pathname != self.remoteOriginPath:
            self.Remote_Home.setEnabled(True)
        else:
            self.Remote_Home.setEnabled(False)
        self.Remote_Return.setEnabled(True)
        self.pwd = pathname
        self.ftp.cwd(pathname)
        self.updateRemoteFileList()

    def cdToRemoteHomeDirectory(self):
        self.ftp.cwd(self.remoteOriginPath)
        self.pwd = self.remoteOriginPath
        self.updateRemoteFileList()
        self.Remote_Home.setEnabled(False)
        self.Remote_Return.setEnabled(False)

    #-------------------------#
    ## for local file system ##
    #-------------------------#
    def cdToLocalPath(self):
        try:
            pathname = str(self.Local_path.text().toUtf8())
        except AttributeError:
            pathname = str(self.Local_path.text())
        pathname = pathname.startswith(os.path.sep) and pathname or os.path.join(self.local_pwd, pathname)
        if not os.path.exists(pathname) and not os.path.isdir(pathname):
            return
        else:
            if self.localBrowseRec[self.localBrowseRec.index(self.local_pwd)]:
                self.localBrowseRec = self.localBrowseRec [:self.localBrowseRec.index(self.local_pwd)+1]
            self.localBrowseRec.append(pathname)
            self.local_pwd = pathname
            self.updateLocalFileList()
            self.Local_Return.setEnabled(True)
            #print(pathname, self.localOriginPath)
            if os.path.abspath(pathname) != self.localOriginPath:
                self.Local_Home.setEnabled(True)
            else:
                self.Local_Home.setEnabled(False)
            self.Local_Next.setEnabled(False)

    def cdToLocalDirectory(self, item, column):
        if self.localBrowseRec[self.localBrowseRec.index(self.local_pwd)]:
            self.localBrowseRec = self.localBrowseRec [:self.localBrowseRec.index(self.local_pwd)+1]
        pathname = os.path.join(self.local_pwd, str(item.text(0)))
        if not self.isLocalDir(pathname):
            return
        self.localBrowseRec.append(pathname)
        # print(self.localBrowseRec)
        self.local_pwd = pathname
        self.updateLocalFileList()
        self.Local_Return.setEnabled(True)
        if pathname != self.localOriginPath:
            self.Local_Home.setEnabled(True)
        self.Local_Next.setEnabled(False)

    def cdToLocalBackDirectory(self):
        pathname = self.localBrowseRec[ self.localBrowseRec.index(self.local_pwd)-1 ]
        # print(self.localBrowseRec)
        # print(self.local_pwd)
        if pathname != self.localBrowseRec[0]:
            self.Local_Return.setEnabled(True)
        else:
            self.Local_Return.setEnabled(False)
        if pathname != self.localOriginPath:
            self.Local_Home.setEnabled(True)
        else:
            self.Local_Home.setEnabled(False)
        self.Local_Next.setEnabled(True)
        self.local_pwd = pathname
        self.updateLocalFileList( )

    def cdToLocalNextDirectory(self):
        pathname = self.localBrowseRec[self.localBrowseRec.index(self.local_pwd)+1]
        # print(self.localBrowseRec)
        # print(self.local_pwd)
        if pathname != self.localBrowseRec[-1]:
            self.Local_Next.setEnabled(True)
        else:
            self.Local_Next.setEnabled(False)
        if pathname != self.localOriginPath:
            self.Local_Home.setEnabled(True)
        else:
            self.Local_Home.setEnabled(False)
        self.Local_Return.setEnabled(True)
        self.local_pwd = pathname
        self.updateLocalFileList()

    def cdToLocalHomeDirectory(self):
        self.local_pwd = self.localOriginPath
        self.updateLocalFileList()
        self.Local_Home.setEnabled(False)
        self.Local_Return.setEnabled(False)

    def updateLocalFileList(self):
        self.Local_Filelist.clear()
        self.loadToLocaFileList()

        self.Local_path.setText(self.local_pwd)

    def updateRemoteFileList(self):
        self.Remote_Filelist.clear()
        self.downloadToRemoteFileList()
        
        self.Remote_path.setText(self.pwd)

    def isLocalDir(self, dirname):
        return self.localDir.get(dirname, None)

    def isRemoteDir(self, dirname):
        return self.remoteDir.get(dirname, None)

    def download(self):

        # if len(self.downloads) == 0:
        #    Thread(target=self._check_download).start()

        dl = Thread(target=self._download)
        dl.start()
        # self.downloads.append(dl)



    def _download(self):
        item     = self.Remote_Filelist.currentItem()
        filesize = int(item.text(1))

        try:
            srcfile  = os.path.join(self.pwd, str(item.text(0).toUtf8()))
            srcfile  = srcfile.replace('\\', '/')
            dstfile  = os.path.join(self.local_pwd, str(item.text(0).toUtf8()))
            
        except AttributeError:
            srcfile  = os.path.join(self.pwd, str(item.text(0)))
            srcfile  = srcfile.replace('\\', '/')
            dstfile  = os.path.join(self.local_pwd, str(item.text(0)))

        try:
            self.progressDialog.show_sig.emit(1)
            
            origin_len = len(self.progressDialog.widgetlist)

            self.progressDialog.addProgress_sig.emit('download', 'Download '+srcfile, filesize)
            while(origin_len == len(self.progressDialog.widgetlist)):
                pass

            pb = self.progressDialog.widgetlist[len(self.progressDialog.widgetlist)-1]

            def callback(data):
                pb.updateProgress.emit(data)
                # pb.set_value(data)
                file.write(data)
            
            file = open(dstfile, 'wb')
            fp = FTP()
            fp.connect(host=self.ftp.host, port=self.ftp.port, timeout=self.ftp.timeout)
            fp.login(user=self.ftp.user, passwd=self.ftp.passwd)
            fp.set_pasv(0)
            fp.cwd(self.pwd)
            fp.retrbinary(cmd='RETR '+srcfile, callback=callback)
        except:
            print('对不起，您没有此操作的权限')
            # message = QMessageBox.information(self,'无权限','对不起，您没有此操作的权限')


        

    def upload(self):
        item     = self.Local_Filelist.currentItem()
        filesize = int(item.text(1))

        try:
            srcfile  = os.path.join(self.local_pwd, str(item.text(0).toUtf8()))
            dstfile  = os.path.join(self.pwd, str(item.text(0).toUtf8()))
            dstfile  = dstfile.replace('\\', '/')
        except AttributeError:
            srcfile  = os.path.join(self.local_pwd, str(item.text(0)))
            dstfile  = os.path.join(self.pwd, str(item.text(0)))
            dstfile  = dstfile.replace('\\', '/')

        try:
            self.progressDialog.show_sig.emit(1)
            origin_len = len(self.progressDialog.widgetlist)
            self.progressDialog.addProgress_sig.emit('upload', 'Upload '+srcfile, filesize)
            while origin_len == len(self.progressDialog.widgetlist):
                pass
            
            pb = self.progressDialog.widgetlist[len(self.progressDialog.widgetlist)-1]

            def callback(data):
                pb.updateProgress.emit(data)

            file = open(srcfile, 'rb')
            fp = FTP()
            fp.connect(host=self.ftp.host, port=self.ftp.port, timeout=self.ftp.timeout)
            fp.login(user=self.ftp.user, passwd=self.ftp.passwd)
            fp.set_pasv(0)
            fp.cwd(self.pwd)
            fp.storbinary(cmd='STOR '+dstfile, fp=file, callback=callback)
        except:
            # message = QMessageBox.information(self,'无权限','对不起，您没有此操作的权限')
            print('对不起，您没有此操作的权限')

        
if __name__ == "__main__":
    app=QApplication(sys.argv)
    myWin=MyMainGui()
    myWin.show()
    sys.exit(app.exec_())
