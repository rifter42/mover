import subprocess
from threading import Thread
from queue import Queue

import psutil
import os
from utils import *

class SubprocessRunner(object):

    """
    :type process subprocess.Popen
    """
    def __init__(self, command, logger=None, nice=19, log_prefix="subprocess", **process_options):
        self.command = command
        self.nice = nice
        self.logger = logger
        self.process = None
        self.log_prefix = log_prefix

        self.process_options = self._extend_options(process_options)

    def run(self):
        """

        :rtype: SubprocessRunner
        """
        command = map(lambda item: as_default_string(item), self.command)
        self.process = subprocess.Popen(command, **self.process_options)

        return self

    def wait(self, extended_return=False, write_output_in_log=True):
        """

        :rtype: tuple|str
        """
        out, err = self.process.communicate()

        try:
            if err and self.logger:
                self.logger.error("%s : Error: %s" % (as_unicode(self.log_prefix), as_unicode(err)))

            if out and write_output_in_log and self.logger:
                self.logger.debug("%s : command output: %s" % (as_unicode(self.log_prefix), as_unicode(out)))

        except:
            if self.logger:
                self.logger.error("%s : Error when write log" % (as_unicode(self.log_prefix)))

        return (out, err, self.process.returncode) if extended_return else out

    def _extend_options(self, options):
        """

        :rtype: dict
        """
        options['cwd'] = options.get('cwd', None)
        options['preexec_fn'] = options.get('preexec_fn', self.pre_exec)
        options['stderr'] = options.get('stderr', subprocess.PIPE)
        options['stdout'] = options.get('stdout', subprocess.PIPE)

        return options

    def pre_exec(self):
        """
        Назначает nice и ionice команде
        """
        os.nice(self.nice)

        p = psutil.Process(os.getpid())
        p.ionice(psutil.IOPRIO_CLASS_IDLE)

    def iterate(self):
        try:
            if self.logger:
                self.logger.debug("%s : iterate command %s" % (as_unicode(self.log_prefix), as_unicode(self.command)))
        except Exception as e:
            if self.logger:
                self.logger.error("%s : Error when write log: %s" % (as_unicode(self.log_prefix), str(e)))

        def enqueue_output(out, queue):
            for line in iter(out.readline, ""):
                queue.put(line.rstrip('\n'))
            out.close()

        def enqueue_errors(err, queue):
            for line in iter(err.readline, ""):
                queue.put(line.rstrip('\n'))
            err.close()

        command = [as_default_string(item) for item in self.command]
        self.process = subprocess.Popen(command, **self.process_options)

        q_out = Queue()
        q_err = Queue()

        t_out = Thread(target=enqueue_output, args=(self.process.stdout, q_out))
        t_out.daemon = True
        t_out.start()

        t_err = Thread(target=enqueue_errors, args=(self.process.stderr, q_err))
        t_err.daemon = True
        t_err.start()

        while True:
            if not q_err.empty():
                err_output = q_err.get()
            else:
                err_output = ""

            if err_output != "":
                if self.logger:
                    self.logger.error("%s : Error: %s" % (as_unicode(self.log_prefix), as_unicode(err_output)))
                raise Exception(err_output)

            if not q_out.empty():
                line_output = q_out.get()
            else:
                line_output = ""

            code = self.process.poll()

            if self.logger and line_output != "":
                try:
                    self.logger.debug(
                        "%s : command iterate: %s" % (as_unicode(self.log_prefix), as_unicode(line_output)))
                except Exception as e:
                    self.logger.error(
                        "%s : Error when write command iterate log: %s" % (as_unicode(self.log_prefix), str(e)))

            if line_output == "":
                if code is not None:
                    self.logger.debug("%s : command iterate end" % as_unicode(self.log_prefix))
                    break

            yield line_output



def get_util(name, use_chroot=None):
    """
    returns absolute path to executable
    :param str|unicode name:
    :return:
    """
    command = ["/bin/which", name]

    env = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"}
    p = SubprocessRunner(command=command, env=env)
    p.run()

    return p.wait().strip()


def make_rsync_command(host, user, password, dir):
    """

    :rtype: list
    """
    cmd = [get_util("rsync")]
    args = ["-r", "-l", "-c", "-p", "-v"]
    cmd.extend(args)
    cmd.append("%s@%s:%s".format(user, host, dir))
    cmd.append(".")
    return cmd
