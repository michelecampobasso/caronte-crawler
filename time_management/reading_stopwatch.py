from random import randint
from time import sleep


def wait_simple_pause():
    sleep(randint(3, 7))


def wait_to_read(text):
    word_count = text.split().__len__()
    reading_speed = randint(140, 200)
    time_to_read = word_count * 60 / reading_speed
    sleep(time_to_read)
    # print "########### I WOULD WAIT " + str(time_to_read) + " FOR A TEXT OF " + str(word_count) + " WORDS."

