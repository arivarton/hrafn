import requests
import os
from bs4 import BeautifulSoup

WORK_DIR = os.path.dirname(os.path.abspath(__file__))


def makeImageDatabaseDirectory(db_dir=None, img_name=None):
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    return os.path.join(db_dir, img_name)


def list_number_evaluation(list_number, list_number_selection, selection):
    selectionsDictionary = {}
    if list_number is not None or list_number_selection is not None:
        try:
            selection = BeautifulSoup.select(selection[list_number], list_number_selection)
            selectionsDictionary.update({'list_number': list_number,
                                         'list_number_selection': list_number_selection})
        except:
            if list_number is None:
                errorAttribute = 'list_number'
                correctAttribute = 'list_number_selection'
            elif list_number_selection is None:
                errorAttribute = 'list_number_selection'
                correctAttribute = 'list_number'
            else:
                raise
            raise AttributeError(correctAttribute + " can't be set without " +
                                 errorAttribute)
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
    def __init__(self, website, db_name, picture_storage):
        self.website = website
        self.dict = {'crawl': [], 'is picture': {}}
        self.selections = []
        self.request = None
        self.db_name = db_name
        self.picture_storage = picture_storage

    def new_request(self, sub_link):
        request = requests.get(self.website + sub_link)
        self.soup = BeautifulSoup(request.text, "lxml")
        self.request = sub_link

    def list_addition(self, new_list, **kwargs):
        selectionsDictionary = {}
        selection = self.soup.select(kwargs['content_selection'])
        selectionsDictionary, selection = list_number_evaluation(kwargs['list_number'],
                                                                 kwargs['list_number_selection'], selection)
        self.dict['is picture'].update({kwargs['title']: kwargs['is_picture']})
        for count, object in enumerate(selection):
            if kwargs['is_picture']:
                picture_link = self.website + object.get("href")
                absolute_picture_path = makeImageDatabaseDirectory(
                        db_dir=os.path.join(self.picture_storage, self.db_name, kwargs['title']),
                        img_name=os.path.split(picture_link)[1]
                        )
                with open(absolute_picture_path, 'wb') as picture:
                    picture.write(requests.get(picture_link).content)
                self.dict['crawl'][count].update({kwargs['title']: absolute_picture_path})
            elif kwargs['get_selection'] is None:
                if new_list:
                    self.dict['crawl'].append({kwargs['title']: object.getText().strip()})
                else:
                    self.dict['crawl'][count].update({kwargs['title']: object.getText().strip()})
            else:
                if new_list:
                    self.dict['crawl'].append({kwargs['title']: object.get(kwargs['get_selection'])})
                else:
                    self.dict['crawl'][count].update({kwargs['title']: object.get(kwargs['get_selection'])})
        selectionsDictionary.update({'title': kwargs['title'], 'content_selection': kwargs['content_selection'],
                                     'get_selection': kwargs['get_selection'], 'is_picture': kwargs['is_picture']})
        self.selections.append(selectionsDictionary)
        return self.dict

    def new_list(self, content_selection, title, get_selection=None, list_number=None,
                 list_number_selection=None, is_picture=False):
        self.selections.clear()
        return self.list_addition(new_list=True, content_selection=content_selection, title=title,
                                  get_selection=get_selection, list_number=list_number,
                                  list_number_selection=list_number_selection,
                                  is_picture=is_picture)

    def addto_list(self, content_selection, title, get_selection=None, list_number=None,
                   list_number_selection=None, is_picture=False):
        return self.list_addition(new_list=False, content_selection=content_selection, title=title,
                                  get_selection=get_selection, list_number=list_number,
                                  list_number_selection=list_number_selection,
                                  is_picture=is_picture)

    # Not robust enough for anything other than hrafn:
    def addto_list_expandonlink(self, link_selection, content_selection, title, get_selection=None,
                                list_number=None, list_number_selection=None, is_picture=False):
        selectionsDictionary = {}
        selection = self.soup.select(content_selection)
        selectionsDictionary, selection = list_number_evaluation(list_number,
                                                                 list_number_selection,
                                                                 selection)
        self.dict['is picture'].update({title: is_picture})
        for count, object in enumerate(selection):
            link = object.get("href")
            request = requests.get(self.website + link)
            soup = BeautifulSoup(request.text, "lxml")
            selection = soup.select(link_selection)
            if is_picture:
                picture_link = selection[0].get("href")
                absolute_picture_path = makeImageDatabaseDirectory(
                        db_dir=os.path.join(self.picture_storage, self.db_name, title),
                        img_name=os.path.split(picture_link)[1]
                        )
                with open(absolute_picture_path, 'wb') as picture:
                    picture.write(requests.get(picture_link).content)
                self.dict['crawl'][count].update({title: absolute_picture_path})
            elif get_selection is None:
                self.dict['crawl'][count].update({title: selection[0].getText().strip()})
            else:
                self.dict['crawl'][count].update({title: selection[0].get(get_selection)})
        selectionsDictionary.update({'title': title, 'content_selection': content_selection,
                                     'get_selection': get_selection, 'link_selection': link_selection,
                                     'is_picture': is_picture})
        self.selections.append(selectionsDictionary)
    '''
    # Need to add support for list_number and list_number_selection
    def update_list(self):
        self.new_request(self.request)
        for selections in self.selections:
            selection = self.soup.select(selections['content_selection'])
            for count,object in enumerate(selection):
                if selections['get_selection'] == None:
                    self.dict[count][selections['title']] = selection[count].getText().strip()
                else:
                    self.dict[count][selections['title']] = selection[count].get(selections['get_selection'])
    '''
