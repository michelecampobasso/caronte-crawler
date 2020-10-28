import random
from time import sleep

from utils.commons import print_warning


class BreakTime:
    def __init__(self):
        self.break_duration_min_seconds = 5 * 60
        self.break_duration_max_seconds = 30 * 60

    def take_a_break(self):
        return random.randint(self.break_duration_min_seconds, self.break_duration_max_seconds)

    def should_i_take_a_break(self):
        if random.random() > 0.97:
            print_warning("[CRAWLER] Caronte needs to smoke a cigarette. Will work in a while.")
            sleep(self.take_a_break())
        else:
            print_warning("[CRAWLER] Not taking any break. Need to work!")
