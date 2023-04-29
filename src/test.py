#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import tkinter
from tkinter import simpledialog
import urllib.request
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



# driver = webdriver.Chrome(r"C:\Program Files\Opera\58.0.3135.127\opera.exe")
# driver = webdriver.Chrome()
# driver = webdriver.Opera(r"C:\gitserver\FPLGUI\supportFiles\operadriver.exe")
driver = webdriver.Opera()
driver.get('https://www.simbrief.com/system/briefing.php')



# element = driver.find_element_by_id("dispinput")
elements = driver.find_elements_by_class_name("dispinput")
elements[0].send_keys('Sowintuu')
elements[1].send_keys('$GmbH@co.de')
elements[1].send_keys(Keys.ENTER)

html = driver.page_source
driver.quit()


html = html.encode("utf-8")

pass
# html = html.decode('iso-8859-15')
# print(html)
html = html.decode().split('\n')

for k in html:
    print(k)


# with urllib.request.urlopen('https://www.simbrief.com/system/briefing.php') as response:
#     html = response.read()
# 

pass



# class MyTest(object):
#         
#     
#     def __init__(self):
#         
#         # Read test file.
#         with open('opf.txt') as f:
#             simbriefOpfStr = f.read()
#         
#         
#         # Seperate in lines.
#         simbriefOpfStr = simbriefOpfStr.split('\n')
#         
#         
#         self.master = tkinter.Tk()
#         
#         
# if __name__ == '__main__':
#     myTest = MyTest()