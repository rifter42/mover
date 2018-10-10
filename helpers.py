import time
from functools import wraps


def make_rsync_command(host, user, password, dir, dst_dir):

    """
    ОЧЕНЬ ХОРОШАЯ ФУНКЦИЯ КОТОРАЯ ВОЗВРАЩАЕТ ОЧЕНЬ ДЛИННУЮ СТРОКУ КОМАНДЫ RSYNC И КОММЕНТ ТОЖЕ ДЛИННЫЙ
    :param host:
    :param user:
    :param password:
    :param dir:
    :param dst_dir:
    :return:
    :rtype: str
    """

    return "RSYNC_PASSWORD={0} rsync --bwlimit=500k -e 'ssh -i '$HOME/.ssh/id_rsa_move' -o StrictHostKeyChecking=no' --log-file=$HOME/.tmp/rsync.log -rlcp {2}@{3}:{4} {5} ".format(password, dst_dir, user, host, dir, dst_dir)

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    # StackOverflow-driven development

    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
