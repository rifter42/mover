class Mover:
    def __init__(self, connection):
        self._connection = connection

    def find_sites(self, domains, path):
        return self._connection.find_sites(domains, path)