#!/usr/bin/env python

from glob import glob
import re
import os

import hrafnauga
import hrafnaklo

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
ITEMLIST = glob(WORK_DIR + "/content/*")
ITEMLIST.sort()


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


def run():
    content = hrafnaklo.SortHrafnContent(ITEMLIST)
    content = content.create_dictionary()
    for item in content:
        sorted_content = content.get(item)
        identifier = sorted_content.pop(0)
        #  sort_nicely(sorted_content)
        #  sorted_content.reverse()
        if identifier == 'image':
            slideshow = hrafnauga.showImage(sorted_content, 10)
            slideshow.show_picture()
            slideshow.run()
        elif identifier == 'video':
            videoshow = hrafnauga.PlayVideo()
            videoshow.run(sorted_content)
        elif identifier == 'web':
            while len(sorted_content) != 0:
                with open(sorted_content.pop(0)) as file:
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

if __name__ == '__main__':
    run()
