#!/usr/bin/env python
# encoding: utf-8

import os
from selenium import webdriver
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800,600))
display.start()
driver = webdriver.Chrome()
driver.get("https://m.facebook.com")
print driver.page_source.encode('utf-8')
driver.quit()
display.stop()
