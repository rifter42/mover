import ftplib
import paramiko


class RemoteConnection:
    def __init__(self, host, user, password, port):
        self.port = port
        self.password = password
        self.user = user
        self.host = host

class FtpConnection(RemoteConnection):
    def __init__(self, host, user, password, port):
        super().__init__(host, user, password, port)
        conn = ftplib.FTP(self.host, self.user, self.password)
        conn.set_pasv(True)
        self.conn = conn

class SshConnection(RemoteConnection):
    def __init__(self, host, user, password, port):
        super().__init__(host, user, password, port)
        conn = paramiko.SSHClient()
        conn.connect(hostname=self.host, username=self.user, password=self.password)
        self.conn = conn

class RsyncConnection(RemoteConnection):
    def __init__(self, host, user, password, port):
        super().__init__(host, user, password, port)
        self.command = ['rsync', '-r', '-l', '-c', '-v', '--log-file=perenos.log']


class ScpConnection(RemoteConnection):
    def __init__(self, host, user, password, port):
        super().__init__(host, user, password, port)
        self.command = ['scp', '-r', '-v']

