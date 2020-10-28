import os
import signal
import sys
import time


# TODO Arrange proper logger with different levels.
def print_error(message):
    print "[-] " + time.ctime()[4:] + " " + message
    sys.stdout.flush()
    return


def print_error_and_exit(message="Unknown error, aborting..."):
    print_error(message)
    sys.stdout.flush()
    os.kill(os.getpid(), signal.SIGTERM)


def print_error_and_exception(message, e):
    print_error(message)
    if hasattr(e, 'msg'):
        if e.msg is not None:
            print e.msg
    sys.stdout.flush()
    return


def print_warning(message):
    print "[.] " + time.ctime()[4:] + " " + message
    sys.stdout.flush()
    return


def print_successful_status(message):
    print "[+] " + time.ctime()[4:] + " " + message
    sys.stdout.flush()
    return


def print_internals(message):
    print "[*] " + time.ctime()[4:] + " " + message
    sys.stdout.flush()
    return

