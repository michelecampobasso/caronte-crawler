class LoginFields:
    def __init__(self, signin_popup_xpath, username_xpath, password_xpath, login_xpath):
        self.signin_popup_xpath = signin_popup_xpath
        self.username_xpath = username_xpath
        self.password_xpath = password_xpath
        self.login_xpath = login_xpath


class ForumFields:
    def __init__(self, thread_pool_xpath, subforum_next_page_xpath):
        self.thread_pool_xpath = thread_pool_xpath
        self.subforum_next_page_xpath = subforum_next_page_xpath


class SpecificForumFields:
    def __init__(self, forum_xpaths, subforum_xpaths):
        self.forum_xpaths = forum_xpaths
        self.subforum_xpaths = subforum_xpaths


class ThreadFields:
    def __init__(self, post_pool_xpath, date_class, post_text_class, author_class, post_count_class, thread_next_page_xpath):
        self.post_pool_xpath = post_pool_xpath
        self.date_class = date_class
        self.post_text_class = post_text_class
        self.author_class = author_class
        self.post_count_class = post_count_class
        self.thread_next_page_xpath = thread_next_page_xpath
