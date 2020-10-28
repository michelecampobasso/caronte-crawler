import MySQLdb
import pymysql.cursors
import pymysql
from database.config import config
from utils.commons import *


class DbHelper:

    __connection = None
    __cursor = None

    """
    Manages the creation of a DB instance.
    """
    def __init__(self):
        print_warning("[BOOTSTRAP] Attempting to establish connection to database...")
        try:
            __db_config = config["mysql"]
            self.__connection = pymysql.connect(host=__db_config['host'],
                                                user=__db_config['user'],
                                                port=__db_config['port'],
                                                password=__db_config['password'],
                                                db=__db_config['db'],
                                                charset='utf8',
                                                use_unicode=True)
            self.__cursor = self.__connection.cursor()
            print_successful_status("[BOOTSTRAP] ...successful.")
        except Exception:
            print_error_and_exit("[BOOTSTRAP] Problems parsing the JSON or reaching the DB. Aborting...")

    def query(self, query, params):
        try:
            self.__cursor.execute(query, params)
        except MySQLdb.Warning:
            pass
        return self.__cursor

    def commit(self):
        self.__connection.commit()

    def get_last_website_id(self):
        return self.query("SELECT MAX(`website_id`) FROM `LOGIN_FIELDS`", []).fetchone()

    def close(self):
        self.__connection.close()

