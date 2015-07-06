#!/usr/bin/python
# -*- coding: utf-8 -*-

import smtplib
import credentials
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

def write_file(content):
    file_object = open(credentials.MAIL_FILE, 'a+')
    try:
        file_object.write(content)
    finally:
        file_object.close()


def read_file():
    file_object = open(credentials.MAIL_FILE)
    try:
        message = file_object.read()
    finally:
        file_object.close
    return message

def send_mail():

    message = """From: From Person <enjoygame>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    %s
    """%(read_file())

    try:
    	smtp = smtplib.SMTP()
    	smtp.connect(credentials.SERVER_ADDRAESS, credentials.SERVER_PORT)
    	smtp.login(credentials.SENDER_USERID, credentials.SENDER_PASSWD)
        for receive in credentials.RECEIVERS:
    	    smtp.sendmail(credentials.SENDER, receive, message)

    	smtp.quit()
    except Exception as e:
    	print e

def send_remend():
    content_txt = "唐娟,到时间发帖了，赶紧回家开权限！！link:",credentials.COMMENT_LINK.encode('utf8')
    #credentials.COMMENT_LINK

    message = """From: From Person <enjoygame>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    %s%s
    """%content_txt 
    try:
    	smtp = smtplib.SMTP()
    	smtp.connect(credentials.SERVER_ADDRAESS, credentials.SERVER_PORT)
    	smtp.login(credentials.SENDER_USERID, credentials.SENDER_PASSWD)

    	smtp.sendmail(credentials.SENDER, credentials.TANG, message)

    	smtp.quit()
    except Exception as e:
    	print e


def do_login(user_info):

    #browser = webdriver.Firefox()
    #browser = webdriver.Chrome(chromedriver)
    browser = webdriver.Chrome()
    browser.get(credentials.MYGROUP_URL)

    try:
        email = browser.find_element_by_name('email')
        email.send_keys(user_info[0])

        pw = browser.find_element_by_name('pass')
        pw.send_keys(user_info[1])

        login = browser.find_element_by_name('login')
        login.send_keys(Keys.RETURN)
    except Exception as e:
        logging.error(e)
        return

    select_language(browser)
    browser.get(credentials.MYGROUP_URL)

    return browser

def select_language(browser):
    browser.get("https://m.facebook.com/language.php")

    user_language = browser.find_element_by_css_selector("div[data-sigil] > strong")
    if (user_language.text == "English (US)"):
        return
    else:
         select_language = browser.find_element_by_css_selector('a[href^="/a/language.php?l=en_US"]')
         select_language.send_keys(Keys.RETURN)

