from model.base_classes import ElementType


class ThreadFieldsDAO:

    """
    NOTE: Consider yourself warned from the desire of parametrize field_name as happens in website_dao: you can inject
    only parameters and not keywords or so on.

    """
    def __init__(self, db):
        self.__db = db

    def get_field_class_by_website_id(self, website_id, field_name):
        field_name = field_name.lower() + "_class"
        return self.__db.query("SELECT " + field_name + " FROM `THREAD_FIELDS` WHERE `website_id` = %s",
                               website_id).fetchone()[0]

    def get_field_xpath_by_website_id(self, website_id, field_name):
        field_name = field_name.lower() + "_xpath"
        return self.__db.query("SELECT " + field_name + " FROM `THREAD_FIELDS` WHERE `website_id` = %s",
                               website_id).fetchone()[0]

    def insert_thread_next_page_id(self, website_id, element_ids, element_type):
        element_ids_string = ""
        for element_id in element_ids:
            element_ids_string = element_ids_string + element_id + ", "
        element_ids_string = element_ids_string[:-2]
        args = [website_id, element_ids_string]
        if element_type == ElementType.XPATH:
            query = "INSERT INTO `THREAD_FIELDS`(`website_id`, `thread_next_page_xpath`) VALUES (%s, %s)"
        else:
            query = "INSERT INTO `THREAD_FIELDS`(`website_id`, `thread_next_page_class`) VALUES (%s, %s)"
        self.__db.query(query, args)
        self.__db.commit()

    def insert_thread_title_id(self, website_id, element_ids, element_type):
        element_ids_string = ""
        for element_id in element_ids:
            element_ids_string = element_ids_string + element_id + ", "
        element_ids_string = element_ids_string[:-2]
        args = [element_ids_string, website_id]
        if element_type == ElementType.XPATH:
            query = "UPDATE `THREAD_FIELDS` SET `thread_title_xpath` = %s WHERE `website_id` = %s"
        else:
            query = "UPDATE `THREAD_FIELDS` SET `thread_title_class` = %s WHERE `website_id` = %s"
        self.__db.query(query, args)
        self.__db.commit()

    def insert_post_author_id(self, website_id, element_ids, element_type):
        element_ids_string = ""
        for element_id in element_ids:
            element_ids_string = element_ids_string + element_id + ", "
        element_ids_string = element_ids_string[:-2]
        args = [element_ids_string, website_id]
        if element_type == ElementType.XPATH:
            query = "UPDATE `THREAD_FIELDS` SET `author_xpath` = %s WHERE `website_id` = %s"
        else:
            query = "UPDATE `THREAD_FIELDS` SET `author_class` = %s WHERE `website_id` = %s"
        self.__db.query(query, args)
        self.__db.commit()

    def insert_post_count_id(self, website_id, element_ids, element_type):
        element_ids_string = ""
        for element_id in element_ids:
            element_ids_string = element_ids_string + element_id + ", "
        element_ids_string = element_ids_string[:-2]
        args = [element_ids_string, website_id]
        if element_type == ElementType.XPATH:
            query = "UPDATE `THREAD_FIELDS` SET `post_count_xpath` = %s WHERE `website_id` = %s"
        else:
            query = "UPDATE `THREAD_FIELDS` SET `post_count_class` = %s WHERE `website_id` = %s"
        self.__db.query(query, args)
        self.__db.commit()

    def insert_post_text_id(self, website_id, element_ids, element_type):
        element_ids_string = ""
        for element_id in element_ids:
            element_ids_string = element_ids_string + element_id + ", "
        element_ids_string = element_ids_string[:-2]
        args = [element_ids_string, website_id]
        if element_type == ElementType.XPATH:
            query = "UPDATE `THREAD_FIELDS` SET `post_text_xpath` = %s WHERE `website_id` = %s"
        else:
            query = "UPDATE `THREAD_FIELDS` SET `post_text_class` = %s WHERE `website_id` = %s"
        self.__db.query(query, args)
        self.__db.commit()

    def insert_post_date_id(self, website_id, element_ids, element_type):
        element_ids_string = ""
        for element_id in element_ids:
            element_ids_string = element_ids_string + element_id + ", "
        element_ids_string = element_ids_string[:-2]
        args = [element_ids_string, website_id]
        if element_type == ElementType.XPATH:
            query = "UPDATE `THREAD_FIELDS` SET `date_xpath` = %s WHERE `website_id` = %s"
        else:
            query = "UPDATE `THREAD_FIELDS` SET `date_class` = %s WHERE `website_id` = %s"
        self.__db.query(query, args)
        self.__db.commit()

    def insert_post_pool_id(self, website_id, element_ids, element_type):
        element_ids_string = ""
        for element_id in element_ids:
            element_ids_string = element_ids_string + element_id + ", "
        element_ids_string = element_ids_string[:-2]
        args = [element_ids_string, website_id]
        if element_type == ElementType.XPATH:
            query = "UPDATE `THREAD_FIELDS` SET `post_pool_xpath` = %s WHERE `website_id` = %s"
        else:
            query = "UPDATE `THREAD_FIELDS` SET `post_pool_class` = %s WHERE `website_id` = %s"
        self.__db.query(query, args)
        self.__db.commit()
