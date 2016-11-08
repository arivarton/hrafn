import os
from bs4 import BeautifulSoup
import requests
import pickle

WORK_DIR = os.getcwd()
DB_DIR = os.path.join(WORK_DIR, 'crawl-DB')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def list_number_evaluation(list_number, list_number_selection, selection):
    selectionsDictionary = {}
    if list_number != None or list_number_selection != None:
        try:
            selection = BeautifulSoup.select(selection[list_number], list_number_selection)
            selectionsDictionary.update({'list_number': list_number, 'list_number_selection': list_number_selection})
        except:
            if list_number == None:
                errorAttribute = 'list_number'
                correctAttribute = 'list_number_selection'
            elif list_number_selection == None:
                errorAttribute = 'list_number_selection'
                correctAttribute = 'list_number'
            else:
                raise
            raise AttributeError(correctAttribute + " can't be set without "
                    + errorAttribute)
    return selectionsDictionary, selection

class ArticleCrawler():
    """
    Example usage:
    investing = ArticleCrawler("http://www.investing.com")
    investing.new_request("/economic-calendar")
    investing.new_list(content_selection="#economicCalendarData tbody .js-event-item .event a", title="Headline")
    investing.addto_list(content_selection="#economicCalendarData tbody .js-event-item .flagCur span", title="Country", get_selection="title")
    investing.addto_list(content_selection="#economicCalendarData tbody .js-event-item .flagCur", title="Currency")
    investing.addto_list(content_selection="#economicCalendarData tbody .js-event-item .time", title="Time")
    investing.update_list()
    for object in investing.list:
        print(object['Time'] + '\t' + object['Currency'] + '\t' + object['Headline'])
    """
    def __init__(self, website):
        self.website = website
        self.list = []
        self.selections = []
        self.request = None
        self.db_file = os.path.join(DB_DIR, self.website.split(".", 1)[1] + ".db")

    def new_request(self, sub_link):
        request = requests.get(self.website + sub_link)
        self.soup = BeautifulSoup(request.text, "lxml")
        self.request = sub_link

    def new_list(self, content_selection, title, get_selection=None, list_number=None, list_number_selection=None, is_picture=False):
        self.list.clear()
        self.selections.clear()
        selectionsDictionary = {}
        selection = self.soup.select(content_selection)
        selectionsDictionary, selection = list_number_evaluation(list_number, list_number_selection, selection)
        for object in selection:
            if get_selection == None:
                self.list.append({title: object.getText().strip()})
            else:
                self.list.append({title: object.get(get_selection)})
        selectionsDictionary.update({'title': title, 'content_selection': content_selection, 'get_selection': get_selection, 'is_picture': is_picture})
        self.selections.append(selectionsDictionary)
        return self.list

    def addto_list(self, content_selection, title, get_selection=None, list_number=None, list_number_selection=None, is_picture=False):
        selectionsDictionary = {}
        selection = self.soup.select(content_selection)
        selectionsDictionary, selection = list_number_evaluation(list_number, list_number_selection, selection)
        for count,object in enumerate(selection):
            if get_selection == None:
                self.list[count].update({title: object.getText().strip()})
            else:
                self.list[count].update({title: object.get(get_selection)})
        selectionsDictionary.update({'title': title, 'content_selection': content_selection, 'get_selection': get_selection, 'is_picture': is_picture})
        self.selections.append(selectionsDictionary)
        return self.list

    # Not robust enough for anything other than hrafn:
    def addto_list_expandonlink(self, link_selection, content_selection, title, get_selection=None, list_number=None, list_number_selection=None, is_picture=False):
        selectionsDictionary = {}
        selection = self.soup.select(content_selection)
        selectionsDictionary, selection = list_number_evaluation(list_number, list_number_selection, selection)
        for count,object in enumerate(selection):
            link = object.get("href")
            request = requests.get(self.website + link)
            soup = BeautifulSoup(request.text, "lxml")
            selection = soup.select(link_selection)
            if is_picture:
                picture_link = selection[0].get("href")
                absolute_picture_path = os.path.join(picture_storage + os.path.split(picture_link)[1])
                picture = open(absolute_picture_path, 'wb')
                picture.write(requests.get(picture_link).content)
                picture.close()
                #self.list[count].update({title: absolute_picture_path, 'is_picture': True})
                self.list[count].update({title: absolute_picture_path})
            elif get_selection == None:
                #self.list[count].update({title: selection[0].getText().strip(), 'is_picture': False})
                self.list[count].update({title: selection[0].getText().strip()})
            else:
                self.list[count].update({title: selection[0].get(get_selection)})
        selectionsDictionary.update({'title': title, 'content_selection': content_selection, 'get_selection': get_selection, 'link_selection': link_selection, 'is_picture': is_picture})
        self.selections.append(selectionsDictionary)
    '''
    # Need to add support for list_number and list_number_selection
    def update_list(self):
        self.new_request(self.request)
        for selections in self.selections:
            selection = self.soup.select(selections['content_selection'])
            for count,object in enumerate(selection):
                if selections['get_selection'] == None:
                    self.list[count][selections['title']] = selection[count].getText().strip()
                else:
                    self.list[count][selections['title']] = selection[count].get(selections['get_selection'])
    '''
