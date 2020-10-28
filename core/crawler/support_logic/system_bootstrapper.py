from time import sleep

from psutil import NoSuchProcess
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, TimeoutException, \
    StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
from tbselenium.exceptions import TBDriverPortError
from tbselenium.tbdriver import TorBrowserDriver
from subprocess import Popen
from utils.commons import *
import psutil


class SystemBootstrapper:

    """
    This class cleans up the environment, creates the tbselenium driver and runs tor process
    """
    def __init__(self):

        self.purge_dangling_processes()
        sleep(3)
        # WARNING! This doesn't disable JavaScript totally, also with the use of NoScript. Instead, is necessary to edit
        # the file venv2/lib/python2.7/site-packages/selenium/webdriver/firefox/webdriver_prefs.json
        # and to manually set javascript.enabled = false
        #
        # self.driver = TorBrowserDriver("/home/user/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US",
        #                                pref_dict={'javascript.enabled': False})
        try:
            self.driver = TorBrowserDriverWithTimeoutHandler()
        except TBDriverPortError:
            print_warning("Tor process still running. Trying to kill it again...")
            self.purge_dangling_processes()
            self.driver = TorBrowserDriverWithTimeoutHandler()
        self.torprocess = self.bootstrap_protocol()

    """
    Starts tor and checks if JavaScript is disabled.
    
    @return: pointer to the tor process.
    """
    def bootstrap_protocol(self):

        url = "https://check.torproject.org"
        p = Popen(['tor', '--SocksPort', '9150'])  # something long running
        sleep(5)
        self.driver.load_url(url)
        status = self.driver.find_element_by("h1.on").text  # status text
        if "Congratulations" not in status:
            print_error_and_exit("[BOOTSTRAP] Not connected to TOR network, aborting...")
        else:
            print_successful_status("[BOOTSTRAP] Connected to TOR!")

        try:
            if self.driver.find_element_by_partial_link_text("JavaScript is enabled.") is not None:
                print_error_and_exit("[BOOTSTRAP] JavaScript is enabled! This tool doesn't provide secure crawling if "
                                     "JavaScript is enabled! Aborting...")
        except NoSuchElementException:
            print_successful_status("[BOOTSTRAP] Javascript is disabled. Is possible to proceed safely.")
        return p

    """
    Kills both tbselenium driver and tor process.
    """
    def shutdown_protocol(self):

        # TODO carefully evaluate if is a good idea to close tor on error or keep it open.
        try:
            self.torprocess.terminate()
            self.driver.close()
        # Browser could have been already closed; if happens, is fine.
        except SessionNotCreatedException:
            pass

    """
    Kills all pending processes that could conflict with Caronte's execution.
    """
    def purge_dangling_processes(self):

        try:
            for proc in psutil.process_iter():
                # check whether the process name matches
                if proc.name() == 'tor':
                    proc.kill()
                if proc.name() == 'geckodriver':
                    proc.kill()
                if proc.name() == 'firefox.real':
                    proc.kill()
        except NoSuchProcess:
            pass


class TorBrowserDriverWithTimeoutHandler(TorBrowserDriver):

    def __init__(self):
        self._default_timeout = 15
        # self._default_timeout = 1
        TorBrowserDriver.__init__(self, "/home/user/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US")
        self.set_page_load_timeout(self._default_timeout)

    def load_url(self, url, wait_on_page=0, wait_for_page_body=False, is_retry=False):
        try:
            if is_retry:
                self.set_page_load_timeout(self._default_timeout * 2)
            super(TorBrowserDriverWithTimeoutHandler, self).load_url(url)
        except TimeoutException:
            self.load_url(url, is_retry=True)
            self.set_page_load_timeout(self._default_timeout)

    def click(self, element, is_retry=False):
        try:
            if is_retry:
                self.set_page_load_timeout(self._default_timeout * 2)
            element.click()
        except TimeoutException:
            self.click(element, True)
            self.set_page_load_timeout(self._default_timeout)
        except StaleElementReferenceException:
            # print element
            pass
