import hashlib


class PostDumpDAO:

    def __init__(self, db):
        self.__db = db

    def insert_post_dump(self, website_id, thread_link, thread_name, author, date, post_count, post_text):
        # Date has not been used for hashing purposes since some forums translate them automatically depending on the
        # TOR circuit created.
        hash = hashlib.md5((str(website_id) + thread_link + thread_name + author + post_count + post_text).encode('utf-8')).hexdigest()
        args = [hash, website_id, thread_link, thread_name, author, date, post_count, post_text]
        self.__db.query(
            "INSERT INTO `POST_DUMPS`(`hash`, `website_id`, `thread_url`, `thread_name`, `author`, `date`, `post_count`, "
            "`post_content`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", args)
        self.__db.commit()

    def check_if_post_dump_exists(self, website_id, thread_link, thread_name, author, date, post_count, post_text):
        # Date has not been used for hashing purposes since some forums translate them automatically depending on the
        # TOR circuit created.
        hash = hashlib.md5((str(website_id) + thread_link + thread_name + author + post_count + post_text).encode('utf-8')).hexdigest()
        element_count = self.__db.query(
            "SELECT COUNT(1) FROM `POST_DUMPS` WHERE `hash` = %s", hash).fetchone()[0]
        if element_count == 1:
            return True
        else:
            return False

    def get_collected_posts_count_by_thread_link(self, thread_link):
        return self.__db.query(
            "SELECT COUNT(*) FROM `POST_DUMPS` WHERE `thread_url` = %s",
            thread_link).fetchone()[0]
