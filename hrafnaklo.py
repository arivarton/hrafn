import os
import re
from sys import path
from bs4 import BeautifulSoup
import requests
import pickle
from datetime import date

import crawler
#from hrafnauga import *

HRAFNPATH = os.path.dirname(os.path.abspath(__file__))
DBPATH = os.path.join(HRAFNPATH, 'db')
file_array = os.listdir(os.path.join(HRAFNPATH, 'content'))
file_array.sort()
video_suffix = ["mp4","mkv","avi"]
picture_suffix = ["jpg","jpeg","gif","png"]
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
            if self.last_item_type == None:
                self.current_list = [item_type, item]
            elif item_type != self.last_item_type:
                self.main_dictionary.update({self.iteration_number:self.current_list})
                self.iteration_number += 1
                self.current_list = [item_type, item]
            else:
                self.current_list.append(item)
            self.main_dictionary.update({self.iteration_number:self.current_list})
            self.last_item_type = item_type
        return self.main_dictionary

# Function to search for keywords inside config files for websites
class WebConfigFileParser():
    def  __init__(self):
        self.request_type = None
        self.website = None
        self.sub_link = None
        self.content_selection = None
        self.title = None
        self.get_selection = None
        self.list_number = None
        self.list_number_selection = None
        self.is_picture = False
        self.link_selection = None
        self.placement_height = '100'
        self.placement_width = '100'
        self.placement_justify = 'center'
        self.placement_anchor = 'n'
        self.font_type = 'NotoSansCJK-Regular'
        self.font_size = '12'
        self.font_weight = 'normal'
    def run(self, line):
        #Type of request
        temp = re.search(r'[^(=]+', line)
        if temp:
            self.request_type = temp.group(0)

        temp = re.search(r'website=["\'](.*)["\']', line)
        if temp:
            self.website = temp.group(1)

        temp = re.search(r'sub_link=["\'](.*)["\']', line)
        if temp:
            temp = temp.group(1)
            if re.search(r'\$\(month\)', temp):
                temp = re.sub(r'\$\(month\)', str(date.today().month), temp)
            if re.search(r'\$\(year\)', temp):
                temp = re.sub(r'\$\(year\)', str(date.today().year), temp)
            self.sub_link = temp

        #All
        temp = re.search(r'content_selection=["\']([^"\']*)["\']', line)
        if temp:
            self.content_selection = temp.group(1)
        temp = re.search(r'title=["\']([^"\']*)["\']', line)
        if temp:
            self.title = temp.group(1)
        temp = re.search(r'get_selection=["\']([^"\']*)["\']', line)
        if temp:
            self.get_selection = temp.group(1)
        temp = re.search(r'list_number=["\']([^"\']*)["\']', line)
        if temp:
            self.list_number = int(temp.group(1))
        temp = re.search(r'list_number_selection=["\']([^"\']*)["\']', line)
        if temp:
            self.list_number_selection = temp.group(1)
        temp = re.search(r'is_picture=["\']([^"\']*)["\']', line)
        if temp:
            if temp.group(1).lower() == "true":
                self.is_picture = True

        #Only expandonlink
        temp = re.search(r'link_selection=["\']([^"\']*)["\']', line)
        if temp:
            self.link_selection = temp.group(1)

        #Text placement
        #Height
        temp = re.search(r'placement\(.*height=["\']([^"\']+)["\'].*\)', line)
        if temp:
            self.placement_height = temp.group(1)
        #Width
        temp = re.search(r'placement\(.*width=["\']([^"\']+)["\'].*\)', line)
        if temp:
            self.placement_width = temp.group(1)
        #Justify
        temp = re.search(r'placement\(.*justify=["\']([^"\']+)["\'].*\)', line)
        if temp:
            self.placement_justify = temp.group(1)
        #Anchor
        temp = re.search(r'placement\(.*anchor=["\']([^"\']+)["\'].*\)', line)
        if temp:
            self.placement_anchor = temp.group(1)

        #Font setup
        #Type
        temp = re.search(r'font\(.*type=["\']([^"\']+)["\'].*\)', line)
        if temp:
            self.font_type = temp.group(1)
        #Size
        temp = re.search(r'font\(.*size=["\']([^"\']+)["\'].*\)', line)
        if temp:
            self.font_size = temp.group(1)
        #Weight
        temp = re.search(r'font\(.*weight=["\']([^"\']+)["\'].*\)', line)
        if temp:
            self.font_weight = temp.group(1)

class WebCrawler():
    def __init__(self):
        self.run_check = True
        if not os.path.exists(DBPATH):
            os.makedirs(DBPATH)

    def crawl(self, list):
        for line in list:
            attributesFromFile = WebConfigFileParser()
            attributesFromFile.run(line.strip())
            if attributesFromFile.website is not None:
                catchedContent = crawler.ArticleCrawler(attributesFromFile.website)
            elif attributesFromFile.sub_link is not None:
                catchedContent.new_request(attributesFromFile.sub_link)
            elif attributesFromFile.request_type == 'new_list':
                # Crawl website and add to list
                catchedContent.new_list(
                    content_selection=attributesFromFile.content_selection,
                    title=attributesFromFile.title,
                    get_selection=attributesFromFile.get_selection,
                    list_number=attributesFromFile.list_number,
                    list_number_selection=attributesFromFile.list_number_selection,
                    is_picture=attributesFromFile.is_picture)
                print('Added crawling content for', attributesFromFile.request_type, 'with title:', attributesFromFile.title)

            elif attributesFromFile.request_type == 'addto_list':
                # Crawl website and add to list
                catchedContent.addto_list(
                    content_selection=attributesFromFile.content_selection,
                    title=attributesFromFile.title,
                    get_selection=attributesFromFile.get_selection,
                    list_number=attributesFromFile.list_number,
                    list_number_selection=attributesFromFile.list_number_selection,
                    is_picture=attributesFromFile.is_picture)
                print('Added crawling content for', attributesFromFile.request_type, 'with title:', attributesFromFile.title)

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
                print('Added crawling content for', attributesFromFile.request_type, 'with title:', attributesFromFile.title)
        return {'Crawled': catchedContent.list}

    def run(self, db_name, config_file):
        def pickleDump():
            self.list = self.crawl(config_file)
            self.list.update({'Date created': str(date.today())})
            self.list.update({'Config file': config_file})
            pickle.dump(self.list, open(os.path.join(DBPATH, db_name + '.db'), "wb"))
            print('Crawling content added to database:', db_name)
        try:
            self.list = pickle.load(open(os.path.join(DBPATH, db_name + '.db'), "rb"))
            if self.list['Date created'] == str(date.today()) \
            and self.list['Config file'] == config_file:
                print('Using current database:', db_name)
            else:
                pickleDump()
        except:
            pickleDump()
        return self.list['Crawled']

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
                print('Added placement and font content for', attributesFromFile.request_type, 'with title:', attributesFromFile.title)
            else:
                print('Will not add placement and font content for:', attributesFromFile.request_type, 'with title:', attributesFromFile.title)
        return {'Placement': placement, 'Font': font}


    '''
        class booking():
            def __init__(self, username, password):
                self.session = requests.session()
                self.loginPage = "https://admin.booking.com"
                #username = "1762155"
                #password = "madra2012"
                self.payload = {"loginname":username,"password":password}
                self.loginId = self.login()
                #print(self.loginId["sessionId"])

            def login(self):
                sessionId_ = self.session.post(self.loginPage,self.payload)
                noStarchSoup = BeautifulSoup(sessionId_.text, "lxml")
            sessionId_ = noStarchSoup.select("#ses")
            sessionId_ = sessionId_[0]["value"]
            hotelId_ = noStarchSoup.find(attrs={"name":"hotel_id"})
            hotelId_ = hotelId_["value"]
            return {"sessionId":sessionId_,"hotelId":hotelId_}


        def registerDevice(self):
            link = "https://admin.booking.com/hotel/hoteladmin/new_location/verify.html?hotel_id=" + self.loginId["hotelId"] + "&ses=" + self.loginId["sessionId"] + "&lang=en"
            linkContent = self.session.get(link)
            noStarchSoup = BeautifulSoup(linkContent.text, "lxml")
            phone_id_ = noStarchSoup.select(".sms-select-box option")
            phone_id_ = phone_id_[0]["value"]
            payload = {"ask_pin":"", "message_type":"sms", "phone_id":phone_id_, "phone_id_call":phone_id_, "phone_id_sms":phone_id_}
            verifyPage = self.session.post(link, payload)
            verifyPin = input("Enter the PIN: ")
            link = "https://admin.booking.com/hotel/hoteladmin/new_location/verify.html?hotel_id=" + self.loginId["hotelId"] + "&ses=" + self.loginId["sessionId"] + "&phone_id=0&dest="
            payload = {"account_id":"1443184", "ask_pin":verifyPin, "ses":self.loginId["sessionId"]}
            verified = self.session.post(link, payload)

        def getReservations(self):
            link = "https://admin.booking.com/hotel/hoteladmin/extranet_ng/manage/new_and_updated_reservations.html?ses=" + self.loginId["sessionId"] + "&lang=xu&hotel_id=" + self.loginId["hotelId"]
            linkContent = self.session.get(link)
            print(linkContent.text)
'''

#bookingSite = fetchWebContent.booking("1762155", "madra2012")
#login = bookingSite.login()
#bookingSite.registerDevice()
#bookingSite.getReservations()
