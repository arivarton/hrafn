import os
import re
import pickle
from datetime import date

import crawler

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DBPATH = os.path.join(WORK_DIR, 'db')
file_array = os.listdir(os.path.join(WORK_DIR, 'content'))
file_array.sort()
video_suffix = ["mp4", "mkv", "avi"]
picture_suffix = ["jpg", "jpeg", "gif", "png"]
website_suffix = ["website"]


# Takes a list of files and separates them into categories for images, videos
# and websites
class SortHrafnContent():
    def __init__(self, list):
        self.last_item_type = None
        self.main_dictionary = {}
        self.current_list = []
        self.iteration_number = 1
        self.list = list

    def create_dictionary(self):
        for item in self.list:
            # Check item type
            if item.lower().endswith(tuple(picture_suffix)):
                item_type = "image"
            elif item.lower().endswith(tuple(video_suffix)):
                item_type = "video"
            elif item.lower().endswith(tuple(website_suffix)):
                item_type = "web"
            else:
                print("Unrecognized filetype: " + item)
                continue
            # Add item to correct list
            if self.last_item_type is None:
                self.current_list = [item_type, item]
            elif item_type != self.last_item_type:
                self.main_dictionary.update({self.iteration_number: self.current_list})
                self.iteration_number += 1
                self.current_list = [item_type, item]
            else:
                self.current_list.append(item)
            self.main_dictionary.update({self.iteration_number: self.current_list})
            self.last_item_type = item_type
        return self.main_dictionary


# Function to search for keywords inside config files for websites
class WebConfigFileParser():
    def _search_and_set_argument(self, regex, line, group_number=0, default_value=None):
        try:
            return re.search(regex, line).group(group_number)
        except AttributeError:
            return default_value

    def run(self, line):
        #Type of request
        # Set the request type
        self.request_type = self._search_and_set_argument(r'[^(=]+', line)

        # Set the website
        self.website = self._search_and_set_argument(r'website=["\'](.*)["\']', line, 1)

        # Set sub link
        try:
            temp = re.search(r'sub_link=["\'](.*)["\']', line).group(1)
            if re.search(r'\$\(month\)', temp):
                temp = re.sub(r'\$\(month\)', str(date.today().month), temp)
            if re.search(r'\$\(year\)', temp):
                temp = re.sub(r'\$\(year\)', str(date.today().year), temp)
        except AttributeError:
            temp = None
        self.sub_link = temp

        # Set display time
        self.display_time = self._search_and_set_argument(r'display_time=["\'](.*)["\']', line, 1)
        # Set word latency
        self.word_latency = self._search_and_set_argument(r'word_latency=["\'](.*)["\']', line, 1)

        #All
        #Content selection
        self.content_selection = self._search_and_set_argument(r'content_selection=["\']([^"\']*)["\']', line, 1)
        #Title
        self.title = self._search_and_set_argument(r'title=["\']([^"\']*)["\']', line, 1)
        #Get selection
        self.get_selection = self._search_and_set_argument(r'get_selection=["\']([^"\']*)["\']', line, 1)
        #List number
        self.list_number = self._search_and_set_argument(r'list_number=["\']([^"\']*)["\']', line, 1)
        if self.list_number is not None:
            if str(self.list_number).lower() == 'today':
                self.list_number = date.today().day - 1
            else:
                self.list_number = int(self.list_number)
        #List number selection
        self.list_number_selection = self._search_and_set_argument(r'list_number_selection=["\']([^"\']*)["\']', line, 1)
        #Is picture
        try:
            temp = re.search(r'is_picture=["\']([^"\']*)["\']', line).group(1).lower()
            if temp == "true":
                self.is_picture = True
            else:
                self.is_picture = False
        except AttributeError:
            self.is_picture = False

        #Only expandonlink
        self.link_selection = self._search_and_set_argument(r'link_selection=["\']([^"\']*)["\']', line, 1)

        #Text placement
        #Height
        self.placement_height = self._search_and_set_argument(r'placement\(.*height=["\']([^"\']+)["\'].*\)', line, 1, '100')
        #Width
        self.placement_width = self._search_and_set_argument(r'placement\(.*width=["\']([^"\']+)["\'].*\)', line, 1, '100')
        #Justify
        self.placement_justify = self._search_and_set_argument(r'placement\(.*justify=["\']([^"\']+)["\'].*\)', line, 1, 'center')
        #Anchor
        self.placement_anchor = self._search_and_set_argument(r'placement\(.*anchor=["\']([^"\']+)["\'].*\)', line, 1, 'n')

        #Font setup
        #Type
        self.font_type = self._search_and_set_argument(r'font\(.*type=["\']([^"\']+)["\'].*\)', line, 1, 'NotoSansCJK-Regular')
        #Size
        self.font_size = self._search_and_set_argument(r'font\(.*size=["\']([^"\']+)["\'].*\)', line, 1, '12')
        #Weight
        self.font_weight = self._search_and_set_argument(r'font\(.*weight=["\']([^"\']+)["\'].*\)', line, 1, 'normal')


class WebCrawler():
    def __init__(self, db_name, picture_storage):
        self.run_check = True
        if not os.path.exists(DBPATH):
            os.makedirs(DBPATH)
        self.db_name = db_name
        if not os.path.exists(picture_storage):
            os.makedirs(picture_storage)
        self.picture_storage = picture_storage

    def crawl(self, config_file):
        display_time = 10
        word_latency = 2
        for line in config_file:
            attributesFromFile = WebConfigFileParser()
            attributesFromFile.run(line.strip())
            if attributesFromFile.website is not None:
                catchedContent = crawler.ArticleCrawler(website=attributesFromFile.website,
                                                        db_name=self.db_name,
                                                        picture_storage=self.picture_storage)
            elif attributesFromFile.sub_link is not None:
                catchedContent.new_request(attributesFromFile.sub_link)
            elif attributesFromFile.display_time is not None:
                display_time = attributesFromFile.display_time
            elif attributesFromFile.word_latency is not None:
                word_latency = attributesFromFile.word_latency
            elif attributesFromFile.request_type == 'new_list':
                # Crawl website and add to list
                catchedContent.new_list(
                    content_selection=attributesFromFile.content_selection,
                    title=attributesFromFile.title,
                    get_selection=attributesFromFile.get_selection,
                    list_number=attributesFromFile.list_number,
                    list_number_selection=attributesFromFile.list_number_selection,
                    is_picture=attributesFromFile.is_picture)
                print('Added crawling content for', attributesFromFile.request_type,
                      'with title:', attributesFromFile.title)

            elif attributesFromFile.request_type == 'addto_list':
                # Crawl website and add to list
                catchedContent.addto_list(
                    content_selection=attributesFromFile.content_selection,
                    title=attributesFromFile.title,
                    get_selection=attributesFromFile.get_selection,
                    list_number=attributesFromFile.list_number,
                    list_number_selection=attributesFromFile.list_number_selection,
                    is_picture=attributesFromFile.is_picture)
                print('Added crawling content for', attributesFromFile.request_type,
                      'with title:', attributesFromFile.title)

            elif attributesFromFile.request_type == 'addto_list_expandonlink':
                # Crawl website and add to list
                catchedContent.addto_list_expandonlink(
                    link_selection=attributesFromFile.link_selection,
                    content_selection=attributesFromFile.content_selection,
                    title=attributesFromFile.title,
                    get_selection=attributesFromFile.get_selection,
                    list_number=attributesFromFile.list_number,
                    list_number_selection=attributesFromFile.list_number_selection,
                    is_picture=attributesFromFile.is_picture)
                print('Added crawling content for', attributesFromFile.request_type,
                      'with title:', attributesFromFile.title)
        return catchedContent.dict, display_time, word_latency

    def run(self, config_file):
        def newDatabaseAndContent():
            self.list, display_time, word_latency = self.crawl(config_file)
            self.list.update({'Date created': str(date.today())})
            self.list.update({'Config file': config_file})
            self.list.update({'Display time': int(display_time)})
            self.list.update({'Word latency': int(word_latency)})
            pickle.dump(self.list, open(os.path.join(DBPATH, self.db_name + '.db'), "wb"))
            print('Crawling content added to database:', self.db_name)
        try:
            self.list = pickle.load(open(os.path.join(DBPATH, self.db_name + '.db'), "rb"))
            if self.list['Date created'] == str(date.today()) \
                    and self.list['Config file'] == config_file:
                print('Using current database:', self.db_name)
            else:
                newDatabaseAndContent()
        except:
            newDatabaseAndContent()
        return self.list


class WebFontAndPlacement():
    def run(list):
        placement = {}
        font = {}
        for line in list:
            attributesFromFile = WebConfigFileParser()
            attributesFromFile.run(line.strip())
            # Update placement dictionary
            request_type_list = ['new_list', 'addto_list', 'addto_list_expandonlink']
            if attributesFromFile.request_type in request_type_list:
                placement.update({attributesFromFile.title:
                                  {'Height': attributesFromFile.placement_height,
                                   'Width': attributesFromFile.placement_width,
                                   'Justify': attributesFromFile.placement_justify,
                                   'Anchor': attributesFromFile.placement_anchor}
                                  })
                # Update font dictionary
                font.update({attributesFromFile.title:
                             {'Type': attributesFromFile.font_type,
                              'Size': attributesFromFile.font_size,
                              'Weight': attributesFromFile.font_weight}
                             })
                print('Added placement and font content for', attributesFromFile.request_type,
                      'with title:', attributesFromFile.title)
            else:
                print('Will not add placement and font content for:',
                      attributesFromFile.request_type, 'with title:', attributesFromFile.title)
        return {'Placement': placement, 'Font': font}
