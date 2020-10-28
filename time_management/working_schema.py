import signal
from subprocess import call
from time import sleep

import pytz
from tzlocal import get_localzone

from model.base_classes import WorkSession
from time_management.break_time import BreakTime
from time_management.work_schedule import *
from crontab import CronTab
from utils.commons import print_error_and_exit, print_warning
from datetime import time
from utils.snooze_alarm import SnoozeAlarm


class WorkingSchema:

    def __init__(self, program):

        self.program = program
        self.now = datetime.now(pytz.timezone('Europe/Moscow'))
        self.weekday = self.now.weekday()
        self.work_schedule = WorkSchedule(self.weekday)
        self.hours_to_add = int(self.calculate_timezone_difference_hours())

        # TODO PARAMETRIZE
        f = open("/home/user/launcher.sh", "w")
        f.write("#!/bin/bash\n")
        f.write("Xvfb :1 -screen 0 800x600x8 & \n")
        f.write("export DISPLAY=\":1\"\n")
        f.write("export PATH=\"$PATH:/usr/local/bin\"\n")
        f.write("/usr/bin/python /home/user/PycharmProjects/untitled/__main__.py 2>./jeez.err >./jeez.log\n")

        call(["chmod", "+x", "/home/user/launcher.sh"])

        self.my_cron = CronTab(user='user')
        self.my_cron.remove_all(comment='crawler_execution')
        self.my_cron.write()
        self.job = self.my_cron.new(command='. $HOME/.profile; /home/user/launcher.sh 2>./jeez.err >./jeez.log',
                                    comment='crawler_execution')

    def to_work_or_not_to_work(self):
        if self.work_schedule.start_time_morning is not None and self.now < self.work_schedule.start_time_morning:
            # Too early to work, schedule morning
            self.schedule_job_and_close(
                self.work_schedule.start_time_morning.hour, self.work_schedule.start_time_morning.minute, False)
        else:
            if self.work_schedule.start_time_morning is not None and self.now < self.work_schedule.end_time_morning:
                # Morning work session
                self.setup_end_job_handler((self.work_schedule.end_time_morning - self.now).seconds,
                                           WorkSession.MORNING)
            else:
                if self.work_schedule.start_time_afternoon is not None and self.now < self.work_schedule.start_time_afternoon:
                    # Too early to work, schedule afternoon
                    self.schedule_job_and_close(
                        self.work_schedule.start_time_afternoon.hour,
                        self.work_schedule.start_time_afternoon.minute, False)
                else:
                    if self.work_schedule.start_time_afternoon is not None and self.now < self.work_schedule.end_time_afternoon:
                        # Afternoon work session
                        self.setup_end_job_handler((self.work_schedule.end_time_afternoon - self.now).seconds,
                                                   WorkSession.AFTERNOON)
                    else:
                        # Too early to work, schedule evening
                        if self.work_schedule.start_time_evening is not None and self.now < self.work_schedule.start_time_evening:
                            self.schedule_job_and_close(self.work_schedule.start_time_evening.hour,
                                                        self.work_schedule.start_time_evening.minute, False)
                        else:
                            if self.work_schedule.start_time_evening is not None and self.now < self.work_schedule.end_time_evening:
                                # Evening work session
                                self.setup_end_job_handler((self.work_schedule.end_time_evening - self.now).seconds,
                                                           WorkSession.EVENING)
                            else:
                                # Too late to work tonight. Let's go with tomorrow.
                                tomorrow_work_schedule = WorkSchedule((self.weekday + 1) % 7)
                                if 0 <= (self.weekday + 1) % 7 <= 4:
                                    # I'll work tomorrow afternoon, since is weekday
                                    while tomorrow_work_schedule.start_time_afternoon is None:
                                        tomorrow_work_schedule = WorkSchedule(self.weekday)
                                    self.schedule_job_and_close(tomorrow_work_schedule.start_time_afternoon.hour,
                                                                tomorrow_work_schedule.start_time_afternoon.minute, True)
                                else:
                                    # I'll work tomorrow morning, since is weekend
                                    while tomorrow_work_schedule.start_time_morning is None:
                                        tomorrow_work_schedule = WorkSchedule(self.weekday)
                                    self.schedule_job_and_close(tomorrow_work_schedule.start_time_morning.hour,
                                                                tomorrow_work_schedule.start_time_morning.minute, True)
        sleep(1)  # Yeah, just for waiting SnoozeAlarm to print its stdout...
        self.print_work_schedule()
        # Linux's cron doesn't allow expressing seconds. For this reason, an analysis could make noticeable that all the
        # sessions start are at the same amounts of seconds, in good network conditions.
        seconds_to_wait = random.randint(1, 60)
        print_warning("[BOOTSTRAP] Delaying start time of " + str(seconds_to_wait) + " seconds...")
        sleep(seconds_to_wait)
        self.setup_breaks_handler()

    def calculate_timezone_difference_hours(self):
        local_timestamp = datetime.now()
        local_timestamp_offset_awa = get_localzone().localize(local_timestamp)
        moscow_timestamp = pytz.timezone("Europe/Moscow").localize(local_timestamp)
        delta = moscow_timestamp - local_timestamp_offset_awa
        return round(delta.total_seconds() / 60.0 / 60.0)

    # Every minute, I have a chance of 3% to get a break.
    def setup_breaks_handler(self):
        signal.signal(signal.SIGALRM, self.break_handler)
        signal.alarm(60)

    def break_handler(self, signal_number, frame):
        distraction = BreakTime()
        distraction.should_i_take_a_break()
        self.setup_breaks_handler()

    '''
    Quick note: I'll skip only the next session if it isn't a morning. 
    '''
    def setup_end_job_handler(self, duration_in_seconds, current_work_session):
        # Figuring out next_work_session
        next_work_session = None
        if current_work_session == WorkSession.MORNING:
            if self.work_schedule.start_time_afternoon is not None:
                # I'll work in the afternoon
                next_work_session = self.work_schedule.start_time_afternoon
            else:
                # I'll work in the evening
                if self.work_schedule.start_time_evening is not None:
                    next_work_session = self.work_schedule.start_time_evening
                else:
                    private_work_schedule = WorkSchedule(self.weekday)
                    while private_work_schedule.start_time_evening is None:
                        private_work_schedule = WorkSchedule(self.weekday)
                    next_work_session = private_work_schedule.start_time_evening
        else:
            if current_work_session == WorkSession.AFTERNOON:
                if self.work_schedule.start_time_evening is not None:
                    # I'll work in the evening
                    next_work_session = self.work_schedule.start_time_evening
                else:
                    if 0 <= (self.weekday + 1) % 7 <= 4:
                        # I'll work tomorrow afternoon, since is weekday
                        private_work_schedule = WorkSchedule((self.weekday + 1) % 7)
                        while private_work_schedule.start_time_afternoon is None:
                            private_work_schedule = WorkSchedule(self.weekday)
                        next_work_session = private_work_schedule.start_time_afternoon
                    else:
                        # I'll work tomorrow morning, since is weekend
                        private_work_schedule = WorkSchedule((self.weekday + 1) % 7)
                        while private_work_schedule.start_time_morning is None:
                            private_work_schedule = WorkSchedule(self.weekday)
                        next_work_session = private_work_schedule.start_time_morning
            else:
                if current_work_session == WorkSession.EVENING:
                    if 0 <= (self.weekday + 1) % 7 <= 4:
                        # I'll work tomorrow afternoon, since is weekday
                        private_work_schedule = WorkSchedule((self.weekday + 1) % 7)
                        while private_work_schedule.start_time_afternoon is None:
                            private_work_schedule = WorkSchedule(self.weekday)
                        next_work_session = private_work_schedule.start_time_afternoon
                    else:
                        # I'll work tomorrow morning, since is weekend
                        private_work_schedule = WorkSchedule((self.weekday + 1) % 7)
                        while private_work_schedule.start_time_morning is None:
                            private_work_schedule = WorkSchedule(self.weekday)
                        next_work_session = private_work_schedule.start_time_morning

        SnoozeAlarm(duration_in_seconds, next_work_session, self.hours_to_add).start()

    def schedule_job_and_close(self, hour, minute, tomorrow):
        self.job.setall(time(hour=(hour + self.hours_to_add) % 24, minute=minute))
        self.my_cron.write()
        message = "[SCHEDULER] Out of work time. Scheduled respawn "
        if (hour + self.hours_to_add) > 23 or tomorrow:
            message = message + "tomorrow "
        else:
            message = message + "today "
        message = message + "at " + str(time((hour + self.hours_to_add) % 24, minute, 0)) + ", local time."
        self.program.driver.close()
        print_error_and_exit(message)

    def print_work_schedule(self):
        print_warning("===================")
        print_warning("Time now here: " + str(get_localzone().localize(datetime.now())))
        print_warning("Time now in Moscow: " + str(datetime.now(pytz.timezone('Europe/Moscow'))))
        print_warning("===================")
        print_warning("Work schedule (in Europe/Moscow timezone): ")
        print_warning("====> Start morning: " + str(self.work_schedule.start_time_morning) + "; duration: " + str(
            self.work_schedule.actual_duration_minutes_morning))
        print_warning("====> Start afternoon: " + str(self.work_schedule.start_time_afternoon) + "; duration: " + str(
            self.work_schedule.actual_duration_minutes_afternoon))
        print_warning("====> Start evening: " + str(self.work_schedule.start_time_evening) + "; duration: " + str(
            self.work_schedule.actual_duration_minutes_evening))
        print_warning("===================")