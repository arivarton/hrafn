import tkinter as tk
from PIL import Image,ImageTk
from subprocess import call
from os import listdir, path
from glob import glob
from datetime import date
import pickle

WORK_DIR = path.dirname(path.abspath(__file__))

#Display images from a list
class showImage(tk.Tk):
    """
    Shows all images in a list/folder using Tkinter and
    then destroys the session.
    """
    def __init__(self, pictureList, displayTime):
        tk.Tk.__init__(self)
        self.attributes("-fullscreen", True)
        self.pictureFrame = tk.Label(self, background="black")
        self.pictureFrame.pack()
        self.pictureList = pictureList
        self.pictureCount = len(pictureList)
        self.imageDisplayTime = displayTime * 1000

    def showPicture(self):
        if(self.pictureCount <= 0):
            self.destroy()
        else:
            self.pictureCount -= 1
            imagePath = self.pictureList.pop()
            print("Image on display: " + imagePath)
            original = Image.open(imagePath)
            image = original.resize((self.winfo_screenwidth(),
                self.winfo_screenheight()),Image.ANTIALIAS)
            imageDisplay = ImageTk.PhotoImage(image)
            self.pictureFrame.image = imageDisplay
            self.pictureFrame.config(image=imageDisplay)
            self.pictureFrame.pack()
            self.after(self.imageDisplayTime, self.showPicture)

    def run(self):
        self.mainloop()

# Play videos from a list
class playVideo():
    """
    Plays video files using mplayer.
    """
    def run(self, fileList):
        for video in fileList:
            print("Playing video file: " + video)
            call(["mplayer", video, "-fs", "-zoom"])

# Show web content from a config file
class showWebContent(tk.Tk):
    """
    Shows content from websites
    """
    def __init__(self, content_list, content_placement, content_font, display_time=10, word_latency=1, imagePath=(WORK_DIR + "/images/background1.png")):
        """
        content_list must contain lists with 2 objects each, first the topic, second for content.
        """
        tk.Tk.__init__(self)
        self.content_list = content_list
        self.content_placement = content_placement
        self.content_font = content_font
        self.display_time = display_time * 1000
        self.word_latency = word_latency * 100
        self.windowWidth = self.winfo_screenwidth()
        self.windowHeight = self.winfo_screenheight()
        self.attributes("-fullscreen", True)
        self.contentCount = len(content_list['crawl'])
        self.windowCenterWidth = self.windowWidth / 2
        self.windowCenterHeight = self.windowHeight / 2
        original = Image.open(imagePath)
        image = original.resize(
            (self.windowWidth, self.windowHeight),Image.ANTIALIAS)
        self.imageDisplay = ImageTk.PhotoImage(image)
        self.canvas = tk.Canvas(self, width=self.windowWidth,
            height=self.windowHeight, background="black", highlightcolor="black",
            highlightbackground="black")
        self.canvas.create_image(self.windowCenterWidth, self.windowCenterHeight,
            image=self.imageDisplay)
        self.canvas_list = []
        self.time = None
        self.content = None
        self.backgroundImageIteration = 0
        self.backgroundImageCount = len(listdir(WORK_DIR + "/images/"))
        self.first_run = True

    def showInfo(self):
        self.image_display = None
        def dynamicWidth(value):
            if value.lower() == "center":
                return self.windowCenterWidth
            else:
                return value
        if(self.contentCount <= 0):
            self.destroy()
        else:
            self.contentCount -= 1
            #print('\n\n\n\n' + str(self.content_list) + '\n\n\n\n')
            web_content = self.content_list['crawl'].pop()
            for iter, value in enumerate(web_content):
                if self.first_run:
                    #print(value)
                    if self.content_list['is picture'][value]:
                        image_path = web_content[value]
                        print('First picture run ' + str(image_path))
                        original = Image.open(image_path)
                        image = original.resize(
                            (300, 300),Image.ANTIALIAS)
                        self.image_display = ImageTk.PhotoImage(original)
                        self.canvas_list.append(
                            self.canvas.create_image(
                                self.windowCenterWidth, self.windowCenterHeight, image=self.image_display
                            )
                        )
                    else:
                        self.canvas_list.append(
                            self.canvas.create_text(
                                dynamicWidth(self.content_placement[value]["Width"]),
                                self.content_placement[value]["Height"], justify=self.content_placement[value]["Justify"],
                                anchor=self.content_placement[value]["Anchor"], text=web_content[value], fill="white",
                                font=(self.content_font[value]["Type"], self.content_font[value]["Size"], self.content_font[value]["Weight"]), width=(self.windowWidth - 100)
                            )
                        )
                else:
                    if self.content_list['is picture'][value]:
                        image_path = web_content[value]
                        print('Second picture run ' + str(image_path))
                        original = Image.open(image_path)
                        image = original.resize(
                            (300, 300),Image.ANTIALIAS)
                        self.image_display = ImageTk.PhotoImage(image)
                        self.canvas_list.append(
                            self.canvas.create_image(
                                self.windowCenterWidth, self.windowCenterHeight, image=self.image_display
                            )
                        )
                    else:
                        self.canvas.itemconfigure(
                            self.canvas_list[iter], text=web_content[value]
                        )

            # Add 750 ms for each word in content
            if "Content" in web_content:
                added_time = len(web_content["Content"].split()) * self.word_latency
            else:
                added_time = 0
            self.canvas.pack()
            self.first_run = False
            self.after(self.display_time + added_time, self.showInfo)

    def run(self):
        self.mainloop()
