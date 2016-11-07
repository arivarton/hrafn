from glob import glob
import re
from hrafnauga import *
import hrafnaklo
import crawler
from os import path

HRAFNPATH = path.dirname(path.abspath(__file__))
ITEMLIST = glob(HRAFNPATH + "/content/*")
ITEMLIST.sort()
HRAFN = hrafnaklo.SortHrafnContent(ITEMLIST)
HRAFNDICTIONARY = HRAFN.create_dictionary()

# from http://nedbatchelder.com/blog/200712/human_sorting.html
def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    l.sort(key=alphanum_key)

for item in HRAFNDICTIONARY:
    list = HRAFNDICTIONARY.get(item)
    if list[0] == 'image':
        del list[0]
        sort_nicely(list)
        list.reverse()
        slideshow = showImage(list, 10)
        slideshow.showPicture()
        slideshow.run()
    elif list[0] == 'video':
        del list[0]
        sort_nicely(list)
        list.reverse()
        videoshow = playVideo()
        videoshow.run(list)
    elif list[0] == 'web':
        del list[0]
        sort_nicely(list)
        list.reverse()
        while len(list) != 0:
            with open(list.pop()) as file:
                db_name = path.basename(file.name)
                cleanup = file.readlines()
                crawler = hrafnaklo.WebCrawler()
                crawled = crawler.run(db_name=db_name, config_file=cleanup)
                font_and_placement = hrafnaklo.WebFontAndPlacement.run(cleanup)
                print(font_and_placement)
            webshow  = showWebContent(crawled, content_placement=font_and_placement['Placement'], content_font=font_and_placement['Font'], display_time=5, word_latency=0)
            webshow.showInfo()
            webshow.run()
