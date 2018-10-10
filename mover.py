import logging
import helpers
from connect import SshRemote


class RcodeError(BaseException):
    pass


class Mover:

    """
    Класс, который непосредственно осуществляет перенос сайтов
    """

    def __init__(self, dst_conn: SshRemote, src_conn: SshRemote, logger):
        """
        :param dst_conn: объект подключения к серверу назначения
        :param src_conn: аналогично с сервером, с которого мы переносим сайты
        :param logger:
        """
        self.logger = logger.getChild("mover")
        self._local = dst_conn
        self._remote = src_conn

    def find_sites(self, domains, path):
        """
        Обертка для функции поиска сайтов в SshRemote
        :param domains:
        :param path:
        :return:
        """
        return self._remote.find_sites(domains, path)

    def move(self, src_dir, domain):
        """
        Метод для переноса сайтов
        :param src_dir:
        :param domain:
        :return:
        """
        self.logger.info("starting move")
        self._addkey()
        dst_dir = "~/.tmp/{}".format(domain)
        self._local.command("mkdir -p {}".format(dst_dir))
        rsync_cmd = helpers.make_rsync_command(self._remote.host,
                                               self._remote.user,
                                               self._remote.password,
                                               src_dir, dst_dir)
        self.logger.info("parsing config")
        try:
            dbconfig = self._remote.parse_config(src_dir)
            self._remote.dump_db(db_host=dbconfig['db_host'],
                                 db_name=dbconfig['db_name'],
                                 db_user=dbconfig['db_user'],
                                 db_password=dbconfig['db_pass'],
                                 site=src_dir)
        except Exception as e:
            self.logger.info("config not found")

        self.logger.info("executing rsync {}".format(rsync_cmd))
        return self._exec_rsync(rsync_cmd)

    @helpers.retry(RcodeError, logger=logging.getLogger('main').getChild('mover'))
    def _exec_rsync(self, cmd: str) -> tuple:
        """
        :param cmd:
        :return:
        """
        stdout, stderr, rcode = self._local.command(cmd, extended_return=True)

        if rcode != 0:
            self.logger.info("failed to launch rsync with error {0}, code {1}".format(stderr, rcode))
            raise RcodeError

        return stdout, stderr

    def _addkey(self):
        """
        ААААААААА БЛЯДЬ НЕ ДЕЛАЙТЕ ТАК
        (добавляет ключ на удаленный хост (иногда))
        :return:
        """
        self.logger.info("adding ssh key")
        self._local.command("mkdir -p ~/.ssh")
        self._remote.command("mkdir -p ~/.ssh")
        cmd = 'yes | ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa_move -q -N "" > /dev/null'
        self._local.command(cmd)
        key, err = self._local.command("cat ~/.ssh/id_rsa_move.pub")
        self._remote.command("echo {0} >> ~/.ssh/authorized_keys".format(key[0].rstrip()))
        self.logger.info("key added")
