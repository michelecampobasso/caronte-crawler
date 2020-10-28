import os
import signal
import threading
import time
import datetime
from subprocess import call

from crontab import CronTab

from utils.commons import print_warning, print_error_and_exit


class SnoozeAlarm(threading.Thread):

    def __init__(self, zzz, restart_time, hours_to_add):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.zzz = zzz
        self.restart_time = restart_time
        self.hours_to_add = hours_to_add

    def run(self):
        print_warning("[CRAWLER] I will work for " + str(self.zzz/3600) + " hours and " + str((self.zzz % 3600)/60) + " minutes.")
        time.sleep(self.zzz)
        print_warning("[CRAWLER] Stop working for now. Scheduling next work session...")
        self.schedule_restart()
        os.kill(os.getpid(), signal.SIGTERM)

    def schedule_restart(self):
        f = open("/home/user/launcher.sh", "w")
        f.write("#!/bin/bash\n")
        f.write("Xvfb :1 -screen 0 800x600x8 & \n")
        f.write("export DISPLAY=\":1\"\n")
        f.write("export PATH=\"$PATH:/usr/local/bin\"\n")
        f.write("/usr/bin/python /home/user/PycharmProjects/untitled/__main__.py 2>./jeez.err >./jeez.log\n")

        call(["chmod", "+x", "/home/user/launcher.sh"])

        my_cron = CronTab(user='user')
        my_cron.remove_all(comment='crawler_execution')
        my_cron.write()
        job = my_cron.new(command='. $HOME/.profile; /home/user/launcher.sh 2>./jeez.err >./jeez.log',
                          comment='crawler_execution')

        hour = self.restart_time.hour
        minute = self.restart_time.minute
        job.setall(datetime.time(hour=(hour + self.hours_to_add) % 24, minute=minute))
        my_cron.write()
        message = "[CRAWLER] Next work session is scheduled for "
        if (hour + self.hours_to_add) > 23:
            message = message + "tomorrow "
        else:
            message = message + "today "
        message = message + "at " + str(datetime.time((hour + self.hours_to_add) % 24, minute, 0)) + ", local time."
        print_error_and_exit(message)
