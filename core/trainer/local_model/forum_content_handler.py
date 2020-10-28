# I feel so bad for this "local_model", but Python ignores absolute imports.


class ForumContentHandler:

    def __init__(self):
        self.forum_name_list = []
        self.subforum_name_list = []
        self.thread_name_list = []
        self.subforum_next_page_name = ""
        self.thread_next_page_name = ""
        self.thread_title = ""
        self.post_content = []
        self.post_date = []
        self.post_author = []
        self.post_count = []
        self.login_username = ""
        self.login_password = ""
        self.login_button = ""
        self.post_pool = []
        self.thread_post_count = []

    def reset(self):
        self.__init__()

    def fill_json(self):

        return {
            "forums": self.get_forum_names(),
            "subforums": self.get_subforum_names(),
            "thread_pool": self.get_thread_names(),
            "subforum_next_page": self.get_subforum_next_page_name(),
            "thread_title": self.get_thread_title(),
            "thread_next_page": self.get_thread_next_page_name(),
            "post_content": self.get_post_content(),
            "post_date": self.get_post_date(),
            "post_author": self.get_post_author(),
            "post_count": self.get_post_count(),
            "login_username": self.get_login_username(),
            "login_password": self.get_login_password(),
            "login_button": self.get_login_button(),
            "post_pool": self.get_post_pool(),
            "thread_post_count": self.get_thread_post_count()
        }

    def handle_request(self, request_path, data):
        if request_path == "/forum_name":
            self.add_forum_name(data)

        if request_path == "/subforum_name":
            self.add_subforum_name(data)

        if request_path == "/thread_name":
            self.add_thread_name(data)

        if request_path == "/subforum_next_page":
            self.add_subforum_next_page_name(data)

        if request_path == "/thread_next_page":
            self.add_thread_next_page_name(data)

        if request_path == "/thread_title":
            self.add_thread_title(data)

        if request_path == "/post_content":
            self.add_post_content(data)

        if request_path == "/post_author":
            self.add_post_author(data)

        if request_path == "/post_date":
            self.add_post_date(data)

        if request_path == "/post_count":
            self.add_post_count(data)

        if request_path == "/login_username":
            self.add_login_username(data)

        if request_path == "/login_password":
            self.add_login_password(data)

        if request_path == "/login_button":
            self.add_login_button(data)

        if request_path == "/post_pool":
            self.add_post_pool(data)

        if request_path == "/thread_post_count":
            self.add_thread_post_count(data)

    def add_forum_name(self, forum_name):
        self.forum_name_list.append(forum_name)

    def add_subforum_name(self, subforum_name):
        self.subforum_name_list.append(subforum_name)

    def add_thread_name(self, thread_name):
        self.thread_name_list.append(thread_name)

    def add_subforum_next_page_name(self, thread_name):
        self.subforum_next_page_name = thread_name

    def add_thread_next_page_name(self, thread_next_page_name):
        self.thread_next_page_name = thread_next_page_name

    def add_thread_title(self, thread_title):
        self.thread_title = thread_title

    def add_post_content(self, post_content):
        self.post_content = post_content

    def add_post_author(self, post_author):
        self.post_author = post_author

    def add_post_date(self, post_date):
        self.post_date = post_date

    def add_post_count(self, post_count):
        self.post_count = post_count

    def add_login_username(self, login_username):
        self.login_username = login_username

    def add_login_password(self, login_password):
        self.login_password = login_password

    def add_login_button(self, login_button):
        self.login_button = login_button

    def add_post_pool(self, post_pool):
        self.post_pool = post_pool

    def add_thread_post_count(self, thread_post_count):
        self.thread_post_count = thread_post_count

    def get_forum_names(self):
        return self.forum_name_list

    def get_subforum_names(self):
        return self.subforum_name_list

    def get_thread_names(self):
        return self.thread_name_list

    def get_subforum_next_page_name(self):
        return self.subforum_next_page_name

    def get_thread_next_page_name(self):
        return self.thread_next_page_name

    def get_thread_title(self):
        return self.thread_title

    def get_post_content(self):
        return self.post_content

    def get_post_author(self):
        return self.post_author

    def get_post_date(self):
        return self.post_date

    def get_post_count(self):
        return self.post_count

    def get_login_username(self):
        return self.login_username

    def get_login_password(self):
        return self.login_password

    def get_login_button(self):
        return self.login_button

    def get_post_pool(self):
        return self.post_pool

    def get_thread_post_count(self):
        return self.thread_post_count
