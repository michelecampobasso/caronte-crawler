from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException
from time import sleep
from itertools import izip
import datetime

from database.dao.forum_fields_dao import ForumFieldsDAO
from database.dao.post_dump_dao import PostDumpDAO
from database.dao.thread_list_dao import ThreadListDAO
from database.dao.website_dao import WebsiteDAO
from database.dao.thread_fields_dao import ThreadFieldsDAO
from model.base_classes import ThreadField, ForumField
from time_management.reading_stopwatch import wait_simple_pause, wait_to_read
from utils.commons import print_warning, print_error, print_error_and_exception


class Dumper:

    """
    This class has the core task of dumping the content of a certain forum, using an already logged in session.

    @param db: an instance of the database;
    @param program: the container of the tor process and the tbselenium driver;
    @param landing_page: a string representing the forum homepage url;
    @param website_id: the identifier of the current website.
    """
    def __init__(self, db, program, landing_page, website_id):
        self.forum_fields_dao = ForumFieldsDAO(db)
        self.website_dao = WebsiteDAO(db)
        self.thread_fields_dao = ThreadFieldsDAO(db)
        self.post_dumps_dao = PostDumpDAO(db)
        self.thread_list_dao = ThreadListDAO(db)
        self.program = program
        self.landing_page = landing_page
        self.website_id = website_id

    """
    This function has the task of iterate through all the forums and subforums. For each subforum page reached, it
    invokes the iterate_threads function.  
    """
    def dump_procedure(self):
        print_warning("[CRAWLER] Beginning dump procedure.")
        print_warning("[CRAWLER] Reaching forum landing page.")
        sleep(1)

        '''
        Could be interesting thinking about how make this flexible to xpaths, ids and partial names. 
        An option could we working with "generic finders" that specialize in front of the informations given from the
        database. The DB should then qualify the property exposed, so that the code can invoke the correct function.

        Moreover, a proper try except structure can be useful to address both the problems connected to a new page 
        structure and for test purposes in training phase. 
        '''

        # TODO replace all load_url with click or different actions. load_url doesn't provide referral link.
        # Iterate forums
        cookie_value = "CARONTE" + str(int((datetime.datetime.today() - datetime.datetime(1970, 1, 1)).total_seconds()))
        for forum_xpath in self.website_dao.get_forum_xpaths_by_url(self.landing_page):
            wait_simple_pause()
            self.program.driver.load_url(self.landing_page)
            # Retrieving forum link for navigation
            forum_element = self.program.driver.find_element_by_xpath(forum_xpath)
            forum_link = forum_element.get_attribute("href")

            subforums = self.website_dao.get_subforum_xpaths_by_url_and_parent_xpath(self.landing_page, forum_xpath)
            # Subforums might be not present but directly posts
            if subforums is None or subforums[0] == '' or subforums[0] is None:
                wait_simple_pause()
                self.program.driver.click(forum_element)
                self.iterate_threads(forum_link)
            else:
                # Iterate subforums
                for subforum_xpath in subforums:
                    wait_simple_pause()
                    self.program.driver.load_url(forum_link)
                    # Retrieving subforum link for navigation
                    subforum_element = self.program.driver.find_element_by_xpath(subforum_xpath)
                    subforum_link = subforum_element.get_attribute("href")
                    wait_simple_pause()
                    self.program.driver.click(subforum_element)
                    self.iterate_threads(subforum_link)

    """
    This function iterates all the threads available in a certain forum or subforum. If threads in the current page
    run off, then it moves to the next page. For each thread identified, it runs crawl_current_thread.
    
    @param subforum_link: string representing the current forum/subforum page.
    """

    # TODO Really needs to raise exception for executing a break? Or there's other cases where it is raised?
    def iterate_threads(self, subforum_link):
        print_warning("[CRAWLER] Starting to read threads on page...")
        scanned_threads = []
        first_page = True
        while True:
            # If all threads of the page have been scanned, move to next page
            thread_pool = self.get_forum_subelements(ForumField.THREAD_POOL, self.program.driver)
            if scanned_threads.__len__() == thread_pool.__len__():
                scanned_threads = []
                # Try to reach next page, if any.
                try:
                    # vBulletin handles next pages differently compared to other forums. In particular, uses the same
                    # tag and class to define the button of the next page, plus XPATH is not exploitable due the fact
                    # it varies depending on thread length.

                    if self.website_dao.get_is_vbullettin_by_website_id(self.website_id):
                        prev_next_elements = self.get_forum_subelements(
                            ForumField.SUBFORUM_NEXT_PAGE, self.program.driver)

                        # If there is 4 navigation buttons (2 on top page, 2 on bottom page), or is the first page,
                        # then there's a next page...
                        try:
                            if prev_next_elements.__len__() == 4 or (prev_next_elements.__len__() == 2 and first_page):
                                first_page = False
                                subforum_link = prev_next_elements[1].get_attribute("href")
                                if subforum_link is None:
                                    # Terrible, but should be worth it: if the current item has not the link,
                                    # it will likely be present in children. For this reason, I iterate on them until
                                    # I don't find the proper link.
                                    for child in prev_next_elements[1].find_elements_by_xpath(".//*"):
                                        subforum_link = child.get_attribute("href")
                                        # Found it!
                                        if subforum_link != "" or not None:
                                            break
                                        # If I reach the end of for cycle, then there's a problem.
                                        raise NoSuchElementException
                                self.program.driver.click(prev_next_elements[1])
                            # ...else, could be or a first or a last page.
                            else:
                                raise NoSuchElementException
                        except AttributeError:
                            raise NoSuchElementException
                    else:
                        first_page = False
                        subforum_next_page = self.get_forum_subelement(ForumField.SUBFORUM_NEXT_PAGE,
                                                                       self.program.driver)
                        if subforum_next_page is None:
                            raise NoSuchElementException
                        else:
                            subforum_link = subforum_next_page.get_attribute("href")
                            if subforum_link is None:
                                # Terrible, but should be worth it: if the current item has not the link, it will
                                # likely be present in children. For this reason, I iterate on them until I don't find
                                # the proper link.
                                for child in subforum_next_page.find_elements_by_xpath(".//*"):
                                    subforum_link = child.get_attribute("href")
                                    # Found it!
                                    if subforum_link != "" or not None:
                                        break
                                    # If I reach the end of for cycle, then there's a problem.
                                    raise NoSuchElementException
                            self.program.driver.click(subforum_next_page)
                except NoSuchElementException:
                    break
            else:
                # Scan next thread
                for thread, thread_post_count_by_browser in izip(
                    self.get_forum_subelements(ForumField.THREAD_POOL, self.program.driver),
                        self.get_forum_subelements(ForumField.THREAD_POST_COUNT, self.program.driver)):
                    thread_post_count_by_browser_text = thread_post_count_by_browser.get_attribute("text")
                    if thread_post_count_by_browser_text is None:
                        thread_post_count_by_browser_text = thread_post_count_by_browser.text
                    thread_post_count_by_browser = filter(unicode.isdigit, thread_post_count_by_browser_text)
                    thread_link = thread.get_attribute("href")
                    if thread_link not in scanned_threads:
                        scanned_threads.append(thread_link)
                        do_i_have_to_scan_it = True
                        has_ever_been_scanned = self.thread_list_dao.has_ever_been_scanned(thread_link)
                        if has_ever_been_scanned:
                            thread_post_count_by_db = str(self.thread_list_dao.get_post_count_by_thread_url(thread_link))
                            # The thread will count as scanned, whether will be carved or not, depending on post count.
                            if thread_post_count_by_db == thread_post_count_by_browser:
                                do_i_have_to_scan_it = False
                                print_warning("[CRAWLER] I already know thread " + thread_link + " and I've collected "
                                              "all the " + thread_post_count_by_browser + " posts in it. Skipped.")
                        # The condition to satisfy is: has never been scanned or it has been scanned but different
                        # post count.
                        if do_i_have_to_scan_it:
                            wait_simple_pause()
                            self.program.driver.click(thread)
                            # Begin thread crawling
                            self.crawl_current_thread(thread_link, False)
                            # Taking note of current amount of posts
                            if has_ever_been_scanned:
                                self.thread_list_dao.update_post_count(thread_link, thread_post_count_by_browser)
                            else:
                                self.thread_list_dao.insert_post_count(thread_link, thread_post_count_by_browser)

                            # Done carving current thread, move on next going back to subforum
                            self.program.driver.load_url(subforum_link)
                            break  # I need to exit the for loop since elements aren't anymore connected to the DOM


    """
    This function iterates all the posts inside of a thread and moves through the pages. For each post, carves its 
    content and saves it in the DB.
    
    @param thread_link: a string representing the current thread to dump;
    @param is_second_try: specifies if it's the second attempt to dump this thread. This parameter is true only if there
                          was a previous fail that could be fatal. In that case, the dump will proceed from the current
                          page and 
    """
    def crawl_current_thread(self, thread_link, is_second_try):
        # Thread crawl
        # This is needed for carving vbulletin threads, in order to tear apart first and last pages.
        print_warning("[CRAWLER] Starting to read posts on page...")
        try:
            # TODO use is_second_try for refreshing the page and continue the parsing from there
            first_page = True
            thread_name = self.get_element_text(self.get_thread_subelements(ThreadField.THREAD_TITLE, self.program.driver)[0])
            while True:
                for thread_post in self.get_thread_subelements(ThreadField.POST_POOL, self.program.driver):
                    # Post carving
                    try:
                        post_text = self.get_element_text(self.get_thread_subelement(ThreadField.POST_TEXT, thread_post))
                        date = self.get_element_text(self.get_thread_subelement(ThreadField.DATE, thread_post))
                        author = self.get_element_text(self.get_thread_subelement(ThreadField.AUTHOR, thread_post))
                        post_count = self.get_element_text(self.get_thread_subelement(ThreadField.POST_COUNT, thread_post))
                        if not self.post_dumps_dao.check_if_post_dump_exists(self.website_id, thread_link, thread_name,
                                                                             author, date, post_count, post_text):
                            # TODO wait longer for the first post (50wpm)
                            self.post_dumps_dao.insert_post_dump(self.website_id, thread_link, thread_name, author,
                                                                 date, post_count, post_text)
                            wait_to_read(post_text)

                    except StaleElementReferenceException as e:
                        if not is_second_try:
                            sleep(1)
                            self.crawl_current_thread(thread_link, True)
                        else:
                            # This could be more worrying, but could also depend from a problem in the DOM of the page.
                            print_error_and_exception("[CRAWLER] Exception thrown. Might be a potential failure of "
                                                      "the carving.", e)
                            print_warning("[CRAWLER] I'm reloading the page...")
                            self.program.driver.load_url(thread_link)

                wait_simple_pause()
                # Try to reach next page of the thread, if any
                try:
                    # vBulletin handles next pages differently compared to other forums. In particular, uses the same
                    # tag and class to define the button of the next page, plus XPATH is not exploitable due the fact
                    # it varies depending on thread length.

                    if self.website_dao.get_is_vbullettin_by_website_id(self.website_id):
                        prev_next_elements = self.get_thread_subelements(ThreadField.THREAD_NEXT_PAGE, self.program.driver)
                        # If there is 4 navigation buttons (2 on top page, 2 on bottom page), or is the first page,
                        # then there's a next page...
                        if prev_next_elements.__len__() == 4 or (prev_next_elements.__len__() == 2 and first_page):
                            first_page = False
                            self.program.driver.click(prev_next_elements[1])
                        # ...else, could be or a first or a last page.
                        else:
                            raise NoSuchElementException
                    else:
                        first_page = False
                        thread_next_page = self.get_thread_subelement(ThreadField.THREAD_NEXT_PAGE, self.program.driver)
                        if thread_next_page is None:
                            raise NoSuchElementException
                        else:
                            try:
                                self.program.driver.click(thread_next_page)
                            #### TODO WORKAROUND PER OFFENSIVE COMMUNITY
                            #### C'E' UNA ROBA NASCOSTA CHE CONTIENE LINK NON CORRETTI
                            except ElementNotInteractableException:
                                thread_next_page = self.get_thread_subelements(ThreadField.THREAD_NEXT_PAGE,
                                                                               self.program.driver)[1]
                                self.program.driver.click(thread_next_page)
                except NoSuchElementException:
                    break

            sleep(1)
        except (IndexError, TypeError) as e:
            if not is_second_try:
                sleep(1)
                self.crawl_current_thread(thread_link, True)
            else:
                print_error_and_exception("[CRAWLER] Exception thrown. Might be a potential failure of the carving.", e)

    """
    This function is an interface with the ForumFieldsDAO that allows to retrieve all required elements by template id
    both searching them by class name or by XPath.
    
    @param field_required: the name of the required field;
    @param element: the parent webelement where to search them. 
    """
    def get_forum_subelements(self, field_required, element):

        try:
            return element.find_elements_by_class_name(
                self.forum_fields_dao.get_field_class_by_website_id(self.website_id, field_required.name))
        except NoSuchElementException:
            try:
                return element.find_elements_by_xpath(
                    self.forum_fields_dao.get_field_xpath_by_website_id(self.website_id, field_required.name))
            except NoSuchElementException:
                print_error("[CRAWLER] Field not found. Website structure has changed?")

    """
    This function is an interface with the ForumFieldsDAO that allows to retrieve a single element by template id
    both searching them by class name or by XPath.
    
    @param field_required: the name of the required field;
    @param element: the parent webelement where to search them.
    """
    def get_forum_subelement(self, field_required, element):

        try:
            return self.get_forum_subelements(field_required, element)[0]
        except (IndexError, TypeError) as e:
            # This is a simple catch for lack of informations in some fields. If many occur
            # might be significant of bad structure.
            if e.message is None:
                print_error_and_exception("[CRAWLER] Exception thrown.", e)
            return None

    """
    This function is an interface with the ThreadFieldsDAO that allows to retrieve all required elements by template id
    both searching them by class name or by XPath.

    @param field_required: the name of the required field;
    @param element: the parent webelement where to search them. 
    """
    def get_thread_subelements(self, field_required, element):

        try:
            return element.find_elements_by_class_name(
                self.thread_fields_dao.get_field_class_by_website_id(self.website_id, field_required.name))
        except NoSuchElementException:
            try:
                return element.find_elements_by_xpath(
                    self.thread_fields_dao.get_field_xpath_by_website_id(self.website_id, field_required.name))
            except NoSuchElementException:
                print_error("[CRAWLER] Field not found. Website structure has changed?")

    """
    This function is an interface with the ThreadFieldsDAO that allows to retrieve a single element by template id
    both searching them by class name or by XPath.

    @param field_required: the name of the required field;
    @param element: the parent webelement where to search them.
    """
    def get_thread_subelement(self, field_required, element):

        try:
            return self.get_thread_subelements(field_required, element)[0]
        except (IndexError, TypeError) as e:
            # This is a simple catch for lack of informations in some fields. If many occur
            # might be significant of bad structure.
            if e.message is None:
                print_error_and_exception("[CRAWLER] Exception thrown.", e)
            return None

    """
    This function allows to retrieve the text of a certain webelement.
    """
    def get_element_text(self, element):

        try:
            return element.text
        except AttributeError:
            return ""
