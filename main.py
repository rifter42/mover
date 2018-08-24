import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', type=str, 'ssh/ftp host')
parser.add_argument('-u', type=str, 'ssh/ftp user')
parser.add_argument('-p', type=str, 'ssh/ftp pass')
parser.add_argument('-d', type=str, 'domain')
args = parser.parse_args()


if __name__ == '__main__':
    pass