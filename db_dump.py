import search
import subprocess


def dump(host, user, db, password):
    command = ['mysqldump', '-u', '{}'.format(user), '{}'.format(db),
               '-p', '{}'.format(password), '-h', '{}'.format(host)]
    subprocess.run(command)

dbdata = search.parse_config(cms)

dump(dbdata['db_host'], dbdata['db_user'], dbdata['db_name'], dbdata['db_pass'])

H U Y