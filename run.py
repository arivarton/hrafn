from glob import glob
import re
import os

import hrafnauga
import hrafnaklo

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
ITEMLIST = glob(WORK_DIR + "/content/*")
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
    return [tryint(c) for c in re.split('([0-9]+)', s)]


def sort_nicely(l):
    l.sort(key=alphanum_key)

for item in HRAFNDICTIONARY:
    list = HRAFNDICTIONARY.get(item)
    if list[0] == 'image':
        del list[0]
        sort_nicely(list)
        list.reverse()
        slideshow = hrafnauga.showImage(list, 10)
        slideshow.show_picture()
        slideshow.run()
    elif list[0] == 'video':
        del list[0]
        sort_nicely(list)
        list.reverse()
        videoshow = hrafnauga.PlayVideo()
        videoshow.run(list)
    elif list[0] == 'web':
        del list[0]
        sort_nicely(list)
        list.reverse()
        while len(list) != 0:
            with open(list.pop()) as file:
                db_name = os.path.basename(file.name)
                cleanup = file.readlines()
                # db_name is equal to content file name
                crawler = hrafnaklo.WebCrawler(db_name=db_name,
                                               picture_storage=os.path.join(WORK_DIR, 'db/images'))
                crawled = crawler.run(config_file=cleanup)
                font_and_placement = hrafnaklo.WebFontAndPlacement.run(cleanup)
            webshow = hrafnauga.showWebContent(crawled,
                                               content_placement=font_and_placement['Placement'],
                                               content_font=font_and_placement['Font'],
                                               display_time=crawled['Display time'], word_latency=0)
            webshow.show_info()
            webshow.run()
