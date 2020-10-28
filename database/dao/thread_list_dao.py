class ThreadListDAO:

    def __init__(self, db):
        self.__db = db

    def get_post_count_by_thread_url(self, thread_link):
        return self.__db.query(
            "SELECT `post_count` FROM `THREAD_LIST` WHERE `thread_url` = %s", thread_link).fetchone()[0]

    def update_post_count(self, thread_link, post_count):
        args = [thread_link, post_count]
        self.__db.query(
            "UPDATE `THREAD_LIST` SET `post_count` = %s WHERE thread_url = %s", args)
        self.__db.commit()

    def insert_post_count(self, thread_link, post_count):
        args = [thread_link, post_count]
        self.__db.query(
            "INSERT INTO `THREAD_LIST`(`thread_url`, `post_count`) VALUES (%s, %s)", args)
        self.__db.commit()

    def has_ever_been_scanned(self, thread_link):
        return False if self.__db.query(
            "SELECT EXISTS ( SELECT * FROM `THREAD_LIST` WHERE thread_url = %s)", thread_link).fetchone()[0] == 0 \
            else True
