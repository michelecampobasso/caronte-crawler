class LoginFieldsDAO:

    def __init__(self, db):
        self.__db = db

    def get_sign_in_xpath_by_website_id(self, website_id):
        return self.__db.query(
            "SELECT signin_xpath FROM `LOGIN_FIELDS` WHERE `website_id` = %s",
            website_id).fetchone()[0]

    def get_username_xpath_by_website_id(self, website_id):
        return self.__db.query(
            "SELECT username_xpath FROM `LOGIN_FIELDS` WHERE `website_id` = %s",
            website_id).fetchone()[0]

    def get_password_xpath_by_website_id(self, website_id):
        return self.__db.query(
            "SELECT password_xpath FROM `LOGIN_FIELDS` WHERE `website_id` = %s",
            website_id).fetchone()[0]

    def get_login_xpath_by_website_id(self, website_id):
        return self.__db.query(
            "SELECT login_xpath FROM `LOGIN_FIELDS` WHERE `website_id` = %s",
            website_id).fetchone()[0]

    def insert_login_xpaths(self, params):
        self.__db.query(
            "INSERT INTO `LOGIN_FIELDS`(`username_xpath`, `password_xpath`, `login_xpath`) VALUES (%s, %s, %s)", params)
        self.__db.commit()





