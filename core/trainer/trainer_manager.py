from time import sleep

from selenium.common.exceptions import InvalidSelectorException

from core.crawler.support_logic.crawl_bootstrapper import CrawlBootstrapper
from core.trainer.support_logic.trainer_functions import TrainerHelper
from database.dao.forum_fields_dao import ForumFieldsDAO
from database.dao.website_dao import WebsiteDAO
from model.base_classes import TrainingStage, ForumField, ElementType
from time_management.reading_stopwatch import wait_simple_pause
from utils.commons import print_successful_status, print_warning


class Trainer:
    """
    This module has the task to create the resource mapping of a new forum, if not known.

    Operates in the following way:
    - Creates a new environment for the training;
    - Downloads the forum landing page;
    - Suppresses all the JS in the page;
    - Injects handlers that will trigger an AJAX request;
    - Starts a server that will receive the AJAX calls triggered from the page, that will allow the server get the
        needed information on the resources;
    - The backend retrieves all the information through MQTT;
    - Shows all the recognized elements in the page;
    - Moves to next kind of resource
    """

    def __init__(self, db, program):
        # The browser has been initialized, so is possible to navigate.
        self.element_xpaths = []
        self.program = program
        self.db = db
        self.trainer_functions = TrainerHelper(program, db)
        self.website_dao = WebsiteDAO(db)
        self.forum_fields_dao = ForumFieldsDAO(db)

    def begin_training(self, forum_landing_page, login_page):
        # Check if the forum's structure is known
        if self.website_dao.get_website_id_by_url(forum_landing_page) is not None:
            print_successful_status("[TRAINER] The forum is known. It is possible to proceed to the crawling.")
        else:
            print_warning("[TRAINER] The forum is not known. Proceeding to the learning phase.")
            self.get_login_page_structure(login_page)

            # Executing login
            CrawlBootstrapper(self.program, self.db, login_page)

            self.get_relevant_forums(forum_landing_page)
            self.get_subforum_structure(forum_landing_page)
            self.get_thread_structure(forum_landing_page)
        return self.website_dao.get_website_id_by_url(forum_landing_page)

    def get_login_page_structure(self, login_page):
        self.trainer_functions.purge_fs()
        self.trainer_functions.download_page(login_page, TrainingStage.LOGIN_PAGE)
        self.trainer_functions.remove_existing_js()
        self.trainer_functions.inject_js_listeners(TrainingStage.LOGIN_PAGE)
        self.trainer_functions.collect_info_and_render_pages(login_page, TrainingStage.LOGIN_PAGE, None, None)

    def get_relevant_forums(self, forum_landing_page):
        self.trainer_functions.purge_fs()
        self.trainer_functions.download_page(forum_landing_page, TrainingStage.FORUM)
        self.trainer_functions.remove_existing_js()
        self.trainer_functions.inject_js_listeners(TrainingStage.FORUM)
        self.element_xpaths = self.trainer_functions.collect_info_and_render_pages(forum_landing_page, TrainingStage.FORUM, None, None)
        for forum_page_xpath in self.element_xpaths:
            """
                WARNING: this sleep is needed for avoiding opening a new page of Firefox before it is actually closed.
                When the analyzed page is being closed, it makes a call to the backend and then popups a confirmation. 
                The confirmation is only for closing Firefox, but the backend is already starting a new Firefox session, 
                resulting in a bad UX.
            """
            sleep(5)  # Let me live pls
            self.program.driver.load_url(forum_landing_page)
            subforum_page = self.program.driver.find_element_by_xpath(forum_page_xpath).get_attribute("href")
            self.get_relevant_subforums(forum_landing_page, subforum_page, forum_page_xpath)

    def get_relevant_subforums(self, forum_landing_page, subforum_page, forum_page_xpath):
        self.trainer_functions.purge_fs()
        self.trainer_functions.download_page(subforum_page, TrainingStage.SUBFORUM)
        self.trainer_functions.remove_existing_js()
        self.trainer_functions.inject_js_listeners(TrainingStage.SUBFORUM)
        self.trainer_functions.collect_info_and_render_pages(forum_landing_page, TrainingStage.SUBFORUM, forum_page_xpath, None)

    # TODO stay on the current page instead of going back from the beginning
    def get_subforum_structure(self, forum_landing_page):
        """
            WARNING: this sleep is needed for avoiding opening a new page of Firefox before it is actually closed.
            When the analyzed page is being closed, it makes a call to the backend and then popups a confirmation.
            The confirmation is only for closing Firefox, but the backend is already starting a new Firefox session,
            resulting in a bad UX.
        """
        sleep(5)  # Let me live pls
        self.program.driver.load_url(forum_landing_page)
        forum_xpath = self.website_dao.get_forum_xpaths_by_url(forum_landing_page)[0]
        subforum_xpath = self.website_dao.get_subforum_xpaths_by_url_and_parent_xpath(forum_landing_page, forum_xpath)[0]

        url_with_threads = self.program.driver.find_element_by_xpath(forum_xpath).get_attribute("href")
        wait_simple_pause()
        self.program.driver.click(self.program.driver.find_element_by_xpath(forum_xpath))

        if subforum_xpath != "" and subforum_xpath is not None:
            url_with_threads = self.program.driver.find_element_by_xpath(subforum_xpath).get_attribute("href")
            wait_simple_pause()
            self.program.driver.click(self.program.driver.find_element_by_xpath(subforum_xpath))

        self.trainer_functions.purge_fs()
        self.trainer_functions.download_page(url_with_threads, TrainingStage.THREAD_POOL)
        self.trainer_functions.remove_existing_js()
        self.trainer_functions.inject_js_listeners(TrainingStage.THREAD_POOL)
        self.trainer_functions.collect_info_and_render_pages(url_with_threads, TrainingStage.THREAD_POOL, None,
                                                             None)

        sleep(3)
        self.trainer_functions.create_content_collector_page(TrainingStage.THREAD_POST_COUNT)
        self.trainer_functions.inject_js_listeners(TrainingStage.THREAD_POST_COUNT)
        self.trainer_functions.collect_info_and_render_pages(url_with_threads, TrainingStage.THREAD_POST_COUNT,
                                                             None, None)

        """
        WARNING: this sleep is needed for avoiding opening a new page of Firefox before it is actually closed.
        When the analyzed page is being closed, it makes a call to the backend and then popups a confirmation. 
        The confirmation is only for closing Firefox, but the backend is already starting a new Firefox session, 
        resulting in a bad UX.
        """
        sleep(3)  # Let me live pls
        self.trainer_functions.inject_js_listeners(TrainingStage.SUBFORUM_NEXT_PAGE)
        self.trainer_functions.collect_info_and_render_pages(url_with_threads, TrainingStage.SUBFORUM_NEXT_PAGE,
                                                             None, None)

    # TODO stay on the current page instead of going back from the beginning
    def get_thread_structure(self, forum_landing_page):

        wait_simple_pause()
        self.program.driver.load_url(forum_landing_page)

        forum_xpath = self.website_dao.get_forum_xpaths_by_url(forum_landing_page)[0]
        subforum_xpath = self.website_dao.get_subforum_xpaths_by_url_and_parent_xpath(forum_landing_page, forum_xpath)[0]
        website_id = self.website_dao.get_website_id_by_url(forum_landing_page)
        thread_pool_xpath = self.forum_fields_dao.get_field_xpath_by_website_id(website_id, ForumField.THREAD_POOL.name)

        wait_simple_pause()
        self.program.driver.click(self.program.driver.find_element_by_xpath(forum_xpath))
        if subforum_xpath != "" and subforum_xpath is not None:
            wait_simple_pause()
            self.program.driver.click(self.program.driver.find_element_by_xpath(subforum_xpath))
        # Picking up the first thread
        thread_page_element = self.program.driver.find_elements_by_xpath(thread_pool_xpath)[0]
        thread_page_url = thread_page_element.get_attribute("href")
        wait_simple_pause()
        self.program.driver.click(thread_page_element)

        self.trainer_functions.purge_fs()
        self.trainer_functions.download_page(thread_page_url, TrainingStage.THREAD_NEXT_PAGE)
        self.trainer_functions.remove_existing_js()

        self.trainer_functions.inject_js_listeners(TrainingStage.THREAD_NEXT_PAGE)
        try:
            next_thread_page_identifier = self.trainer_functions.collect_info_and_render_pages(
                thread_page_url, TrainingStage.THREAD_NEXT_PAGE, None, None)[0]
            sleep(3)

            ## Check for second page in section. This is needed whereas the forum is a PhpBB, MyBB or VBulletin.
            try:
                element_list = self.program.driver.find_elements_by_xpath(next_thread_page_identifier)
                element_type = ElementType.XPATH
            except InvalidSelectorException:
                element_list = []
            if len(element_list) == 0:
                next_thread_page_identifier = next_thread_page_identifier.replace(" ", ".")
                element_list = self.program.driver.find_elements_by_class_name(next_thread_page_identifier)
                element_type = ElementType.CLASS
            self.program.driver.click(element_list[0])
            next_thread_page_url = self.program.driver.current_url
            self.trainer_functions.purge_fs()
            self.trainer_functions.download_page(next_thread_page_url, TrainingStage.THREAD_NEXT_PAGE2)
            self.trainer_functions.remove_existing_js()

            self.trainer_functions.render_element_identifiers_and_collect_answers(forum_landing_page, TrainingStage.THREAD_NEXT_PAGE2, None, None, next_thread_page_identifier)
            sleep(3)
        except InvalidSelectorException:
            # TODO trovare un altro posto dove andare, qui non c'e' probabilmente il next button da premere
            pass
            
        ##################
        # The listeners injected in these fields are completely different,
        # so the page must be downloaded again in order to recreate a proper set of them.
        ##################

        self.trainer_functions.purge_fs()
        self.trainer_functions.download_page(thread_page_url, TrainingStage.THREAD_STRUCTURE)
        self.trainer_functions.remove_existing_js()

        post_xpath = self.collect_post_info(TrainingStage.POST_POOL, thread_page_url, None)
        post_xpath = post_xpath[0]  # It is returned as a vector, but we need only the XPath
        self.collect_post_info(TrainingStage.THREAD_TITLE, thread_page_url, None)
        self.collect_post_info(TrainingStage.POST_AUTHOR, thread_page_url, post_xpath)
        self.collect_post_info(TrainingStage.POST_COUNT, thread_page_url, post_xpath)
        self.collect_post_info(TrainingStage.POST_CONTENT, thread_page_url, post_xpath)
        self.collect_post_info(TrainingStage.POST_DATE, thread_page_url, post_xpath)

    def collect_post_info(self, training_stage, current_page, parent_element_xpath):

        if parent_element_xpath is None:
            parent_element_xpath = ""
        self.trainer_functions.create_content_collector_page(training_stage)
        self.trainer_functions.inject_js_listeners(training_stage)
        element_xpath = self.trainer_functions.collect_info_and_render_pages(
            current_page, training_stage, "", parent_element_xpath)
        sleep(3)
        return element_xpath
