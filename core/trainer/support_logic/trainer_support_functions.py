import re

from model.base_classes import TrainingStage, ContentType
import json
import itertools
from difflib import SequenceMatcher


class ElementRetriever:

    def __init__(self, program):
        self.program = program
        self.last_calculated_xpath = ""

    def get_element_xpaths_from_json(self, training_stage, element_names_received, has_failed_before, parent_element_xpath):

        results = []

        ### <Multiple xpaths by name>
        if training_stage == TrainingStage.FORUM:
            for element in json.loads(element_names_received)['forums']:
                results.append(element)

        if training_stage == TrainingStage.SUBFORUM:
            for element in json.loads(element_names_received)['subforums']:
                results.append(element)
        ### </Multiple xpaths by name>

        ### <Single xpath by multiple name>
        if training_stage == TrainingStage.POST_POOL:
            results.append(self.retrieve_elements_common_xpath(json.loads(element_names_received)['post_pool'],
                                                               ContentType.TEXT, has_failed_before, parent_element_xpath))

        if training_stage == TrainingStage.THREAD_POST_COUNT:
            results.append(self.retrieve_elements_common_xpath(json.loads(element_names_received)['thread_post_count'],
                                                               ContentType.TEXT, has_failed_before,
                                                               parent_element_xpath, training_stage=training_stage))

        # THOSE ARE ALREADY XPATHS
        if training_stage == TrainingStage.THREAD_POOL:
            results.append(self.calculate_common_xpath(json.loads(element_names_received)['thread_pool'],
                                                       has_failed_before))

        ### Special treatment for them: they are children of another already defined element. Since we want to retrieve
        ### exactly the elements inside of it, we are creating a relative xpath.
        if training_stage == TrainingStage.POST_CONTENT:
            subelement_full_xpath = self.retrieve_elements_common_xpath(json.loads(
                element_names_received)['post_content'], ContentType.TEXT, has_failed_before, parent_element_xpath)
            results.append(subelement_full_xpath)
            if results[0].startswith(parent_element_xpath):
                # +1 is for removing the extra slash
                results[0] = results[0][parent_element_xpath.__len__() + 1:]

        if training_stage == TrainingStage.POST_DATE:
            subelement_full_xpath = self.retrieve_elements_common_xpath(json.loads(
                element_names_received)['post_date'], ContentType.TEXT, has_failed_before, parent_element_xpath)
            results.append(subelement_full_xpath)
            if results[0].startswith(parent_element_xpath):
                # +1 is for removing the extra slash
                results[0] = results[0][parent_element_xpath.__len__() + 1:]

        if training_stage == TrainingStage.POST_AUTHOR:
            subelement_full_xpath = self.retrieve_elements_common_xpath(json.loads(
                element_names_received)['post_author'], ContentType.TEXT, has_failed_before, parent_element_xpath)
            results.append(subelement_full_xpath)
            if results[0].startswith(parent_element_xpath):
                # +1 is for removing the extra slash
                results[0] = results[0][parent_element_xpath.__len__() + 1:]

        if training_stage == TrainingStage.POST_COUNT:
            subelement_full_xpath = self.retrieve_elements_common_xpath(json.loads(
                element_names_received)['post_count'], ContentType.TEXT, has_failed_before, parent_element_xpath)
            results.append(subelement_full_xpath)
            if results[0].startswith(parent_element_xpath):
                # +1 is for removing the extra slash
                results[0] = results[0][parent_element_xpath.__len__() + 1:]

        ### </Single xpath by multiple name>

        ### <Single xpath by name>
        if training_stage == TrainingStage.SUBFORUM_NEXT_PAGE:
            results.append(json.loads(element_names_received)['subforum_next_page'])

        if (training_stage == TrainingStage.THREAD_NEXT_PAGE) or (training_stage == TrainingStage.THREAD_NEXT_PAGE2):
            results.append(json.loads(element_names_received)['thread_next_page'])
        ### </Single xpath by name>

        ### <Single xpath by text>
        if training_stage == TrainingStage.THREAD_TITLE:
            results.append(self.retrieve_element_xpath_by_text_content(
                json.loads(element_names_received)['thread_title'], has_failed_before, parent_element_xpath)
            )
        ### </Single xpath by text>

        if training_stage == TrainingStage.LOGIN_PAGE:
            results.append(json.loads(element_names_received)['login_username'])
            results.append(json.loads(element_names_received)['login_password'])
            results.append(json.loads(element_names_received)['login_button'])

        for element in results:
            if element[-1:] == "/":
                results.remove(element)
                results.append(element[:-1])
        return results

    # TODO mi puzza un po'... Se ho collisioni di nomi tra cose che mi interessano e non?
    def retrieve_element_xpaths_by_element_name(self, element_names):
        element_xpaths = []
        # Retrieve elements' XPath
        for element_name in element_names:
            element_xpaths.append(self.retrieve_element_xpath_by_element_name(element_name))
        return element_xpaths

    def retrieve_element_xpaths_by_class(self, class_names):
        # Source based on Johnsyweb's answer (rapid insertion in list without duplicates)
        # https://stackoverflow.com/a/19835134/4804285
        element_xpaths = []
        seen = set(element_xpaths)
        for item in self.program.driver.find_elements_by_css_selector('.'.join(class_names)):
            if item not in seen:
                seen.add(item)
                element_xpaths.append(item)
        return element_xpaths

    def retrieve_element_xpath_by_element_name(self, element_name):
        element = self.program.driver.find_element_by_link_text(element_name)
        return self.calculate_xpath(element)

    def retrieve_element_xpaths_by_text_content(self, text_contents, has_failed_before, parent_element_xpath, training_stage = None):
        elements_xpaths = []
        for text in text_contents:
            elements_xpaths.append(self.retrieve_element_xpath_by_text_content(text, has_failed_before, parent_element_xpath, training_stage))
        return elements_xpaths

    # TODO: sta cosa non va bene - dovro' iterare gli XPATH invece di buttare via tutto cio' che non e' primo
    # TODO: questa funzione fa schifo
    def retrieve_element_xpath_by_text_content(self, text_content, has_failed_before, parent_element_xpath, training_stage = None):
        # TODO: assure that there's not any space at the beginning nor at the end of the string
        elements = []
        text_content = text_content.replace("'", "\\'")
        if parent_element_xpath is "":
            if training_stage == TrainingStage.THREAD_POST_COUNT:
                elements = self.program.driver.find_elements_by_xpath("//*[text()=\"" + text_content + "\"]")
            else:
                elements = self.program.driver.find_elements_by_xpath("//*[text()[contains(., \"" + text_content + "\")]]")
        else:
            """
            IDEA: se l'xpath e' completamente definito, allora posso togliere la prima parte che matcha. Se invece 
            prevede l'esistenza di id, starts with e puttanate varie, allora posso tranquillamente cercare all'interno
            """
            elements = self.program.driver.find_element_by_xpath(parent_element_xpath).find_elements_by_xpath("//*[text()[contains(., \"" + text_content + "\")]]")
        # Checking if is not taking some wrong elements
        element_xpaths = []
        for element in elements:
            element_xpaths.append(self.calculate_xpath(element))
        element_xpaths = filter(lambda a: "head" not in a and "HEAD" not in a and "&nbsp;" not in a, element_xpaths)
        if has_failed_before and element_xpaths.__len__() > 1:
            return element_xpaths[1]
        if element_xpaths.__len__() == 0:
            return ""
        return element_xpaths[0]

    def calculate_xpath(self, element):
        # Source based on FourTwoOmega's reply
        # https://stackoverflow.com/questions/4176560/webdriver-get-elements-xpath
        xpath = self.program.driver.execute_script(
            "gPt=function(c){if(c.id!==''){return\"id('\"+c.id+\"')\"}if(c===document.body){return c.tagName}var "
            "a=0;var e=c.parentNode.childNodes;for(var b=0;b<e.length;b++){var d=e[b];if(d===c){return gPt(c."
            "parentNode)+'/'+c.tagName.toLowerCase()+'['+(a+1)+']'}if(d.nodeType===1&&d.tagName===c.tagName)"
            "{a++}}};return gPt(arguments[0]);", element)
        return xpath

    '''
    Custom function that, given a list of three strings, retrieves a string that no longer presents the numeric 
    indicator of a certain node, if different.

    @param element_xpaths: a list of three xpaths.
    @return: a string matching all the three xpaths.

    es:
    element_xpaths: 
        - /html/body/div[2]/div[3]/ol[1]/li[3]
        - /html/body/div[2]/div[4]/ol[1]/li[1]
        - /html/body/div[2]/div[4]/ol[1]/li[2]
    return value:
        - /html/body/div[2]/div/ol[1]/li

    based on RickardSjogren's answer: http://stackoverflow.com/questions/18715688/ddg#39404777
    #############
    Based on Inbar Rose's and Ben Blank's answers on StackOverflow:
    https://stackoverflow.com/a/17388505/4804285
    https://stackoverflow.com/a/942551/4804285
    '''
    def retrieve_elements_common_xpath(self, content, content_type, has_failed_before, parent_element_xpath, training_stage = None):
        element_xpaths = []
        if content_type == ContentType.NAME:
            element_xpaths = self.retrieve_element_xpaths_by_element_name(content)
        if content_type == ContentType.TEXT:
            element_xpaths = self.retrieve_element_xpaths_by_text_content(content, has_failed_before, parent_element_xpath, training_stage)
        return self.calculate_common_xpath(element_xpaths, has_failed_before)

    def calculate_common_xpath(self, element_xpaths, has_failed_before):

        at_least_one = False
        for element in element_xpaths:
            if element is not "" and element is not None:
                at_least_one = True

        if not at_least_one:
            return ""

        if has_failed_before:
            last_calculated_xpath_splitted = self.last_calculated_xpath.split("/")
            # If it is the root element, resolve a previous one.
            if (last_calculated_xpath_splitted[-1].__contains__("=")) or (last_calculated_xpath_splitted[-1].__contains__("@")):
                current_level_elements = self.program.driver.find_elements_by_xpath(self.last_calculated_xpath)[:5]
                parent_xpaths = []
                for element in current_level_elements:
                    parent_xpaths.append(self.calculate_xpath(element.find_element_by_xpath("..")))
                self.last_calculated_xpath = self.calculate_common_xpath(parent_xpaths, False)
            else:
                last_calculated_xpath_splitted = last_calculated_xpath_splitted[:-1]
                self.last_calculated_xpath = "/".join(map(str, last_calculated_xpath_splitted))
            return self.last_calculated_xpath

        else:
            def _similar(a, b):
                return SequenceMatcher(None, a, b).ratio()

            def _calculate_common_xpath_of_pair(pair):
                element1_splitted = pair[0].split("/")
                element2_splitted = pair[1].split("/")

                # Avoiding wrong splits. This is taken in account in the end.
                if pair[0][:5] == "//*[@" and pair[1][:5] == "//*[@":
                    element1_splitted = pair[0][5:].split("/")
                    element2_splitted = pair[1][5:].split("/")

                # Same number of elements, removing unwanted subfields.
                element1_splitted = element1_splitted[:element2_splitted.__len__()]
                element2_splitted = element2_splitted[:element1_splitted.__len__()]

                first_element_modified = False
                for index in range(0, element1_splitted.__len__()):
                    if element1_splitted[index] != element2_splitted[index]:
                        if index == 0:
                            first_element_modified = True
                        match = SequenceMatcher(None, element1_splitted[index], element2_splitted[index]). \
                            find_longest_match(0, len(element1_splitted[index]),
                                               0, len(element2_splitted[index]))
                        element1_splitted[index] = element1_splitted[index][match.b: match.b + match.size]
                        if "[" in element1_splitted[index]:
                            # The mismatch handled here is like:
                            # div[4] <---> div[22]
                            element1_splitted[index] = element1_splitted[index].split("[")[0]
                        else:
                            # If the XPath has a node depending on id or whatever, it has to be handled.
                            # It is always always the first node, so is fine to say that starts-with.
                            # TODO Nonetheless, this below is an assumption.
                            # If is a digit, is very likely that is a false positive (shouldn't be there)
                            while element1_splitted[index][-1].isdigit():
                                element1_splitted[index] = element1_splitted[index][:-1]
                if "('" in element1_splitted[0]:
                    # We get: id('tid-link-
                    # We want: //*[starts-with(@id, 'tid-link-')]
                    if first_element_modified:
                        element1_splitted[0] = "//*[starts-with(@" + element1_splitted[0].split("(")[0] + \
                                               ", " + element1_splitted[0].split("(")[1] + "')]"
                    else:
                        # We get: id('content')
                        # We want: //*[@id='content']
                        element1_splitted[0] = "//*[@" + element1_splitted[0].split("(")[0] + "=" + \
                                               element1_splitted[0].split("(")[1].split(")")[0] + "]"
                else:
                    if "='" in element1_splitted[0]:
                        # We get: //*[@id='tid_link-']
                        # We want: //*[starts-with(@id, "tid-link-")]
                        if first_element_modified:
                            element1_splitted[0] = "//*[starts-with(@" + element1_splitted[0].split("='")[0] + \
                                                   ", '" + element1_splitted[0].split("='")[1] + "')]"
                        else:
                            # We get: ["id='top']
                            # We want: //*[@id='top']
                            element1_splitted[0] = "//*[@" + element1_splitted[0]
                return "/".join(map(str, element1_splitted))

            all_possible_candidates = []
            all_reduced_xpaths = []
            similarity = 0
            most_similar_pair = []
            # Calculate most similar pair
            for pair in itertools.combinations(element_xpaths, r=2):
                if pair[0] != pair[1]:
                    current_similarity = _similar(pair[0], pair[1])
                    if current_similarity > similarity:
                        similarity = current_similarity
                        most_similar_pair = pair
            all_reduced_xpaths.append(_calculate_common_xpath_of_pair(most_similar_pair))
            element_xpaths.remove(most_similar_pair[0])
            element_xpaths.remove(most_similar_pair[1])
            print "######### JUST REMOVED:"
            print most_similar_pair[0]
            print most_similar_pair[1]
            print "SIMILARITY: " + str(similarity)
            print "the last one is the chain element"
            # Finding all the xpaths that have the same similarity with the second element. This is done since
            # there could be some other differences not covered from a single couple.
            all_checked = False
            chain_element = most_similar_pair[1]
            while not all_checked:
                if element_xpaths.__len__() > 1:
                    for (element, index) in zip(element_xpaths, range(1, element_xpaths.__len__() + 1)):
                        if chain_element != element:
                            current_similarity = _similar(chain_element, element)
                            print "CANDIDATE: " + element + " SIMILARITY: " + str(current_similarity)
                            if current_similarity == similarity:
                                all_possible_candidates.append(element)
                                element_xpaths.remove(element)
                                break
                        if index + 1 == element_xpaths.__len__():
                            all_checked = True
                if all_checked or element_xpaths.__len__() == 1:
                    break
            for element in all_possible_candidates:
                print "POSSIBLE CANDIDATE: " + element
            for element in all_possible_candidates:
                # They are inverted so I can produce the new xpath always based on the second one.
                new_pair = [element, chain_element]
                all_reduced_xpaths.append(_calculate_common_xpath_of_pair(new_pair))
            for element in all_reduced_xpaths:
                print "REDUCTED XPATHS: " + element
            while len(all_reduced_xpaths) != 1:
                result = _calculate_common_xpath_of_pair((all_reduced_xpaths[0], all_reduced_xpaths[1]))
                all_reduced_xpaths.append(result)
                all_reduced_xpaths.remove(all_reduced_xpaths[1])
                all_reduced_xpaths.remove(all_reduced_xpaths[0])
            self.last_calculated_xpath = all_reduced_xpaths[0]
            return all_reduced_xpaths[0]

    def get_elements_class_from_json(self, training_stage, element_names_received, has_failed_before, parent_element_xpath):

        results = []
        ### <Multiple classes by name>
        if training_stage == TrainingStage.FORUM:
            results = self.retrieve_elements_class_by_xpath(json.loads(element_names_received)['forums'])

        if training_stage == TrainingStage.SUBFORUM:
            results = self.retrieve_elements_class_by_xpath(json.loads(element_names_received)['subforums'])
        ### </Multiple classes by name>

        ### <Single class by names>
        if training_stage == TrainingStage.THREAD_POOL:
            results = self.calculate_common_xpath(
                json.loads(element_names_received)['thread_pool'], has_failed_before)
        ### </Single class by names>

        ### <Single class by name>
        if training_stage == TrainingStage.SUBFORUM_NEXT_PAGE:
            results.append(self.retrieve_element_class_by_xpath(json.loads(element_names_received)['subforum_next_page']))

        if (training_stage == TrainingStage.THREAD_NEXT_PAGE) or (training_stage == TrainingStage.THREAD_NEXT_PAGE2):
            results.append(self.retrieve_element_class_by_xpath(json.loads(element_names_received)['thread_next_page']))
        ### </Single class by name>

        ### <Single class by text>
        if training_stage == TrainingStage.THREAD_TITLE:
            results.append(self.retrieve_element_class_by_text_content(
                json.loads(element_names_received)['thread_title'], parent_element_xpath))

        if training_stage == TrainingStage.POST_CONTENT:
            results = self.retrieve_elements_common_class(json.loads(
                element_names_received)['post_content'], ContentType.TEXT, has_failed_before, parent_element_xpath)

        if training_stage == TrainingStage.POST_DATE:
            results = self.retrieve_elements_common_class(json.loads(
                element_names_received)['post_date'], ContentType.TEXT, has_failed_before, parent_element_xpath)

        if training_stage == TrainingStage.POST_AUTHOR:
            results = self.retrieve_elements_common_class(json.loads(
                element_names_received)['post_author'], ContentType.TEXT, has_failed_before, parent_element_xpath)

        if training_stage == TrainingStage.POST_COUNT:
            results = self.retrieve_elements_common_class(json.loads(
                element_names_received)['post_count'], ContentType.TEXT, has_failed_before, parent_element_xpath)

        ### </Single class by text>

        if training_stage == TrainingStage.LOGIN_PAGE:
            results.append(json.loads(element_names_received)['login_username'])
            results.append(json.loads(element_names_received)['login_password'])
            results.append(json.loads(element_names_received)['login_button'])

        if training_stage == TrainingStage.THREAD_POST_COUNT:
            results.append(self.retrieve_elements_common_class(json.loads(
                element_names_received)['thread_post_count'], ContentType.TEXT, has_failed_before, parent_element_xpath))

        return results

    def retrieve_elements_class_by_xpath(self, element_xpaths):
        class_list = []
        for xpath in element_xpaths:
            class_list.append(self.retrieve_element_class_by_xpath(xpath))
        return class_list

    def retrieve_element_class_by_xpath(self, element_xpath):
        classes = self.program.driver.find_elements_by_xpath(element_xpath)[0].get_attribute("class")
        while (classes is None) or (classes == ""):
            element = self.program.driver.find_elements_by_xpath(element_xpath)[0]
            parent = element.find_element_by_xpath("..")
            # Looking for parent's class
            classes = self.retrieve_element_class_by_xpath(self.calculate_xpath(parent))
        return classes

    def retrieve_elements_class_by_element_name(self, element_names, parent_element_xpath):
        element_classes = []
        for element_name in element_names:
            element_classes.append(self.retrieve_element_class_by_element_name(element_name, parent_element_xpath))
        return element_classes

    def retrieve_element_class_by_element_name(self, element_name, parent_element_xpath):
        element = None
        if parent_element_xpath is "":
            element = self.program.driver.find_element_by_link_text(element_name)
        else:
            parent_element = self.program.driver.find_element_by_xpath(parent_element_xpath)
            element = parent_element.find_element_by_link_text(element_name)
        # Class might not be present in this level...
        while element.get_attribute("class") is None or element.get_attribute("class") == "" or element.get_attribute(""):
            element = element.find_element_by_xpath("..")
        return element.get_attribute("class")

    def retrieve_elements_class_by_text_content(self, text_contents, parent_element_xpath):
        element_classes = []
        for text in text_contents:
            element_classes.append(self.retrieve_element_class_by_text_content(text, parent_element_xpath))
        return element_classes

    def retrieve_element_class_by_text_content(self, text_content, parent_element_xpath):
        elements = []
        if parent_element_xpath is "":
            # TODO: assure that there's not any space at the beginning nor at the end of the string
            elements = self.program.driver.find_elements_by_xpath("//*[text()[contains(., \"" + text_content + "\")]]")
        else:
            parent_element = self.program.driver.find_element_by_xpath(parent_element_xpath)
            # TODO: assure that there's not any space at the beginning nor at the end of the string
            elements = parent_element.find_elements_by_xpath("//*[text()[contains(., \"" + text_content + "\")]]")
        classes = []
        for element in elements:
            xpath = self.calculate_xpath(element)
            # Checking if is not taking some wrong elements
            if "head" not in xpath and "HEAD" not in xpath:
                while element.get_attribute("class") is None or element.get_attribute("class") == "":
                    element = element.find_element_by_xpath("..")
                classes.append(element.get_attribute("class"))

        def most_common(lst):
            return max(set(lst), key=lst.count)

        return most_common(classes).replace(" ", ".")

    def retrieve_elements_common_class(self, content, content_type, has_failed_before, parent_element_xpath):
        elements_classes = []
        if content_type == ContentType.NAME:
            elements_classes = self.retrieve_elements_class_by_element_name(content, parent_element_xpath)
        if content_type == ContentType.TEXT:
            elements_classes = self.retrieve_elements_class_by_text_content(content, parent_element_xpath)
        # Pointless
        # elements_classes = filter(lambda a: a != "hide", elements_classes)

        results = []

        def most_common(lst):
            return max(set(lst), key=lst.count)

        new_class = most_common(elements_classes).replace(" ", ".")
        if new_class[-1:] == '.':
            new_class = new_class[:-1]
        results.append(new_class)
        if has_failed_before:
            # Returning them as the or for the CSS Selector
            elements_classes = filter(lambda a: a != most_common(elements_classes), elements_classes)
            most_common(elements_classes).replace(" ", ".")
            new_class = most_common(elements_classes).replace(" ", ".")
            if new_class[-1:] == '.':
                new_class = new_class[:-1]
            results.append(new_class)

        return results
