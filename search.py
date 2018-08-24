import re
import json


class Database:
    def __init__(self, host, user, name, password):
        self.host = host
        self.user = user
        self.name = name
        self.password = password

with open("cms.json", "r", encoding='utf-8-sig') as f:
    regex = json.load(f)


def parse_config(cms):
    config = 'sample_configs/{}'.format(regex[cms]['config'])
    db_name = re.compile(regex[cms]['db_name'])
    db_host = re.compile(regex[cms]['db_host'])
    db_user = re.compile(regex[cms]['db_user'])
    db_pass = re.compile(regex[cms]['db_pass'])

    with open(config, "r") as f:
        for line in f:

            dbn = db_name.match(line)
            if dbn:
                dbn = dbn.group(1)

            dbh = db_host.match(line)
            if dbh:
                dbh = dbh.group(1)

            dbp = db_pass.match(line)
            if dbp:
                dbp = dbp.group(1)

            dbu = db_user.match(line)
            if dbu:
                dbu = dbu.group(1)

    return {'db_name': dbn, 'db_user': dbu, 'db_pass': dbp, 'db_host': dbh}