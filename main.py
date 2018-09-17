import argparse
from connect import SshConnection, FtpConnection
from mover import Mover
parser = argparse.ArgumentParser()
parser.add_argument('-s', type=str, help='ssh/ftp host')
parser.add_argument('-u', type=str, help='ssh/ftp user')
parser.add_argument('-p', type=str, help='ssh/ftp pass')
parser.add_argument('-d', type=str, help='domain')
args = parser.parse_args()


if __name__ == '__main__':
    #ssh = SshConnection(host='liadeiso.beget.tech', user='liadeiso', password='T9AoqGEW', port=22)
    #mover = Mover(ssh)
    # sites = mover.find_sites(["liadeiso.beget.tech", "django2.liadeiso.beget.tech"], "/home/l/liadeiso")
   # db = ssh.dump_db("liadeiso_card", "localhost", "liadeiso_card", "*s73r2g^")
    #with open("testdump.sql", 'w') as f:
   #     f.writelines(db)
   # print(db)
    ftp = FtpConnection('liadeiso.beget.tech', 'liadeiso', 'T9AoqGEW', port=21)
    ftp.find_sites(['liadeiso.beget.tech'])