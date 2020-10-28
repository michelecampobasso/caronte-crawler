import commands
import json
from time import sleep
from subprocess import Popen
import os

import pyautogui
import re
import pymsgbox

from core.trainer.support_logic.trainer_support_functions import ElementRetriever
from core.trainer.helpers.http_request_listener import HTTPRequestListener
from database.dao.forum_fields_dao import ForumFieldsDAO
from database.dao.login_fields_dao import LoginFieldsDAO
from database.dao.thread_fields_dao import ThreadFieldsDAO
from database.dao.website_dao import WebsiteDAO
from helpers.message_dispatcher import MessageDispatcher
from model.base_classes import TrainingStage, ElementType
from utils.commons import print_warning, print_successful_status, print_error_and_exit, print_internals


class TrainerHelper:

    def __init__(self, program, db):

        self.program = program
        self.element_names_received = ""
        self.element_xpaths = []
        self.structure_analyzers = ElementRetriever(program)
        self.db = db
        self.website_id = self.db.get_last_website_id()

        self.login_fields_dao = LoginFieldsDAO(db)
        self.forum_fields_dao = ForumFieldsDAO(db)
        self.website_dao = WebsiteDAO(db)
        self.thread_fields_dao = ThreadFieldsDAO(db)

        # TODO put this somewhere as an helper
        self.ROOT_DIR = os.path.join(
            os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."), ".."), "..")

    '''
    This function removes all the temporary files created in previous training phases.
    '''

    def purge_fs(self):

        if os.path.exists("/tmp/dump.html"):
            os.remove("/tmp/dump.html")
        if os.path.exists("/tmp/no_js_dump.html"):
            os.remove("/tmp/no_js_dump.html")
        if os.path.exists("/tmp/clean_dump.html"):
            os.remove("/tmp/clean_dump.html")

    '''
    This function allows to download a full page, with images, CSS and JavaScript. 
    
    @param page: this is the url of the page to be downloaded.
    @param is_first_time: specifies if it is the first time that the module has been used for downloading a page.
                          This is done since the browser remembers the previous preference while downloading a document,
                          like opening or saving.
    '''

    def download_page(self, page, training_stage):

        print_warning("[TRAINER] Opening page...")
        self.program.driver.load_url(page)
        self.program.driver.switch_to.window(self.program.driver.window_handles[0])

        print_warning("[TRAINER] Downloading page...")
        pyautogui.hotkey('CTRL', '0')
        # TODO try to find a more efficient way to do it...
        sleep(16)
        '''if training_stage == TrainingStage.LOGIN_PAGE:
            pyautogui.hotkey('DOWN', 'ENTER')
        # Browser remembers about previously chosen action - save and not open
        else:
            pyautogui.hotkey('ENTER')'''

        # TODO FIX THIS
        if commands.getoutput("xset q | grep LED | awk '{print $10}' | cut -b 8") == 1:
            print "CAPS Enabled"
            pyautogui.press('CAPSLOCK')
            if commands.getoutput("xset q | grep LED | awk '{print $10}' | cut -b 8") == 1:
                print "CAPS STILL ENABLED"
        pyautogui.hotkey('ENTER')
        sleep(1)
        pyautogui.keyDown('shift')
        pyautogui.typewrite('7')
        pyautogui.keyUp('shift')
        pyautogui.typewrite("tmp")
        pyautogui.keyDown('shift')
        pyautogui.typewrite('7')
        pyautogui.keyUp('shift')
        pyautogui.typewrite("dump")
        pyautogui.hotkey('ENTER')
        sleep(2)
        print_successful_status("[TRAINER] ...done!")

    '''
    This function removes all the JS contained in the page.
    '''
    def remove_existing_js(self):
        print_warning("[TRAINER] Purging JS content from page...")
        with open("/tmp/dump.html") as oldfile, open("/tmp/no_js_dump.html", 'w') as newfile:
            script_open_tag = False
            for line in oldfile:
                pattern = re.compile("<script.*</script>")
                # This line is a an oneliner script?
                if pattern.match(line):
                    # It is
                    line = re.sub("<script.*/script>", "", line)
                    # It is just an oneliner or there's something left?
                    if line is not "":
                        # There's something left. Lets write it on the file.
                        newfile.write(line)
                    # else, it is just script and i can skip it.
                else:
                    # The line is not an oneliner script.
                    pattern = re.compile("<script.*")
                    # Begin of a multiliner?
                    if pattern.match(line):
                        # Yes it is
                        script_open_tag = True
                        line = re.sub("<script.*>", "", line)
                        # It is just starting or there's also something before?
                        if line is not "":
                            # There's something left. Lets write it on the file.
                            newfile.write(line)
                        # else, it is just starting and i can skip it
                    else:
                        pattern = re.compile(".*</script>")
                        # End of a multiliner?
                        if pattern.match(line):
                            script_open_tag = False
                            line = re.sub("<script.*/script>", "", line)
                            # There's something left?
                            if line is not "":
                                # Lets write it on the file.
                                newfile.write(line)
                        # Outside of a multiliner?
                        elif not script_open_tag:
                            newfile.write(line)
                        # else inside of a multiliner, skipping

    '''
    Create page 
    '''

    # TODO: maybe I could use some parametrized template...
    def create_content_collector_page(self, training_stage):

        with open("/tmp/content_collector.html", 'w') as newfile:
            http_request = ""
            field_text = ""
            name_field = ""
            if training_stage == TrainingStage.THREAD_TITLE:
                http_request = "http://localhost:8080/thread_title"
                field_text = "Thread name: "
                name_field = "thread_name"
            if training_stage == TrainingStage.POST_CONTENT:
                http_request = "http://localhost:8080/post_content"
                field_text = "Post content: "
                name_field = "post_content"
            if training_stage == TrainingStage.POST_DATE:
                http_request = "http://localhost:8080/post_date"
                field_text = "Post date: "
                name_field = "post_date"
            if training_stage == TrainingStage.POST_AUTHOR:
                http_request = "http://localhost:8080/post_author"
                field_text = "Post author: "
                name_field = "post_author"
            if training_stage == TrainingStage.POST_COUNT:
                http_request = "http://localhost:8080/post_count"
                field_text = "Post count: "
                name_field = "post_count"
            if training_stage == TrainingStage.POST_POOL:
                http_request = "http://localhost:8080/post_pool"
                field_text = "Post content: "
                name_field = "post_content"
            if training_stage == TrainingStage.THREAD_POST_COUNT:
                http_request = "http://localhost:8080/thread_post_count"
                field_text = "Thread post count: "
                name_field = "thread_post_count"

            page_source = "<!DOCTYPE html><html><body><h1>Paste in the appropriate fields some snippets " \
                          "copied from the page.</h1><h2> i.e.: for \"Post content\", paste in the specified " \
                          "field a snippet containing some text from inside of a post, <b>being careful not to paste " \
                          "content that is used in other fields, such as the title.</b></h2><form action=\"" + \
                          http_request + "\" method=\"post\">"

            # Multiple data required
            if (training_stage == TrainingStage.POST_DATE) or (training_stage == TrainingStage.POST_CONTENT) or (
                    training_stage == TrainingStage.POST_COUNT) or (training_stage == TrainingStage.POST_AUTHOR) or (
                    training_stage == TrainingStage.POST_POOL) or (training_stage == TrainingStage.THREAD_POST_COUNT):
                page_source += field_text + " 1 <input type=\"text\" name=\"" + name_field + "1\"><br>" + field_text \
                               + " 2 <input type=\"text\" name=\"" + name_field + "2\"><br>" + field_text + \
                               " 3 <input type=\"text\" name=\"" + name_field + "3\"><br>" + field_text + \
                               " 4 <input type=\"text\" name=\"" + name_field + "4\"><br>" + field_text + \
                               " 5 <input type=\"text\" name=\"" + name_field + "5\"><br>"
            else:
                page_source += field_text + " <input type=\"text\" name=\"" + name_field + "\"><br>"
            page_source += "<input type=\"submit\" value=\"Submit\"></form><h3>When all " \
                           "fields are filled, press the \"Submit\" button. A blank page will be " \
                           "displayed and it's possible to close it.</h3></body></html>"

            newfile.write(page_source)

    '''
    This functions injects in the cleaned page some JS functions that trigger AJAX calls against a local webserver.
    This allows the backend to recognize the requested resources by the user.
    
    @param is_forum: at the moment, this boolean allows to change the HTTP request triggered against the backend server.
    '''

    def inject_js_listeners(self, training_stage):

        print_warning("[TRAINER] Injecting JS content...")
        jquery_content = open(os.path.join(os.path.join(self.ROOT_DIR, "resources"), "jquery-3.3.1.min.js"), "r").read()
        with open("/tmp/no_js_dump.html") as oldfile, open("/tmp/clean_dump.html", 'w') as newfile:

            # Click-and-trigger-HTTP-request listeners + call on close
            if (training_stage == TrainingStage.FORUM) or (training_stage == TrainingStage.SUBFORUM) or (
                    training_stage == TrainingStage.THREAD_POOL) or (training_stage == TrainingStage.POST_POOL) or (
                    training_stage == TrainingStage.THREAD_NEXT_PAGE) or (
                    training_stage == TrainingStage.SUBFORUM_NEXT_PAGE) or (training_stage == TrainingStage.LOGIN_PAGE):

                for line in oldfile:
                    # Pre-editing for correcting body tag
                    if "<body " in line or "<BODY " in line or "<body>" in line or "<BODY>" in line:
                        index = line.find('>')
                        output_line = line[:index] + " onload=\"setupListeners()\"" + line[index:]
                        line = output_line
                    newfile.write(line)
                    # After writing head tag, let's inject the scripts
                    if "<head " in line or "<HEAD " in line or "<head>" in line or "<HEAD>" in line:

                        # Beautified snippet below
                        if training_stage == TrainingStage.LOGIN_PAGE:
                            injected_content = '<script>function setupListeners(){var ' \
                                               'Anchors=document.getElementsByTagName("a");for(var ' \
                                               'i=0;i<Anchors.length;i+=1){Anchors[i].removeAttribute("href")}var ' \
                                               'forms=document.getElementsByTagName("form");for(var ' \
                                               'i=0;i<forms.length;i+=1){forms[i].removeAttribute("action");forms[' \
                                               'i].removeAttribute("method")}}</script><script>var username_collected' \
                                               '=false;var is_next_button=false;document.onclick=function(event){ ' \
                                               'console.log(event); var target=\'target\'in event?event.target:event.' \
                                               'srcElement;console.log(target); if(' \
                                                'target.tagName===\'INPUT\' || target.tagName===\'BUTTON\' ){console.' \
                                               'log(target.tagName);console.log(\'My thoughts against JS are censored' \
                                               '. Why? Because removing any of these 4 prints up there causes it to ' \
                                               'fail to send the last HTTP request.\');console.log(\'Please leave ' \
                                               'this piece of black magic where it is. I hate doing things in this ' \
                                               'way, but Im done debugging JS. Well never be friends.\'); var ' \
                                                'root=document.compatMode===\'CSS1Compat\'?document.documentElement' \
                                                ':document.body;var path=getPathTo(target);if(!username_collected){' \
                                                '$.post("http://localhost:8080/login_username",{xpath:path},' \
                                                'function(data,status){console.log("error while ' \
                                                'posting..?")});username_collected=true;alert("Please click on ' \
                                                'password field.")}else{if(!is_next_button){$.post(' \
                                                '"http://localhost:8080/login_password",{xpath:path},function(data,' \
                                                'status){console.log("error while posting..?")});alert("Please click ' \
                                                'on the login button. After this, close the window. After you close ' \
                                               'the next page, put again Tor Browser on foreground, if it isn\'t.");' \
                                               'is_next_button=true}else{$.post("http://localhost:8080/login_button"' \
                                               ',{xpath:path},function(data,status){console.log("error while posting' \
                                               '..?")})}}}};function getPathTo(element){if(element.id!==\'\'){return ' \
                                               '"//*[@id=\'"+element.id+"\']"}if(element===document.body){return ' \
                                                'element.tagName.toLowerCase()}var ix=0;var ' \
                                                'siblings=element.parentNode.childNodes;for(var ' \
                                                'i=0;i<siblings.length;i+=1){var sibling=siblings[i];if(' \
                                                'sibling===element){return getPathTo(' \
                                                'element.parentNode)+\'/\'+element.tagName.toLowerCase()+\'[\'+(' \
                                                'ix+1)+\']\'}if(sibling.nodeType===1&&sibling.tagName===element.' \
                                                'tagName){ix+=1}}};alert("Please click on username field.")</script>'
                        else:
                            injected_content = '<script>function setupListeners(){for(var e=document.' \
                                               'getElementsByTagName("a"),n=0;n<e.length;n++)e[n].removeAttribute' \
                                               '("href"),e[n].addEventListener("click",function(e){name_found=' \
                                               'getPathTo(this),$.post("http://'
                            if training_stage == TrainingStage.FORUM:
                                injected_content += 'localhost:8080/forum_name'
                            if training_stage == TrainingStage.SUBFORUM:
                                injected_content += 'localhost:8080/subforum_name'
                            if training_stage == TrainingStage.SUBFORUM_NEXT_PAGE:
                                injected_content += 'localhost:8080/subforum_next_page'
                            if training_stage == TrainingStage.THREAD_POOL:
                                injected_content += 'localhost:8080/thread_name'
                            if training_stage == TrainingStage.THREAD_NEXT_PAGE:
                                injected_content += 'localhost:8080/thread_next_page'
                            injected_content += '",{name:name_found},function(e,n){console.log("error while posting' \
                                                '..?")})},!1)}</script><script>'
                            if training_stage == TrainingStage.FORUM:
                                injected_content += 'alert("Click forums to crawl.'
                            if training_stage == TrainingStage.SUBFORUM:
                                injected_content += 'alert("Click subforums to crawl.'
                            if training_stage == TrainingStage.SUBFORUM_NEXT_PAGE:
                                injected_content += 'alert("Click the next page button.'
                            if training_stage == TrainingStage.THREAD_POOL:
                                injected_content += 'alert("Click exactly five thread titles.'
                            if training_stage == TrainingStage.THREAD_NEXT_PAGE:
                                injected_content += 'alert("Click the next page button.'
                            injected_content += ' After you close the next page, put again Tor Browser on foreground,' \
                                                ' if it isn\'t.");function ' \
                                                'getPathTo(element){if(element.id!==\'\'){return "//*[' \
                                                '@id=\'"+element.id+"\']"}if(element===document.body){return ' \
                                                'element.tagName.toLowerCase()}var ix=0;var ' \
                                                'siblings=element.parentNode.childNodes;for(var ' \
                                                'i=0;i<siblings.length;i+=1){var sibling=siblings[i];if(' \
                                                'sibling===element){return getPathTo(' \
                                                'element.parentNode)+\'/\'+element.tagName.toLowerCase()+\'[\'+(' \
                                                'ix+1)+\']\'}if(sibling.nodeType===1&&sibling.tagName===element.' \
                                                'tagName){ix+=1}}}</script>'

                        injected_content += '<script>window.addEventListener("beforeunload",function(e){$.get("' \
                                            'http://localhost:8080/closed",function(e,o){console.log("should really ' \
                                            'be triggered?")});return(e||window.event).returnValue="o/","o/"});' \
                                            '</script><script>' + jquery_content + '</script>'
                        newfile.write(injected_content)
            else:
                # Call on close
                for line in oldfile:
                    newfile.write(line)
                    if "<head " in line or "<HEAD " in line or "<head>" in line or "<HEAD>" in line:
                        injected_content = "<script>window.addEventListener(\"beforeunload\",function(e){$.get(\"" \
                                           "http://localhost:8080/closed\",function(e,o){console.log(\"should really " \
                                           "be triggered?\")});return(e||window.event).returnValue=\"o/\",\"o/\"" \
                                           "});</script><script>" + jquery_content + "</script>"
                        newfile.write(injected_content)
        print_successful_status("[TRAINER] ...done!")

    def check_found_elements(self, element_identifiers, element_type, parent_element_xpath, training_stage):

        with open("/tmp/no_js_dump.html") as oldfile, open("/tmp/highlighted_dump.html", 'w') as newfile:
            for line in oldfile:
                # Pre-editing for correct\ing body tag
                if "<body " in line or "<BODY " in line or "<body>" in line or "<BODY>" in line:
                    index = line.find('>')
                    output_line = line[:index] + " onload=\"highlightElements()\"" + line[index:]
                    line = output_line
                newfile.write(line)
                if "<head " in line or "<HEAD " in line or "<head>" in line or "<HEAD>" in line:
                    injected_content = ""
                    # Beautified snippets below
                    if element_type == ElementType.CLASS:
                        injected_content = "<script>function highlightElements(){var nodeList=document." \
                                           "querySelectorAll(\""
                        for element in element_identifiers:
                            element = element.replace(" ", ".")
                            injected_content += "." + element + ", "
                        injected_content = injected_content[:-2]
                        injected_content += "\");for(var i=0,length=nodeList.length;i<length;i+=1){nodeList[i].style." \
                                            "backgroundColor=\"yellow\";}}</script>"
                    else:
                        if element_type == ElementType.XPATH:
                            injected_content = "<script>function highlightElements(){var element_identifiers=["
                            for element in element_identifiers:
                                if (training_stage == TrainingStage.POST_COUNT) or (training_stage == TrainingStage.
                                        POST_AUTHOR) or (training_stage == TrainingStage.POST_CONTENT) or (
                                        training_stage == TrainingStage.POST_DATE):
                                    injected_content += "\"" + parent_element_xpath + "/" + element + "\","
                                else:
                                    injected_content += "\"" + element + "\","
                            injected_content += "];for(var j=0;j<element_identifiers.length;j+=1){result=document." \
                                                "evaluate(element_identifiers[j],document,null,XPathResult." \
                                                "ORDERED_NODE_SNAPSHOT_TYPE,null);for(var i=0;i<result.snapshotLength" \
                                                ";i+=1){result.snapshotItem(i).style.backgroundColor=\"yellow\"}}}" \
                                                "</script>"
                    newfile.write(injected_content)

        Popen(["sudo", "-u", "user", "/usr/lib/firefox/firefox", "-new-window", "-url",
               "file:///tmp/highlighted_dump.html", "-foreground"])

        sleep(5)

        if training_stage == TrainingStage.THREAD_NEXT_PAGE2:
            if pymsgbox.confirm('Is the content marked correctly?', 'Check', ['Yes', 'No']) == 'No':
                if pymsgbox.confirm('The buttons for going back are highlighted as well?', 'Check', ['Yes', 'No']) == 'No':
                    return 'No'
                else:
                    return 'Duplicate'
            else:
                return 'Yes'

        return pymsgbox.confirm('Is the content marked correctly?', 'Check', ['Yes', 'No'])

    '''
    This function orchestrates the sequence of those activities: opens the crafted page in a different browser and 
    starts the webserver to listen to the AJAX calls. Moreover, instances a MQTT message dispatcher, in order to receive
    the collected information through different processes; finally, converts the information in XPaths and provides to 
    store them in the DB.
    
    @param is_forum: at the moment, allows the function to extract different fields of the Json received and is used as
                     a check of completion: if the data collected is from subforums, then is possible to insert on DB
                     a row with both forum and subforum's XPath.
    @param forum_page_xpath: it is needed only if is_forum = False. If so, it will be used for creating the entry on DB.  
    '''

    def collect_info_and_render_pages(self, forum_landing_page, training_stage, forum_page_xpath, parent_element_xpath):

        if forum_page_xpath is None:
            forum_page_xpath = ""
        if parent_element_xpath is None:
            parent_element_xpath = ""

        if (training_stage == TrainingStage.FORUM) or (training_stage == TrainingStage.SUBFORUM) or (
                training_stage == TrainingStage.THREAD_POOL) or (
                training_stage == TrainingStage.SUBFORUM_NEXT_PAGE) or (
                training_stage == TrainingStage.THREAD_NEXT_PAGE) or (training_stage == TrainingStage.LOGIN_PAGE):
            # Hope that you'll never need an actual marionette to open a different driver...
            # webdriver.Firefox(firefox_binary="/usr/bin/firefox").get("file:///tmp/clean_dump.html")
            # TODO parametrize please.
            # TODO perche' non mi apre una nuova finestra di Firefox?
            Popen(["sudo", "-u", "user", "/usr/lib/firefox/firefox", "-new-window", "-url",
                   "file:///tmp/clean_dump.html", "-foreground"])
        else:
            # Hope that you'll never need an actual marionette to open a different driver...
            # webdriver.Firefox(firefox_binary="/usr/bin/firefox").get("file:///tmp/clean_dump.html")
            # TODO parametrize please.
            Popen(["sudo", "-u", "user", "/usr/lib/firefox/firefox", "-new-window", "-url",
                   "file:///tmp/content_collector.html", "-url", "file:///tmp/clean_dump.html", "-foreground"])

        def callback(ch, method, properties, body):
            print_internals("[TRAINER - LISTENER] Received %r" % json.loads(str(body)))
            self.element_names_received = body
            ch.stop_consuming()

        server = HTTPRequestListener()
        server.start()
        MessageDispatcher().receive_one_json(callback=callback)
        # Not needed, since the shutdown is done from the handler
        # server.shut_down()

        return self.render_element_identifiers_and_collect_answers(forum_landing_page, training_stage, forum_page_xpath, parent_element_xpath, None)

    def render_element_identifiers_and_collect_answers(self, forum_landing_page, training_stage, forum_page_xpath, parent_element_xpath, previous_identifier):

        sleep(5)
        element_class = []
        element_xpaths = []
        if (training_stage == TrainingStage.THREAD_NEXT_PAGE) or (training_stage == TrainingStage.THREAD_NEXT_PAGE2):
            if training_stage == TrainingStage.THREAD_NEXT_PAGE2:
                reply = self.check_found_elements([previous_identifier], ElementType.CLASS, parent_element_xpath,
                                                  training_stage)
            else:
                # Retrieve elements by finding the most common class among the elements found by text
                element_class = self.structure_analyzers.get_elements_class_from_json(
                    training_stage, self.element_names_received, False, parent_element_xpath)
                reply = self.check_found_elements(element_class, ElementType.CLASS, parent_element_xpath,
                                                  training_stage)
            if reply == 'No':
                # Retrieve elements by finding the two most common classes among the elements found by text
                element_class = self.structure_analyzers.get_elements_class_from_json(
                    training_stage, self.element_names_received, True, parent_element_xpath)
                reply = self.check_found_elements(element_class, ElementType.CLASS, parent_element_xpath,
                                                  training_stage)
                if reply == 'No':
                    # Retrieve elements by the sharpest and similar XPath of the collected elements.
                    element_xpaths = self.structure_analyzers.get_element_xpaths_from_json(
                        training_stage, self.element_names_received, False, parent_element_xpath)
                    reply = self.check_found_elements(element_xpaths, ElementType.XPATH, parent_element_xpath,
                                                      training_stage)
                    if reply == 'No':
                        # Retrieve elements the same XPath as before, but removing the last level.
                        element_xpaths = self.structure_analyzers.get_element_xpaths_from_json(
                            training_stage, self.element_names_received, True, parent_element_xpath)
                        reply = self.check_found_elements(element_xpaths, ElementType.XPATH, parent_element_xpath,
                                                          training_stage)
                        # TODO: If the content contains squared brackets, then the class retrieval fails.
                        if reply == 'No':
                            print_error_and_exit("[TRAINER] We got problems figuring out how to programmatically "
                                                 "collect this content.")
            if reply == 'Duplicate':
                self.insert_information_in_db(
                    None, None, training_stage, None, None)
        else:
            # Retrieve elements by the sharpest and similar XPath of the collected elements.
            element_xpaths = self.structure_analyzers.get_element_xpaths_from_json(
                training_stage, self.element_names_received, False, parent_element_xpath)
            element_class = []

            reply = self.check_found_elements(element_xpaths, ElementType.XPATH, parent_element_xpath, training_stage)

            # Post pool is treated differently because it is an XPath that has to be generalized starting from some text
            if training_stage == TrainingStage.POST_POOL:
                while reply == 'No':
                    element_xpaths = self.structure_analyzers.get_element_xpaths_from_json(
                        training_stage, self.element_names_received, True, parent_element_xpath)
                    reply = self.check_found_elements(element_xpaths, ElementType.XPATH, parent_element_xpath, training_stage)
            else:
                if reply == 'No':
                    # Retrieve elements the same XPath as before, but removing the last level.
                    element_xpaths = self.structure_analyzers.get_element_xpaths_from_json(
                        training_stage, self.element_names_received, True, parent_element_xpath)
                    reply = self.check_found_elements(element_xpaths, ElementType.XPATH, parent_element_xpath, training_stage)
                    # TODO: If the content contains squared brackets, then the class retrieval fails.
                    if reply == 'No':
                        # Retrieve elements by finding the most common class among the elements found by text
                        element_class = self.structure_analyzers.get_elements_class_from_json(
                            training_stage, self.element_names_received, False, parent_element_xpath)
                        reply = self.check_found_elements(element_class, ElementType.CLASS, parent_element_xpath, training_stage)
                        if reply == 'No':
                            # Retrieve elements by finding the two most common classes among the elements found by text
                            element_class = self.structure_analyzers.get_elements_class_from_json(
                                training_stage, self.element_names_received, True, parent_element_xpath)
                            reply = self.check_found_elements(element_class, ElementType.CLASS, parent_element_xpath, training_stage)
                            if reply == 'No':
                                print_error_and_exit("[TRAINER] We got problems figuring out how to programmatically "
                                                     "collect this content.")
        if element_class.__len__() == 0:
            self.insert_information_in_db(
                forum_landing_page, forum_page_xpath, training_stage, element_xpaths, ElementType.XPATH)
            return element_xpaths

        else:
            self.insert_information_in_db(
                forum_landing_page, forum_page_xpath, training_stage, element_class, ElementType.CLASS)
            return element_class

    def insert_information_in_db(self, forum_landing_page, forum_page_xpath, training_stage, element_ids, element_type):

        """
        NOTE: Forum as training stage is being purposely skipped since the whole data structure to insert is
        a row containing also subforum XPaths.
        """
        if training_stage == TrainingStage.LOGIN_PAGE:
            self.login_fields_dao.insert_login_xpaths(element_ids)
            self.website_id = self.db.get_last_website_id()
        if training_stage == TrainingStage.FORUM:
            return
        if training_stage == TrainingStage.SUBFORUM:
            for subforum_xpath in element_ids:
                self.website_dao.insert_link_forum_subforum_xpaths(self.website_id, forum_landing_page, forum_page_xpath, subforum_xpath)
            if len(element_ids) == 0:
                self.website_dao.insert_link_forum_subforum_xpaths(self.website_id, forum_landing_page,
                                                                   forum_page_xpath, None)
        if training_stage == TrainingStage.THREAD_POOL:
            self.forum_fields_dao.insert_thread_pool_id(self.website_id, element_ids, element_type)
        if training_stage == TrainingStage.SUBFORUM_NEXT_PAGE:
            self.forum_fields_dao.insert_subforum_next_page(self.website_id, element_ids, element_type)
        if training_stage == TrainingStage.THREAD_POST_COUNT:
            self.forum_fields_dao.insert_thread_post_count(self.website_id, element_ids, element_type)

        if training_stage == TrainingStage.POST_POOL:
            self.thread_fields_dao.insert_post_pool_id(self.website_id, element_ids, element_type)
        if training_stage == TrainingStage.THREAD_NEXT_PAGE:
            self.thread_fields_dao.insert_thread_next_page_id(self.website_id, element_ids, element_type)
        if training_stage == TrainingStage.THREAD_NEXT_PAGE2:
            self.website_dao.set_is_vbullettin_by_website_id(self.website_id)
        if training_stage == TrainingStage.THREAD_TITLE:
            self.thread_fields_dao.insert_thread_title_id(self.website_id, element_ids, element_type)
        if training_stage == TrainingStage.POST_AUTHOR:
            self.thread_fields_dao.insert_post_author_id(self.website_id, element_ids, element_type)
        if training_stage == TrainingStage.POST_COUNT:
            self.thread_fields_dao.insert_post_count_id(self.website_id, element_ids, element_type)
        if training_stage == TrainingStage.POST_CONTENT:
            self.thread_fields_dao.insert_post_text_id(self.website_id, element_ids, element_type)
        if training_stage == TrainingStage.POST_DATE:
            self.thread_fields_dao.insert_post_date_id(self.website_id, element_ids, element_type)


##############################################
# Javascript snippet for inject_js_listeners #
# -------------- FORUM CASE ---------------- #
# ----- Change http://../forum_name to ----- #
# -- http://../subforum_name for subforums - #
##############################################

"""
    Injected function in inject_js_listeners:
    <script>
    function setupListeners(){
        var Anchors = document.getElementsByTagName("a");
        for (var i = 0; i < Anchors.length; i++) {
            Anchors[i].removeAttribute("href");
            Anchors[i].addEventListener("click", function(event) {
                name_found = getPathTo(this)
                $.post("http://localhost:8080/forum_name",
                {
                    name: name_found
                },
                function(data, status){
                    console.log("error while posting..?")
                });
            }, false);
        }
    }
    function getPathTo(element) {
        if (element.id !== '')
            return "//*[@id='" + element.id + "']";
    
        if (element === document.body)
            return element.tagName.toLowerCase();
    
        var ix = 0;
        var siblings = element.parentNode.childNodes;
        for (var i = 0; i < siblings.length; i++) {
            var sibling = siblings[i];
    
            if (sibling === element) return getPathTo(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
    
            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                ix++;
            }
        }
    }
    </script>
    <script>
    window.addEventListener("beforeunload", function(e) {
        $.get("http://localhost:8080/closed", function(e, o) {
            console.log("should really be triggered?")
        });
        return (e || window.event).returnValue = "o/", "o/"
    });
    </script>
    <script> ...jquery here... </script>
"""

##############################################
# Javascript snippet for inject_js_listeners #
# ------------ LOGIN_PAGE CASE ------------- #
##############################################
"""
<script>
function setupListeners(){
    var Anchors = document.getElementsByTagName("a");
    for (var i = 0; i < Anchors.length; i++) {
        Anchors[i].removeAttribute("href");
    }
    var forms = document.getElementsByTagName("form");
    for (var i = 0; i < forms.length; i++) {
        forms[i].removeAttribute("action");
        forms[i].removeAttribute("method");
    }
}
</script>
<script>
var username_collected = false;
var is_next_button = false;
document.onclick = function(event) {
    var target = 'target' in event ? event.target : event.srcElement; // another IE hack
    console.log(event);
    if (target.tagName === 'INPUT' || target.tagName === 'BUTTON') {
        console.log(target.tagName)
        console.log('My thoughts against JS are censored. Why? Because removing any of these 4 prints up there causes it to fail to send the last HTTP request.')
        console.log('Please leave this piece of black magic where it is. I hate doing things in this way, but I'm done debugging JS. We'll never be friends.')
        var root = document.compatMode === 'CSS1Compat' ? document.documentElement : document.body;
        var path = getPathTo(target);
        if (!username_collected) {
            $.post("http://localhost:8080/login_username", {
                    name: path
                },
                function(data, status) {
                    console.log("error while posting..?")
                });
            username_collected = true;
            alert("Please click on password field.")
        } else {
            if (!is_next_button) {
                $.post("http://localhost:8080/login_password", {
                        name: path
                    },
                    function(data, status) {
                        console.log("error while posting..?")
                    });
                alert("Please click on the login button. After this, close the window. After you close the next page, put again Tor Browser on foreground, if it isn\'t.");
                is_next_button = true;
            } else {
                $.post("http://localhost:8080/login_button", {
                        name: path
                    },
                    function(data, status) {
                        console.log("error while posting..?")
                    });
            }
        }
    }
}

alert("Please click on username field.")

function getPathTo(element) {
    if (element.id !== '')
        return "//*[@id='" + element.id + "']";

    if (element === document.body)
        return element.tagName.toLowerCase();

    var ix = 0;
    var siblings = element.parentNode.childNodes;
    for (var i = 0; i < siblings.length; i++) {
        var sibling = siblings[i];

        if (sibling === element) return getPathTo(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';

        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
            ix++;
        }
    }
}</script>
<script>jquery code here...</script>
"""

###############################################
# Javascript snippet for check_found_elements #
# --------------- CLASS CASE ---------------- #
###############################################

"""
<script>
function highlightElements() {
    var nodeList = document.querySelectorAll("." + '.'.join("element_identifiers")); 
        for (var i = 0, length = nodeList.length; i < length; i++) {
            nodeList[i].style.backgroundColor = "yellow"
        }
    }
</script>
"""

###############################################
# Javascript snippet for check_found_elements #
# --------------- XPATH CASE ---------------- #
#  CARE WHILE REPLACING! THE SNIPPET DOESN'T  #
# ------ INCLUDE VARIABLE INJECTIONS! ------- #
###############################################

"""
<script>
function highlightElements() {
    var element_identifiers = [\"'//*[starts-with(@id, "post_id_")]/div[1]/div[2]/div[1]', \"];
    for (var j = 0; j < element_identifiers.length; j += 1) {
        result = document.evaluate(element_identifiers[j], document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (var i = 0; i < result.snapshotLength; i += 1) {
            result.snapshotItem(i).style.backgroundColor = "yellow"
        }
    }
}
</script>
"""
