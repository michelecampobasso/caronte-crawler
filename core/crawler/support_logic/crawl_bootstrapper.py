from selenium.common.exceptions import NoSuchElementException

from database.dao.login_fields_dao import LoginFieldsDAO
from time import sleep

from database.dao.website_dao import WebsiteDAO
from core.crawler.support_logic.credential_manager import retrieve_creds
from utils.commons import *


class CrawlBootstrapper:

    """
    This class executes the login.

    @param program: the container of the tor process and the tbselenium driver;
    @param db: an instance of the database;
    @param login_page: a string representing the login url.
    """
    def __init__(self, program, db, login_page):
        self.login_fields_dao = LoginFieldsDAO(db)
        self.website_dao = WebsiteDAO(db)
        self.website_id = db.get_last_website_id()
        # TODO if not, run the trainer!
        self.initialize_session(program, login_page)

    """
    Bootstraps the crawler, reaching the login page and executing it.
    
    @param program: the container for the tor process and the tbselenium driver;
    @param login_url: a string representing the login url.
    """
    def initialize_session(self, program, login_url):
        print_warning("[BOOTSTRAP] Reaching the login page...")
        program.driver.load_url(login_url)
        print_successful_status("[BOOTSTRAP] Done.")
        self.execute_login(program)

    """
    A function that executes the login on the specified page.
    
    @param program: the container for the tor process and the tbselenium driver
    """
    def execute_login(self, program):
        print_warning("[BOOTSTRAP] Attempting to execute login...")
        creds = retrieve_creds()
        program.driver.find_element_by_xpath(self.login_fields_dao.get_username_xpath_by_website_id(
            self.website_id)).send_keys(creds.u)
        program.driver.find_element_by_xpath(self.login_fields_dao.get_password_xpath_by_website_id(
            self.website_id)).send_keys(creds.p)
        program.driver.click(program.driver.find_element_by_xpath(self.login_fields_dao.get_login_xpath_by_website_id(
            self.website_id)))
        sleep(3)
        try:
            program.driver.find_element_by_link_text(creds.u)
        except NoSuchElementException as e:
            # TODO [BUG] Doesn't work, at least in PyCharm
            '''
            print_error("Login might be unsuccessful. Should we continue? (Y/N)")
            answer = ""
            while answer is not "Y" or "N":
                stdin.read()
                if answer == "Y":
                    break
                else:
                    if answer == "N":
                        print_error_and_exit("Login unsuccessful. Aborting...")
                    else:
                        print_warning("Choose Y or N.")
            '''
            print_error("[BOOTSTRAP] Login might be unsuccessful. I consider your're aware of this.")
        print_successful_status("[BOOTSTRAP] Login successful!")

