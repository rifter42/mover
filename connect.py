import json
import re
from abc import ABCMeta, abstractmethod
import ftplib
import os
from collections import defaultdict
import paramiko
import requests
import io


FILE = 'site_search.txt'
HASH = '535e596808c20d846742340676c90f38'

class RemoteConnection(metaclass=ABCMeta):
    def __init__(self, host, user, password, port):
        self.port = port
        self.password = password
        self.user = user
        self.host = host

    @abstractmethod
    def find_sites(self, domains, path):
        raise NotImplementedError

    @abstractmethod
    def dump_db(self, db_name, db_host, db_user, db_password, site):
        raise NotImplementedError

class FtpConnection(RemoteConnection):
    def dump_db(self, db_name, db_host, db_user, db_password, site):
        pass

    def __init__(self, host, user, password, port):
        super().__init__(host, user, password, port)
        conn = ftplib.FTP(self.host, self.user, self.password)
        conn.set_pasv(True)
        self.conn = conn

    def try_cwd(self, dir):
        try:
            self.conn.cwd(dir)
        except:
            return False
        return True

    def traverse(self, startpath="/", depth=2):
        print("searching for dirs.........")
        dirs = {i: [] for i in range(depth + 1)}
        dirs[0] = startpath
        for key, value in dirs.items():
            for entry in value:
                try:
                    dirs[key + 1].extend(self.conn.nlst(entry))
                except:
                    break
        for key in dirs:
            dirs[key] = list([x for x in dirs[key] if self.try_cwd(x)])
        return dirs


    def find_sites(self, domains, path='/'):
        dirs = self.traverse(path)
        sites = defaultdict()
        self.conn.cwd(path)
        for dirlist in dirs.values():
            for dir in dirlist:
                print("looking in dir", dir, "..........")
                domain, site_path = self._find_site_path(domains, dir)
                if site_path:
                    domains.remove(domain)
                    sites[domain] = os.path.normpath(os.path.join(path, site_path))
        print(sites)
        return sites

    def _find_site_path(self, domains, path):
        self.conn.cwd(path)
        tempf = io.BytesIO(bytes(HASH, "utf-8"))
        self.conn.storbinary("STOR site_search.txt", tempf)
        domain, ret_path = None, None
        for domain in domains:
            response = requests.get('http://{0}/{1}'.format(domain, FILE))
            if HASH in str(response.content):
                domain, ret_path = domain, self.conn.pwd()
        self.conn.delete("site_search.txt")
        return domain, ret_path


class SshConnection(RemoteConnection):
    def __init__(self, host, user, password, port, logger):
        super().__init__(host, user, password, port)
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        conn.connect(hostname=self.host, username=self.user, password=self.password)
        self.conn = conn
        self.logger = logger.getChild('ssh')

    def find_sites(self, domains, path='/'):
        self.logger.info("searching for {0} in {1}".format(domains, path))
        self.command("find . -type f -name 'site_search.txt' -delete") # pizdos
        sites = defaultdict()
        self.command("cd {}".format(path))
        dirs, err = self.command("find . -type d -maxdepth 2")
        for dir in dirs:
            domain, site_path = self._find_site_path(domains, dir)
            if site_path:
                domains.remove(domain)
                sites[domain] = os.path.normpath(os.path.join(path, site_path))
                self.logger.info("found {0} in {1}".format(domain, site_path))
                self.command("find . -type f -name 'site_search.txt' -delete")
        self.logger.info("search finished")
        return sites


    def dump_db(self, db_name, db_host, db_user, db_password, site):
        self.logger.info("dumping db {}".format(db_name))
        return self.command("mysqldump -h {0} -u{1} -p'{2}' {3} > {4}".format(
            db_host, db_user, db_password, db_name, os.path.join(site, "dump.sql")
        ))

    def _find_site_path(self, domains, path):
        path = path.rstrip()
        file_path = os.path.join(path, FILE)
        self.command("echo {0} > {1}".format(HASH, file_path))
        domain, ret_path = None, None
        for domain in domains:
            response = requests.get('http://{0}/{1}'.format(domain, FILE))
            if HASH in str(response.content):
                domain, ret_path = domain, path

        return domain, ret_path

    def parse_config(self, site):
        with open("cms.json", "r", encoding='utf-8-sig') as f:
            regex = json.load(f)


        for k, v in regex.items():
            out, err = self.command("cat {0}".format(os.path.join(site,k)))
            if err != []:
                continue
            db_name = re.compile(regex[k]['db_name'])
            db_host = re.compile(regex[k]['db_host'])
            db_user = re.compile(regex[k]['db_user'])
            db_pass = re.compile(regex[k]['db_pass'])
            result = {}
            for line in out:
                dbn = db_name.match(line)
                if dbn:
                    result['db_name'] = dbn.group(1)

                dbh = db_host.match(line)
                if dbh:
                    result['db_host'] = dbh.group(1)

                dbp = db_pass.match(line)
                if dbp:
                    result['db_pass'] = dbp.group(1)

                dbu = db_user.match(line)
                if dbu:
                    result['db_user'] = dbu.group(1)

            return result


    def command(self, cmd: str, extended_return=False):
        self.logger.debug("executing {}".format(cmd))
        stdin, stdout, stderr = self.conn.exec_command(cmd)
        return_code = stdout.channel.recv_exit_status()
        stdout = stdout.readlines()
        stderr = stderr.readlines()

        if extended_return:
            return stdout, stderr, return_code

        return stdout, stderr



# def ftp_listing(ftp, depth=0):
#     if depth > 3:
#         return ['depth > 3']
#     level = {}
#     for entry in (path for path in ftp.nlst() if path not in ('.', '..')):
#         try:
#             ftp.cwd(entry)
#             level[entry] = ftp_listing(ftp, depth+1)
#             ftp.cwd('..')
#         except ftplib.error_perm:
#             level[entry] = None
#     return level

 # АЛГОРИТМ:
# 1. ПОСОСАТЬ ХУЙ
# 2. ЛИСТИНГ директрории
# 3. ПОСОСАТЬ ХУЙ
# 4. СДАМПИТЬ ДБ
# 5. ПОСОСАТЬ ХУЙ
# 6. GTHTYTCNB CFQN
# 7. ПОСОСАТЬ ХУЙ
# 8. Коды рсинка
# 9. GJCJCFNM {EQ
# 10. Л О Г И
# 11. ХУЙ ДОСОСАН