import helpers
from connect import SshConnection


class Mover:
    def __init__(self, dst_conn: SshConnection, src_conn: SshConnection):
        self._local = dst_conn
        self._remote = src_conn

    def find_sites(self, domains, path):
        return self._remote.find_sites(domains, path)

    def move(self, src_dir):
        rsync_cmd = helpers.make_rsync_command(self._remote.host,
                                               self._remote.user,
                                               self._remote.password,
                                               src_dir)
        self._local.command(rsync_cmd)
