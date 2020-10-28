from enum import Enum


class Credentials:
    def __init__(self, username, password):
        self.u = username
        self.p = password


class ThreadField(Enum):
    POST_COUNT = 1
    DATE = 2
    POST_TEXT = 3
    AUTHOR = 4
    THREAD_NEXT_PAGE = 5
    POST_POOL = 6
    THREAD_TITLE = 7


class ForumField(Enum):
    SUBFORUM_NEXT_PAGE = 1
    THREAD_POOL = 2
    THREAD_POST_COUNT = 3


class TrainingStage(Enum):
    FORUM = 1
    SUBFORUM = 2
    THREAD_POOL = 3
    SUBFORUM_NEXT_PAGE = 4
    THREAD_TITLE = 5
    POST_CONTENT = 6
    POST_DATE = 7
    POST_AUTHOR = 8
    POST_COUNT = 9
    THREAD_STRUCTURE = 10
    THREAD_NEXT_PAGE = 11
    THREAD_NEXT_PAGE2 = 12
    LOGIN_PAGE = 13
    LOGIN_USERNAME = 14
    LOGIN_PASSWORD = 15
    LOGIN_BUTTON = 16
    POST_POOL = 17
    THREAD_POST_COUNT = 18


class ElementType(Enum):
    XPATH = 1
    CLASS = 2


class ContentType(Enum):
    TEXT = 1
    NAME = 2


class WorkSession(Enum):
    MORNING = 1
    AFTERNOON = 2
    EVENING = 3
