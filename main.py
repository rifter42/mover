import argparse
from connect import SshConnection, ApiConnection
from mover import Mover
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from pprint import pprint
import logging
from logging import getLogger
import sys
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument('-s', type=str, help='ssh/ftp host')
parser.add_argument('-u', type=str, help='ssh/ftp user')
parser.add_argument('-p', type=str, help='ssh/ftp pass')
parser.add_argument('-d', type=str, help='domain')
args = parser.parse_args()

def setup_logging():
    logging.basicConfig(filename='mover.log', filemode='w', level=logging.INFO)

    logger = getLogger('main')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    return logger

if __name__ == '__main__':

    logger = setup_logging()
    with open("config.yaml", 'r') as f:
        config = yaml.load(f, Loader=Loader)
        pprint(config)



    for user_name, values in config.items():
        logger.info("moving for user {0}, domains {1}".format(user_name, values['domains']))
        try:
            src = SshConnection(host=values['source']['host'],
                            user=values['source']['user'],
                            password=values['source']['password'],
                            port=22, logger=logger)
            dst = SshConnection(host=values['destination']['host'],
                            user=values['destination']['user'],
                            password=values['destination']['password'],
                            port=22, logger=logger)
        except Exception as e:
            continue

        mover = Mover(dst, src, logger)

        try:
            start_dir = values['source']['start_dir']
        except KeyError:
            start_dir = '~/'

        try:
            ticket = values['ticket']
        except KeyError:
            logger.info("ticket not found for user {}".format(user_name))
            ticket = None

        token = ApiConnection.get_token('a.smirnova', 'eIwUpSjzHmXD')
        api = ApiConnection(token)

        domains = list(set(values['domains']))

        if ticket is not None:
            now = datetime.now()
            delay_time = format(now + timedelta(hours=5), '%Y-%m-%d %H:%M:%S')
            api.delay_ticket('ca73902', ticket, delay_time, "transfer for user {0} has started, delayed until {1}".format(user_name, delay_time))

        sites = mover.find_sites(domains, start_dir)

        for domain, dir in sites.items():
            logger.info("moving {0}:{1} from {2}".format(user_name, domain, dir))
            result = mover.move(dir, domain)

            if ticket is not None:
                comm = api.post_comment("transfer finished for user {0} domain {1}".format(user_name, domain), 'ca73902', ticket)
                logger.info("posted to {}".format(ticket))
            pprint(result[0][-2:]) # pizdos

        if ticket is not None:
            now = datetime.now()
            delay_time = format(now + timedelta(minutes=2), '%Y-%m-%d %H:%M:%S')
            #api.delay_ticket('ca73902', ticket, delay_time, "transfer finished for user {}".format(user_name))