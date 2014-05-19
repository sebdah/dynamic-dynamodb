# -*- coding: utf-8 -*-
"""
Python daemon implementation from:

http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
"""
import atexit
import os
import sys
import time
from signal import SIGTERM


class Daemon:
    """ A generic daemon class

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null',
                 stdout='/dev/null', stderr='/dev/null'):
        """ Constructor """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """ Do the UNIX double-fork magic

        See Stevens' "Advanced Programming in the UNIX Environment" for
        details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(
                "fork #1 failed: %d (%s)\n" % (err.errno, err.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(
                "fork #2 failed: %d (%s)\n" % (err.errno, err.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        try:
            file(self.pidfile, 'w+').write("%s\n" % pid)
        except IOError as err:
            raise

    def delpid(self):
        os.remove(self.pidfile)

    def start(self, *args, **kwargs):
        """ Start the daemon """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        try:
            self.daemonize()
        except IOError:
            raise
        self.run(*args, **kwargs)

    def stop(self):
        """ Stop the daemon """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            sys.stderr.write(
                "pidfile {0} does not exist. Daemon not running?\n".format(
                    self.pidfile))
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self, *args, **kwargs):
        """ Restart the daemon """
        self.stop()
        try:
            self.start(*args, **kwargs)
        except IOError:
            raise

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """
