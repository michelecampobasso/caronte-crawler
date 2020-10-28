from model.base_classes import ElementType


class ForumFieldsDAO:

    """
    NOTE: Consider yourself warned from the desire of parametrize field_name as happens in website_dao: you can inject
    only parameters and not keywords or so on.

    """
    def __init__(self, db):
        self.__db = db

    def get_field_class_by_website_id(self, website_id, field_name):
        field_name = field_name.lower() + "_class"

        tmp = self.__db.query("SELECT " + field_name + " FROM `FORUM_FIELDS` WHERE `website_id` = %s", website_id
                               ).fetchone()[0]
        return tmp

    def get_field_xpath_by_website_id(self, website_id, field_name):
        field_name = field_name.lower() + "_xpath"
        tmp = self.__db.query("SELECT " + field_name + " FROM `FORUM_FIELDS` WHERE `website_id` = %s", website_id
                               ).fetchone()[0]
        return tmp

    def insert_thread_pool_id(self, website_id, element_id, element_type):
        args = [website_id, element_id]
        if element_type == ElementType.XPATH:
            query = "INSERT INTO `FORUM_FIELDS`(`website_id`, `thread_pool_xpath`) VALUES (%s, %s)"
        else:
            query = "INSERT INTO `FORUM_FIELDS`(`website_id`, `thread_pool_class`) VALUES (%s, %s)"
        self.__db.query(query, args)
        self.__db.commit()

    def insert_subforum_next_page(self, website_id, element_id, element_type):
        args = [element_id, website_id]
        if element_type == ElementType.XPATH:
            query = "UPDATE `FORUM_FIELDS` SET `subforum_next_page_xpath`=%s WHERE `website_id` = %s"
        else:
            query = "UPDATE `FORUM_FIELDS` SET `subforum_next_page_class`=%s WHERE `website_id` = %s"
        self.__db.query(query, args)
        self.__db.commit()

    def insert_thread_post_count(self, website_id, element_id, element_type):
        args = [element_id, website_id]
        if element_type == ElementType.XPATH:
            query = "UPDATE `FORUM_FIELDS` SET `thread_post_count_xpath`=%s WHERE `website_id` = %s"
        else:
            query = "UPDATE `FORUM_FIELDS` SET `thread_post_count_class`=%s WHERE `website_id` = %s"
        self.__db.query(query, args)
        self.__db.commit()
