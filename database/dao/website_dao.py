import ast


class WebsiteDAO:

    def __init__(self, db):
        self.__db = db

    # Retrieves a list of XPATHS that point to one or more forums.
    def get_forum_xpaths_by_url(self, url):
        return [item[0] for item in self.__db.query(
            "SELECT DISTINCT forum_xpaths FROM `WEBSITE` WHERE `url` = %s",
            url).fetchall()]

    # Retrieves a list of XPATHS that point to one or more subforums.
    def get_subforum_xpaths_by_url_and_parent_xpath(self, url, forum_xpath):
        return [item[0] for item in self.__db.query(
            """SELECT subforum_xpaths FROM `WEBSITE` WHERE `url` = %s AND `forum_xpaths` = %s""",
            (url, forum_xpath)).fetchall()]

    def get_website_id_by_url(self, url):
        website_id_array = self.__db.query(
            "SELECT website_id FROM `WEBSITE` WHERE `url` = %s",
            url).fetchone()
        website_id = None
        if website_id_array is not None:
            website_id = website_id_array[0]
        return website_id

    # Retrieves a list of partial names that point to one or more forums.
    def get_forum_partial_names_by_website_id(self, website_id):
        return ast.literal_eval(self.__db.query(
            "SELECT value FROM `WEBSITE` WHERE `website_id` LIKE %s",
            website_id).fetchone()[0])

    # Retrieves a list of partial names that point to one or more subforums.
    def get_subforum_partial_names_by_website_id(self, website_id):
        return ast.literal_eval(self.__db.query(
            "SELECT value FROM `WEBSITE` WHERE `website_id` LIKE %s",
            website_id).fetchone()[0])

    def get_is_vbullettin_by_website_id(self, website_id):
        return self.__db.query("SELECT `is_vbullettin` FROM `WEBSITE` WHERE `website_id` = %s", website_id).fetchone()[0]

    def set_is_vbullettin_by_website_id(self, website_id):
        args = [1, website_id]
        self.__db.query("UPDATE `WEBSITE` SET `is_vbullettin` = %s WHERE `website_id` = %s", args)
        self.__db.commit()

    def insert_link_forum_subforum_xpaths(self, website_id, current_page, forum_page_xpath, subforum_xpath):
        args = [website_id, current_page, forum_page_xpath, subforum_xpath, "False"]
        self.__db.query(
            "INSERT INTO `WEBSITE`(`website_id`, `url`, `forum_xpaths`, `subforum_xpaths`, `is_vbullettin`) VALUES "
            "(%s, %s, %s, %s, %s)",
            args)
        self.__db.commit()

        



