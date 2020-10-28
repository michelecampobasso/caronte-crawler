import random
from datetime import datetime, timedelta, time, date

from pytz import timezone


class WorkSchedule:
    def __init__(self, weekday):
        if 0 <= weekday <= 3:
            self.default_duration_minutes_morning = 0
            self.default_start_time_morning = None
            self.default_duration_minutes_afternoon = 210
            self.default_start_time_afternoon = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=17, minute=0)))
            self.default_duration_minutes_evening = 210
            self.default_start_time_evening = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=21, minute=30)))

            self.start_time_morning = None
            self.end_time_morning = None
            self.actual_duration_minutes_morning = 0
            self.start_time_afternoon = None
            self.end_time_afternoon = None
            self.actual_duration_minutes_afternoon = 0
            self.start_time_evening = None
            self.end_time_evening = None
            self.actual_duration_minutes_evening = 0
        else:
            if weekday == 4:
                self.default_duration_minutes_morning = 0
                self.default_start_time_morning = None
                self.default_duration_minutes_afternoon = 210
                self.default_start_time_afternoon = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=17, minute=0)))
                self.default_duration_minutes_evening = 390
                self.default_start_time_evening = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=21, minute=30)))

                self.start_time_morning = None
                self.end_time_morning = None
                self.actual_duration_minutes_morning = 0
                self.start_time_afternoon = None
                self.end_time_afternoon = None
                self.actual_duration_minutes_afternoon = 0
                self.start_time_evening = None
                self.end_time_evening = None
                self.actual_duration_minutes_evening = 0
            else:
                if weekday == 5:
                    self.default_duration_minutes_morning = 270
                    self.default_start_time_morning = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=10, minute=0)))
                    self.default_duration_minutes_afternoon = 300
                    self.default_start_time_afternoon = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=15, minute=30)))
                    self.default_duration_minutes_evening = 330
                    self.default_start_time_evening = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=21, minute=30)))

                    self.start_time_morning = None
                    self.end_time_morning = None
                    self.actual_duration_minutes_morning = 0
                    self.start_time_afternoon = None
                    self.end_time_afternoon = None
                    self.actual_duration_minutes_afternoon = 0
                    self.start_time_evening = None
                    self.end_time_evening = None
                    self.actual_duration_minutes_evening = 0
                else:
                    if weekday == 6:
                        self.default_duration_minutes_morning = 210
                        self.default_start_time_morning = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=10, minute=0)))
                        self.default_duration_minutes_afternoon = 360
                        self.default_start_time_afternoon = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=14, minute=30)))
                        self.default_duration_minutes_evening = 210
                        self.default_start_time_evening = timezone("Europe/Moscow").localize(datetime.combine(date.today(), time(hour=21, minute=30)))

                        self.start_time_morning = None
                        self.end_time_morning = None
                        self.actual_duration_minutes_morning = 0
                        self.start_time_afternoon = None
                        self.end_time_afternoon = None
                        self.actual_duration_minutes_afternoon = 0
                        self.start_time_evening = None
                        self.end_time_evening = None
                        self.actual_duration_minutes_evening = 0
                    else:
                        raise ValueError

        # I might take some rest or I would like to do something else
        if random.random() < 0.20:
            self.default_duration_minutes_morning = 0
            self.default_start_time_morning = None
        if random.random() < 0.20:
            self.default_duration_minutes_afternoon = 0
            self.default_start_time_afternoon = None
        # I don't want to be unproductive all day
        if random.random() < 0.20 and \
                not (self.default_start_time_morning is None and self.default_start_time_afternoon is None):
            self.default_duration_minutes_evening = 0
            self.default_start_time_evening = None

        # This is not a work, no need to be in time!
        if self.default_start_time_morning is not None:
            start_delay_minutes_morning = self.get_late_start_minutes(self.default_duration_minutes_morning)
            self.actual_duration_minutes_morning = self.get_actual_duration_minutes(
                self.default_duration_minutes_morning, start_delay_minutes_morning)
            self.start_time_morning = self.get_actual_start_time(self.default_start_time_morning,
                                                                 start_delay_minutes_morning)
            self.end_time_morning = self.get_actual_end_time(self.start_time_morning,
                                                             self.actual_duration_minutes_morning)

        if self.default_start_time_afternoon is not None:
            start_delay_minutes_afternoon = self.get_late_start_minutes(self.default_duration_minutes_afternoon)
            self.actual_duration_minutes_afternoon = self.get_actual_duration_minutes(
                self.default_duration_minutes_afternoon, start_delay_minutes_afternoon)
            self.start_time_afternoon = self.get_actual_start_time(self.default_start_time_afternoon,
                                                                   start_delay_minutes_afternoon)
            self.end_time_afternoon = self.get_actual_end_time(self.start_time_afternoon,
                                                               self.actual_duration_minutes_afternoon)

        if self.default_start_time_evening is not None:
            start_delay_minutes_evening = self.get_late_start_minutes(self.default_duration_minutes_evening)
            self.actual_duration_minutes_evening = self.get_actual_duration_minutes(
                self.default_duration_minutes_evening, start_delay_minutes_evening)
            self.start_time_evening = self.get_actual_start_time(self.default_start_time_evening,
                                                                 start_delay_minutes_evening)
            self.end_time_evening = self.get_actual_end_time(self.start_time_evening,
                                                             self.actual_duration_minutes_evening)

    @staticmethod
    def get_late_start_minutes(work_session_duration):
        return 0.25 * random.random() * work_session_duration

    @staticmethod
    def get_actual_start_time(work_session_start, start_delay):
        return work_session_start + timedelta(hours=start_delay / 60, minutes=start_delay % 60)

    @staticmethod
    def get_actual_duration_minutes(work_session_duration, start_delay):
        return work_session_duration - (0.25 * random.random() * work_session_duration) - start_delay

    @staticmethod
    def get_actual_end_time(work_session_start, duration):
        return work_session_start + timedelta(hours=duration / 60, minutes=duration % 60)
