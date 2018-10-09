from connect import SshConnection
from api import Api
from mover import Mover

import logging
from logging import getLogger
import sys
from datetime import timedelta
import argparse
import requests
import subprocess
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def setup_logging(user_name):
    filename = 'logs/mover_{}.log'.format(user_name)
    logging.basicConfig(filename=filename, filemode='w', level=logging.INFO)

    logger = getLogger('main')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    return logger

def test_domains(domains, logger):
    valid_domains = []
    for domain in domains:
        try:
            requests.get('http://{0}/'.format(domain))
            valid_domains.append(domain)
        except Exception as e:
            logger.info("{} is not responding and won't be moved".format(domain))
    print(valid_domains)
    return valid_domains



def run(config, logger=None):
    if logger is None:
        logger = logging.getLogger()

    for user_name, values in config.items():
        logger.info("moving for user {0}, domains {1}".format(user_name, values['domains']))
        try:
            src = SshConnection(host=values['source']['host'],
                                user=values['source']['user'],
                                password=values['source']['password'],
                                port=22, logger=logger)
            print("source connected")
            print(values['source']['host'], values['source']['user'], values['source']['password'])
            print(values['destination']['host'], values['destination']['user'], values['destination']['password'])
            dst = SshConnection(host=values['destination']['host'],
                                user=values['destination']['user'],
                                password=values['destination']['password'],
                                port=22, logger=logger)
            print("dst connected")
        except Exception:
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

        token = Api.get_token('t.transfer', 'w8et76r4g8s7df6eresdg')
        api = Api(token)

        domains_check = list(set(values['domains']))
        domains = test_domains(domains_check, logger)


        post_comment = api.post_comment if ticket else lambda *x: None
        delay_ticket = api.delay_ticket if ticket else lambda *x: None

        result = {}
        try:
            delta = timedelta(hours=5)
            delay_ticket(user_name, ticket, delta, "transfer for user {0} has started, delayed for {1}".format(user_name, str(delta)))

            sites = mover.find_sites(domains, start_dir)

            for domain, dir in sites.items():
                logger.info("moving {0}:{1} from {2}".format(user_name, domain, dir))
                try:
                    mover.move(dir, domain)
                    result[domain] = "done"
                except:
                    logger.warning("transfer for user {0} domain {1} failed".format(user_name, domain))
                    result[domain] = "failed"
                    continue
        finally:
            post_comment("transfer finished for user {0}: {1}".format(user_name, '\n'.join(["{}: {}".format(k, v) for k, v in result.items()])), user_name, ticket, True)
            logger.info("posted to {}".format(ticket))
            subprocess.Popen(["sshpass", "-p", "{0}".format(dst.password), "scp", "logs/mover_{0}.log".format(user_name), "{0}@{1}:$HOME/.tmp/".format(dst.user, dst.host)])

if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", type=str, help="config file for transfer (full path please)", required=True)
    args = parser.parse_args()
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=Loader)
    logger = setup_logging(list(config)[0])
    try:
        run(config, logger)
    except Exception as e:
        logger.error("move failed:", str(e))
