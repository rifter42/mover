import os
import requests
from collections import defaultdict
import glob


FILE = 'site_search.txt'
HASH = '535e596808c20d846742340676c90f38'

def recursive_scan_dirs(domains, path='/'):
    os.chdir(path)
    sites = defaultdict()
    for root, dirs, files in os.walk(path):
        if root.count('/') > 3:
            continue
        for domain in domains:
            site_path = find_domain(domain, root)
            if site_path:
                sites[domain] = site_path
    if len(sites.keys()) == len(domains):
        return sites

    return None



def find_domain(domain, path):
    file_path = os.path.join(path, FILE)
    with open(file_path, 'w+') as f:
        print(file_path)
        f.write(HASH)
    response = requests.get('http://{0}/{1}'.format(domain, FILE))
    os.remove(file_path)
    if HASH in str(response.content):
        return path

    return None

print(recursive_scan_dirs(["127.0.0.1", "127.0.0.1:8000"], "/home/s"))