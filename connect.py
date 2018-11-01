import json
import re
from abc import ABCMeta, abstractmethod
import os
from collections import defaultdict
import paramiko
import requests


FILE = 'site_search.txt'
HASH = '535e596808c20d846742340676c90f38'

class BaseRemote(metaclass=ABCMeta):
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



class SshRemote(BaseRemote):

    """
    Класс удаленного подключения.
    Выполняет команды на удаленном сервере, ищет сайты, делает дампы БД.
    """

    def __init__(self, host, user, password, port, logger):
        super().__init__(host, user, password, port)
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        self.logger = logger.getChild('ssh')

        try:
            conn.connect(hostname=self.host, username=self.user, password=self.password)
            self.conn = conn
        except Exception as e:
            self.logger.info("can't connect via ssh for user {}".format(user))
            raise e

    def find_sites(self, domains, path='/'):

        """
        Поиск сайтов
        :param domains:
        :param path:
        :return:
        """

        _domains = domains # чтобы не менять переданный список и не использовать [:]

        self.logger.info("searching for {0} in {1}".format(domains, path))
        self.command("find . -type f -name 'site_search.txt' -delete")

        sites = defaultdict()

        dirs, err = self.command("find $PWD -type d -maxdepth 2", pwd=path)
        for dir in dirs:
            domain, site_path = self._find_site_path(_domains, dir)
            if site_path:
                _domains.remove(domain)
                sites[domain] = os.path.normpath(os.path.join(path, site_path))
                self.logger.info("found {0} in {1}".format(domain, site_path))
                self.command("find . -type f -name 'site_search.txt' -delete")

        self.logger.info("search finished")
        return sites


    def dump_db(self, db_name, db_host, db_user, db_password, site):

        """
        :param db_name:
        :param db_host:
        :param db_user:
        :param db_password:
        :param site:
        :return:
        """

        self.logger.info("dumping db {}".format(db_name))
        return self.command("mysqldump -h {0} -u{1} -p'{2}' {3} > {4}".format(
            db_host, db_user, db_password, db_name, os.path.join(site, "dump.sql")
        ))

    def _find_site_path(self, domains, path):

        """
        Ищем сайты в переданной директории
        В директорию кладется файл site_search.txt
        и делается запрос к домену. Если в ответе есть хэш
        :param domains:
        :param path:
        :return:
        """

        path = path.rstrip()
        file_path = os.path.join(path, FILE)
        self.command("echo {0} > {1}".format(HASH, file_path))

        for domain in domains:
            response = requests.get('http://{0}/{1}'.format(domain, FILE))
            if HASH in str(response.content):
                ret_domain, ret_path = domain, path
                self.command("rm '{}'".format(file_path))
                return ret_domain, ret_path
        return None, None

    def parse_config(self, site):

        """
        Парсинг конфигов разных CMS
        :param site:
        :return:
        """

        with open("cms.json", "r", encoding='utf-8') as f:
            regex = json.load(f)


        for filename, params in regex.items():
            out, err = self.command("cat {0}".format(os.path.join(site, filename)))
            if err != []:
                continue

            db_name = re.compile(params['db_name'])
            db_host = re.compile(params['db_host'])
            db_user = re.compile(params['db_user'])
            db_pass = re.compile(params['db_pass'])

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


    def command(self, cmd: str, pwd=None, extended_return=False):

        """
        Запускает команду на удаленном сервере
        :param cmd:
        :param pwd:
        :param extended_return: возвращать return code помимо stdout, stderr
        :return:
        """

        _cmd = cmd
        if pwd:
            _cmd = "cd {0}; {1}".format(pwd, cmd)

        self.logger.debug("executing {}".format(_cmd))

        stdin, stdout, stderr = self.conn.exec_command(_cmd)
        return_code = stdout.channel.recv_exit_status()
        stdout = stdout.readlines()
        stderr = stderr.readlines()

        if extended_return:
            return stdout, stderr, return_code

        return stdout, stderr

