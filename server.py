import socket
import os
import sys
import time
import threading
from utils import fileProperty

CWD  = os.getenv('HOME') if os.name == 'posix' else 'D:\\'
CWD = os.path.join(CWD, 'ftp')
USERNAME = 'public'
PASSWORD = 'public'

class FtpServerProtocol(threading.Thread):
    def __init__(self, commSock, address):
        threading.Thread.__init__(self)
        self.authenticated = False
        # self.pasv_mode = False
        self.rest = False
        self.cwd = CWD
        self.commSock = commSock # communication socket
        self.address = address
        self.upload = [os.path.join(CWD, 'upload')]
        self.download = [os.path.join(CWD, 'download')]

    def _send_command(self, cmd):
        self.commSock.send(cmd.encode('utf-8'))
    
    def _send_data(self, data):
        if isinstance(data, bytes):
            self.dataSock.send(data)
        else:
            self.dataSock.send(data.encode('utf-8'))

    def send_welcome(self):
        self._send_command('220 Welcome.\r\n')

    def run(self):
        '''
        recieve commands from client and execute commands
        '''
        self.send_welcome()
        while True:

            # get command(cmd) from client
            try:
                data = self.commSock.recv(1024).rstrip()
                try:
                    cmd = data.decode('utf-8')
                except AttributeError:
                    cmd = data
                print('Received data: {}'.format(cmd))
                if not cmd:
                    break
            except socket.error as err:
                print('Receive', err)
            
            # run functions according to command
            #    cmd
            #   /  \
            # cmd  arg
            try:
                cmd, arg = cmd[:4].strip().upper(), cmd[4:].strip() or None
                func = getattr(self, cmd) # get function according to cmd
                func(arg) # func's args
            except AttributeError as err:
                self._send_command('500 Syntax error, command unrecognized. '
                    'This may include errors such as command line too long.\r\n')
                print('Receive', err)
    
    def start_data_sock(self):
        print('start data socket: Openning a data channel\n')
        try:
            self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.dataSock.connect((self.dataSockAddr, self.dataSockPort))
        except socket.error as err:
            print('start data socket{}\n'.format(err))
    

    def stop_data_sock(self):
        print('stop data socket: closing a data channel\n')
        try:
            self.dataSock.close()
            '''
            if self.pasv_mode:
                self.serverSock.close()
            '''
        except socket.error as err:
            print('stop data socket', err, '\n')

    
    ### Ftp services and functions

    def USER(self, user):
        print('USER:', user, '\n')
        if not user:
            self._send_command('501 Syntax error in parameters or arguments.\r\n')
        elif not user == USERNAME:
            self._send_command('502 Username error.\r\n')
        else:
            self._send_command('331 User name okay, need password.\r\n')
            print('user name ok\n')
            self.username = user

    def PASS(self, passwd):
        print('PASS:', passwd, '\n')
        if not passwd:
            self._send_command('501 Syntax error in parameters or arguments.\r\n')

        elif not self.username:
            self._send_command('503 Bad sequence of commands.\r\n')

        elif not passwd == PASSWORD:
            self._send_command('504 Password error.\r\n')
        else:
            self._send_command('230 User logged in, proceed.\r\n')
            self.passwd = passwd
            self.authenticated = True
    
    def TYPE(self, type):
        print('TYPE', type)
        self.mode = type
        if self.mode == 'I':
            self._send_command('200 Binary mode.\r\n')
        elif self.mode == 'A':
            self._send_command('200 Ascii mode.\r\n')

    # client tells server addr and port it watches
    def PORT(self, cmd):
        print('PORT:', cmd, '\r')

        # TODO:
        l=cmd.split(',')
        # print('l={}'.format(l))
        self.dataSockAddr='.'.join(l[:4])
        self.dataSockPort=(int(l[4])<<8)+int(l[5])
        self._send_command('200 Get port.\r\n')

    # ls
    def LIST(self, dirpath):
        if not self.authenticated:
            self._send_command('530 User not logged in.\r\n')
            return
        
        if not dirpath: # current directory
            pathname = os.path.abspath(os.path.join(self.cwd, '.'))
        elif dirpath.startswith(os.path.sep): # start with /, abspath
            pathname = os.path.abspath(dirpath)
        else: # cwd/dirpath
            pathname = os.path.abspath(os.path.join(self.cwd, dirpath))
        
        print('LIST:{}\n'.format(pathname))
        if not os.path.exists(pathname):
            self._send_command('550 LIST failed: Path name not exists.\r\n')
        else:
            self._send_command('150 Here is listing.\r\n')
            self.start_data_sock()

            # TODO
            if not os.path.isdir(pathname):
                fileMessage = fileProperty(pathname)
                self._send_data(fileMessage+'\r\n')
            else:
                for f in os.listdir(pathname):
                    # TODO
                    fileMessage = fileProperty(os.path.join(pathname, f))
                    self._send_data(fileMessage+'\r\n')
            
            self.stop_data_sock()
            self._send_command('226 List done.\r\n')

    # change working directory
    def CWD(self, dirpath):
        pathname = dirpath.startswith(os.path.sep) and dirpath or os.path.join(self.cwd, dirpath)
        print('CWD:{}\n'.format(pathname))
        if not os.path.exists(pathname) or not os.path.isdir(pathname):
            self._send_command('550 CWD failed Directory not exists.\r\n')
            return
        self.cwd = pathname
        self._send_command('250 CWD Command successful.\r\n')

    # pwd
    def PWD(self, cmd):
        print('PWD:{}\n'.format(cmd))
        self._send_command('257 "{}"\r\n'.format(self.cwd))

    def _permission(self, type_):
        '''
        type_ - 'download', 'upload', 'others'
        '''
        print(self.cwd + '\n')
        if type_ == 'download':
            denied_path = self.upload
        elif type_ == 'upload':
            denied_path = self.download
        else:  # others
            denied_path = self.upload + self.download

        for _denied_path in denied_path:
            if _denied_path in self.cwd:
                self._send_command('500 Permission denied.\r\n')
                return False

        return True


    # delete
    def DELE(self, filename):

        if self._permission(type_='others') == False:
            return

        pathname = filename.startswith(os.path.sep) and filename or os.path.join(self.cwd, filename)
        print('DELE:{}\n'.format(pathname))
        if not self.authenticated:
            self._send_command('530 User not logged in.\r\n')
        elif not os.path.exists(pathname):
            self._send_command('550 DELE failed File {} not exists.\r\n'.format(pathname))
        elif os.path.isdir(pathname):
            self._send_command('555 DELE failed File {} is a directory.\r\n'.format(pathname))
        else:
            os.remove(pathname)
            self._send_command('250 File deleted.\r\n')

    # mkdir
    def MKD(self, dirname):

        if self._permission(type_='others') == False:
            return

        pathname = dirname.startswith(os.path.sep) and dirname or os.path.join(self.cwd, dirname)
        print('MKD:{}\n'.format(pathname))
        if not self.authenticated:
            self._send_command('530 User not logged in.\r\n')
        
        else:
            try:
                os.mkdir(pathname)
                self._send_command('257 Directory created.\r\n')
            except OSError:
                self._send_command('550 MKD failed Directory {} already exists.\r\n'.format(pathname))
    
    # rm directory
    def RMD(self, dirname):

        if self._permission(type_='others') == False:
            return

        pathname = dirname.startswith(os.path.sep) and dirname or os.path.join(self.cwd, dirname)
        print('RMD:{}\n'.format(pathname))
        if not self.authenticated:
            self._send_command('530 User not logged in.\r\n')
        elif not os.path.exists(pathname):
            self._send_command('550 RMDIR failed Directory {} not exists.\r\n'.format(pathname))
        elif not os.path.isdir(pathname):
            self._send_command('555 RMDIR failed {} is a file.\r\n'.format(pathname))
        else:
            import shutil
            shutil.rmtree(pathname)
            self._send_command('250 Directory deleted.\r\n')
    
    # rename file
    def RNFR(self, filename):

        if self._permission(type_='others') == False:
            return

        pathname = filename.startswith(os.path.sep) and filename or os.path.join(self.cwd, filename)
        print('RNFR:{}\n'.format(pathname))
        if not os.path.exists(pathname):
            self._send_command('550 RNFR failed File or Directory {} not exists.\r\n'.format(pathname))
        else:
            self.rnfr = pathname
            self._send_command('300 RNFR success.\r\n')
            print('RNFR success')

    # rename to
    def RNTO(self, filename):
        pathname = filename.startswith(os.path.sep) and filename or os.path.join(self.cwd, filename)
        print('RNTO:{}'.format(pathname))
        try:
            os.rename(self.rnfr, pathname)
            self._send_command('260 RNTO success.\r\n')
        except OSError as err:
            print('RNTO', err)
    
    # file pointer points to pos
    def REST(self, pos):
        self.pos = int(pos)
        print('REST:{}\n'.format(self.pos))
        self.rest = True
        self._send_command('250 File position reseted.\r\n')
    
    def RETR(self, filename):
        if self._permission(type_='download') == False:
            return

        pathname = os.path.join(self.cwd, filename)
        print('RETR:{}\n'.format(pathname))
        if not os.path.exists(pathname):
            return
        try:
            if self.mode == 'I':
                file = open(pathname, 'rb')
            else:
                file = open(pathname ,'r')
        except OSError as err:
            print('RETR:{}\n'.format(err))
        
        self._send_command('150 Opening data connection.\r\n')
        if self.rest:
            file.seek(self.pos)
            self.rest = False
        
        self.start_data_sock()
        while True:
            data = file.read(1024)
            if not data:
                break
            self._send_data(data)
        file.close()
        self.stop_data_sock()
        self._send_command('266 Transfer complete.\r\n')

    # store # cover old file
    def STOR(self, filename):
        if self._permission(type_='upload') == False:
            return
        
        pathname = os.path.join(self.cwd, filename)
        print('STOR:{}\n'.format(pathname))
        try:
            if self.mode == 'I':
                file = open(pathname, 'wb')
            else:
                file = open(pathname ,'w')
        except OSError as err:
            print('STORE:{}\n'.format(err))
        
        self._send_command('150 Opening data connection,\r\n')
        self.start_data_sock()
        while True:
            data = self.dataSock.recv(1024)
            if not data:
                break
            file.write(data)
        file.close()
        self.stop_data_sock()
        self._send_command('226 Transfer completed.\r\n')

    
    def QUIT(self, arg):
        print('QUIT:{}\n'.format(arg))
        self._send_command('221 Goodbye.\r\n')
    


def server_listener():
    global listen_sock
    HOST='192.168.92.128'
    PORT=21
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind((HOST, PORT))
    listen_sock.listen(5)
    print('Server started', 'Listen on: {}'.format(listen_sock.getsockname()))

    while True:
        connection, address = listen_sock.accept()
        f = FtpServerProtocol(connection, address)
        f.start()
        print('Accept: Create a new connection {}'.format(address))


if __name__ == '__main__':
    print('Start ftp server, Enter q or Q to stop ftp server..\n')
    listener = threading.Thread(target=server_listener)
    listener.start()

    # default py3
    if input().lower() == 'q':
        listen_sock.close()
        print('Server stop: Sever closed.\n')
        sys.exit()


