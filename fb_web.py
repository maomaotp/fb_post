#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import sys
import credentials
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(process)d %(lineno)d %(message)s',\
                        datefmt='%Y %m-%d %H:%M:%S %p',\
                        filename= credentials.LOG_FILE,\
                        level=logging.INFO\
                        )

class web_operate:
    def __init__(self):
        self.browser = webdriver.Chrome()
        #browser = webdriver.Firefox()
        #browser = webdriver.Chrome(chromedriver)

    def get_url(self, url):
        self.browser.get(url)

    def get_browser(self):
        return self.browser

    def web_wait(self):
        WebDriverWait(self.browser, 10).until(lambda x: x.execute_script('return document.readyState') == 'complete')

    def find_element(self, href_str):
        link = self.browser.find_elements_by_css_selector('a[href^="%s"]' % href_str)
        return link

    #校验该页面是否存在post_link
    def verity_exist(self, post_link):
        return self.browser.find_elements_by_css_selector('a[href^="%s"]' % post_link)

    def write_content(self, post_content):
        inp = self.browser.find_element_by_id('composerInput')
        inp.send_keys(post_content)
        time.sleep(0.5)

    #获取发送失败的信息
    def find_post_error_message(self):
        inp = self.browser.find_element_by_css_selector('div#root span.mfsm > div')
        return inp.text

    def post_operate(self):
        btn = self.browser.find_element_by_css_selector('button[type="submit"][value="Post"]')
        btn.send_keys(Keys.RETURN)

    def do_login(self, user_info):
        self.get_url(credentials.MYGROUP_URL)

        try:
            email = self.browser.find_element_by_name('email')
            email.send_keys(user_info[0])

            pw = self.browser.find_element_by_name('pass')
            pw.send_keys(user_info[1])

            login = self.browser.find_element_by_name('login')
            login.send_keys(Keys.RETURN)
        except Exception as e:
            logging.error(e)

        self.select_language()
        self.browser.get(credentials.MYGROUP_URL)

    def select_language(self):
        self.browser.get("https://m.facebook.com/language.php")

        user_language = self.browser.find_element_by_css_selector("div[data-sigil] > strong")
        if (user_language.text == "English (US)"):
            return
        else:
             select_language = self.browser.find_element_by_css_selector('a[href^="/a/language.php?l=en_US"]')
             select_language.send_keys(Keys.RETURN)

    def get_group_ids(self):
        try:
            WebDriverWait(self.browser, 30).until(EC.title_contains("Groups Browser"))
            self.do_scroll(3, 2)
        except Exception as e:
            logging.error(e)

        group_ids = []
        try:
            root_elem = self.browser.find_element_by_css_selector("div#root")
            links = root_elem.find_elements_by_css_selector(\
                                'section > div > div > div > div > a[href^="/groups/"]')

            for link in map(lambda x: x.get_attribute('href'), links):
                # https://m.facebook.com/groups/266868887237?refid=27
                group_ids += re.findall(r"\.facebook\.com/groups/(\d+)", str(link))
        except Exception as e:
            logging.error(e)

        return group_ids

    def delete_china_tag(self, link):
        url = link + "/settings/?tab=settings&section=country_restrictions&view"
        self.browser.get(url)
        #value = browser.find_element_by_css_selector('.uiInputLabel  input#geo_gating_not_inverted')
        delete_tag = self.browser.find_element_by_css_selector('a[class="remove uiCloseButton uiCloseButtonSmall"][aria-label="Remove China"]')
        if (delete_tag):
            delete_tag.click()

            save = self.browser.find_element_by_css_selector('input[value="Save Changes"]')
            save.click()

    def add_china_tag(self, link):
        url = link + "/settings/?tab=settings&section=country_restrictions&view"
        self.browser.get(url)

        add_china = self.browser.find_element_by_css_selector('input[type="text"][placeholder="Enter country or countries"]')
        add_china.send_keys('china')
        time.sleep(3)
        add_china.send_keys(Keys.RETURN)
        #保存修改
        save = self.browser.find_element_by_css_selector('input[value="Save Changes"]')
        #save.click()
        save.send_keys(Keys.RETURN)

    def get_group_comment_ids(self, group_id):
        comment_tuples = []
        group_url = "https://m.facebook.com/groups/" + group_id

        self.browser.get(group_url)
        self.do_scroll(2, 2)
        comments = self.browser.find_elements_by_css_selector('span.cmt_def')

        for comment in comments:
            try:
                href = comment.find_element_by_xpath('..').get_attribute('href')
            except Exception as e:
                logging.error(e)

            comment_count_str = re.findall(r"(\d+) Comments", str(comment.text))
            if len(comment_count_str) > 0:
                comment_count = (int(comment_count_str[0]),)

                # https://m.facebook.com/groups/266868887237?view=permalink&id=10152905979522238&refid=18&_ft_
                comment_list = re.findall(r"\.facebook\.com/groups/(\d+)\?view=permalink&id=(\d+)", str(href))
                if(len(comment_list) > 0):
                    comment_tuple = [comment_list[0] + comment_count]
                    comment_tuples += comment_tuple

        return comment_tuples

    def judge_id(self, group_id, exclude_groups_id):
        res_code = 1
        if len(group_id) == 0:
            return res_code

        if group_id[0] in exclude_groups_id:
            logging.info("this group:%s is exclude", group_id)

        return res_code

    #翻页功能
    def do_scroll(self, n, t):
        # scroll n times
        for i in range(n):
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logging.debug('page %d', i)
            time.sleep(t)

    def exit_browser(self):
        self.browser.quit()
