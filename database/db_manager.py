import database.db_helper


class DBManager:

    """
    Allows to return the same DB instance to different callee.
    """
    def __init__(self):
        self.db = database.db_helper.DbHelper()

    def get_instance(self):
        return self.db

