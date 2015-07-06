#/usr/bin/env python
# -*- coding: utf-8 -*-

"""this script  auto post comment in facebook"""

#import sys
import time
import datetime
import re
import logging
import random
import string
import multiprocessing
import os

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from pyvirtualdisplay import Display

import credentials
import fb_auto_mail
import fb_sqlite_operate
import fb_web
import gs


logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(lineno)d %(message)s',\
                datefmt='%Y %m-%d %H:%M:%S %p',\
                filename= credentials.LOG_FILE,\
                level=logging.INFO\
                )

CHROMEDRIVER = '/usr/local/bin/chromedriver'

os.environ['webdriver.chrome.driver'] = CHROMEDRIVER

def gen_random_str(size=6,chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def add_record(comment):
    db.add_new_post(comment,user_id)
    db.update_comment_old(comment,user_id)

def post_interval(start_time):
    now_time = datetime.datetime.now()

    if (now_time - start_time).seconds >= credentials.SECOND_INTERVAL:
        sleep_time = random.randint(credentials.IN_SLEEP_MIN, credentials.IN_SLEEP_MAX)
        logging.info('Has been sent for %d seconds and now sleep %d', credentials.SECOND_INTERVAL, sleep_time)
        time.sleep(sleep_time)
        return now_time
    else:
        return start_time

def filtrate_group(group_id):
    shield_groups = credentials.exclude_group_ids
    if group_id in shield_groups:
        return False

    if group_id in french_groups_id:
        if sys.argv[1] != credentials.FRENCH:
            logging.info("this group %s in french_group and this is not french command", group_id)
            return False
    else:
        if sys.argv[1] == credentials.FRENCH:
            logging.info("this group:%s not french_group and this is french command", group_id)
            return False

    return True

def collect_group(web):
    group_ids = []
    comment_ids = []

    logging.info('start collect %s comment message..', sys.argv[1])

    group_ids = web.get_group_ids()

    for group_id in group_ids:
        if filtrate_group(group_id):
            logging.info("collect this group:%s comments", group_id)
            comment_ids += web.get_group_comment_ids(group_id)
        else:
            logging.info("this group:%s is mismatch condition!", group_id)

    for comment in comment_ids:
        db.add_new_comment(comment, user_id)

def googledocs_group(web):
    logging.info('start collect French comment message..')

    group_ids = []
    comment_ids = []

    for group_id in french_groups_id:
        logging.info("group_id:%s", group_id)
        comment_ids += web.get_group_comment_ids(group_id)

    for comment in comment_ids:
        db.add_new_comment(comment, user_id)

#校验发送结果，如果返回0则退出循环
def verify_post_result(web, comment_url, comment):
    global post_num

    #判断是否发送成功
    time.sleep(2)
    post_link = web.verity_exist(credentials.COMMENT_LINK)
    if len(post_link) > 0:
        post_num += 1
        logging.info('new post[%d]:%s', post_num, comment_url)
        add_record(comment)
        time.sleep(random.randint(credentials.POST_SLEEP_MIN, credentials.POST_SLEEP_MAX))
    else:
        logging.error('post failed,%s', comment_url)
        '''
        try:
            error_message = web.find_post_error_message()
            logging.error(error_message)
        except Exception as e:
            logging.error("Look for error messages failed:%s", e)
            return 1

        for locked_str in credentials.fb_locked_strs:
            res = re.search(locked_str, error_message)
            if res:
                logging.error(credentials.fb_locked_str)
                return 0
        '''

def post_comment_operate(web, comment_url, comment):
    index = random.randint(0, len(credentials.COMMENT_CONTENT)-1)

    if sys.argv[1] == credentials.BRAZIL:
        post_string = credentials.COMMENT_HEAD + credentials.COMMENT_LINK + credentials.COMMENT_CONTENT[index]
    else:
        post_string = credentials.COMMENT_CONTENT[index] + credentials.COMMENT_LINK

    web.write_content(post_string)

    try:
        web.post_operate()
    except Exception:
        logging.error("post comment error")

    return 1

def verity_has_posted(web):
    old_links = web.find_element(credentials.COMMENT_LINK)

    if len(old_links) >= 1:
        return 0
    return 1


#发评论功能   成功返回1 失败返回0
def post_comments(web):
    cur_day_comment_num = db.get_comment_num(user_id)
    logging.info('start post,task number:%d', cur_day_comment_num)

    start_num = 0
    limit_num = 10
    start_time = datetime.datetime.now()

    while 1:
        comment_ids = db.get_comment(user_id, start_num, limit_num)
        if len(comment_ids) == 0:
            break
        start_num += 1

        for comment in comment_ids:
            if post_comment(web, comment) == 0:
                break
            start_time = post_interval(start_time)

    return 1

#发评论功能   成功返回1 失败返回0
def post_comment(web, comment):
    comment_url = "https://m.facebook.com/groups/%s?view=permalink&id=%s" % comment

    try:
        web.get_url(comment_url)
        web.web_wait()

        # stop by 2s
        web.do_scroll(1, 2)

    except Exception as e:
        logging.error(e)

    try:
        #寻找页面是否存在已经发过的评论
        if verity_has_posted(web) == 0:
            logging.info('skip,%s', comment_url)
            db.update_comment_old(comment, user_id)
        else:
            # add new comment
            if post_comment_operate(web, comment_url, comment) != 0:
                #判断是否发送成功
                if verify_post_result(web, comment_url, comment) == 0:
                    return 0

    except Exception as e:
        logging.error(e)
    return 1

def add_task(user_info):
    try:
        global user_id
        global post_num
        global db
        post_num = 0
        user_id = user_info[0]

        db = fb_sqlite_operate.fb_operate_db(user_id)

        logging.info("start new user:%s PID:%d", user_id,os.getpid())
        web = fb_web.web_operate()
        web.do_login(user_info)

        #从网页获取群组ID和帖子ID，讲数据更新入sqlite3

        if sys.argv[1] == credentials.FRENCH:
            googledocs_group(web)
        else:
            collect_group(web)

        #自动回帖操作
        res = post_comments(web)
        if res == 0:
            content = "[%s]:%si\n"%(user_info[0], credentials.fb_locked_str)
            fb_auto_mail.write_file(content)
    except Exception as e:
        logging.error(e)
    finally:
        record_str = "[%s]:post comment number %d\n"%(user_id, post_num)
        logging.info("DOWN QUIT,%s", record_str)
        web.exit_browser()
        db.close_sqlite3()
        fb_auto_mail.write_file(record_str)

def open_limit():
    try:
        web = fb_web.web_operate()
        web.do_login(credentials.CONTROL_ACCOUNT)
        web.delete_china_tag(credentials.COMMENT_LINK)
        logging.info("open limit successed")
    except Exception as e:
        fb_auto_mail.write_file("delete china tab error--" + credentials.COMMENT_LINK + "\n")
        logging.error(e)
    finally:
        web.exit_browser()

def close_limit():
    try:
        web = fb_web.web_operate()
        web.do_login(credentials.CONTROL_ACCOUNT)
        web.add_china_tag(credentials.COMMENT_LINK)
        logging.info("close limit successed")
    except Exception as e:
        fb_auto_mail.write_file("add china tag error--" + credentials.COMMENT_LINK + "\n")
        logging.error(e)
    finally:
        web.exit_browser()


def read_from_googledocs():
    g = gs.gs_operate()
    g.login()
    return g.open_by_url()

def start_task_process():
    pool = multiprocessing.Pool(1)
    #pool.map(add_task, credentials.USER_INFO)
    pool.map_async(add_task, credentials.USER_INFO)
    pool.close()
    pool.join()

def main():
    if (len(sys.argv) < 2):
        print "./fb_auto_commenter.py Brazil/English/French"
        return

    fb_auto_mail.write_file("---------------------------" + sys.argv[1] + "\n")

    try:
        display = Display(visible=0, size=(800,600))
        display.start()
        #打开区域权限
        logging.info(">>>>>>>open limit")
        open_limit()
        #读取googledocs 群组信息
        logging.info(">>>>>>>read from google docs")
        global french_groups_id
        french_groups_id = read_from_googledocs()
        #french_groups_id = ['309490585766406', '745769152175443', '1393190844256106', '1384933575085078', '1458512047714028', '1581747275377893', '778025652245798', '252563551503667', '1468450793419237']
        logging.info(french_groups_id)

        #打开任务进程
        logging.info(">>>>>>>start post task")
        start_task_process()

        #关闭权限
        logging.info(">>>>>>>close limit")
        close_limit()

        logging.info(">>>>>>>send result mail")
        fb_auto_mail.send_mail()
    except Exception as e:
        logging.error(e)
    finally:
        logging.info("end")
        display.stop()

if __name__ == '__main__':
    main()

