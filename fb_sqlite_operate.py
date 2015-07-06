#/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import logging

import credentials
import fb_auto_mail

C_COMMENT_TABLE = 'c_comment_info'
P_COMMENT_TABLE = 'p_record_info'
C_GROUP_TABLE = 'c_group_info'

class fb_operate_db:
    def __init__(self, user_id):
        db_name = credentials.DB_FILE_PATH + user_id + ".db"
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_table();

    def create_table(self):
        c_comment_sql = "create table if not exists %s(id integer primary key autoincrement,\
                                                           comment_id varchar(20),\
                                                           group_id varchar(20),\
                                                           comment_num integer not null default 0,\
                                                           create_time timestamp NOT NULL default current_timestamp,\
                                                           update_time timestamp default NULL,\
                                                           post_time timestamp default NULL,\
                                                           is_new integer default 1,\
                                                           post_num integer default 0,\
                                                           user_id varchar(20))"\
                                                           %C_COMMENT_TABLE
    
        p_comment_sql = "create table if not exists %s(id integer primary key autoincrement,\
                                                           comment_id varchar(20),\
                                                           group_id varchar(20),\
                                                           user_id varchar(20),\
                                                           create_time TIMESTAMP NOT NULL DEFAULT current_timestamp)"\
                                                           %P_COMMENT_TABLE
    
        c_group_sql = "create table if not exists %s(id integer primary key autoincrement,\
                                                           group_id varchar(20),\
                                                           member_num integer NOT NULL DEFAULT 0,\
                                                           is_public integer NOT NULL DEFAULT -1,\
                                                           user_id varchar(20),\
                                                           create_time TIMESTAMP NOT NULL DEFAULT current_timestamp)"\
                                                           %C_GROUP_TABLE
        try:
            self.c.executescript("""%s;%s;%s;"""%(c_comment_sql, p_comment_sql, c_group_sql))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(e)
    
    def add_new_comment(self, comment, user_id):
        count_sql = "select count(*) from %s where comment_id='%s' and group_id='%s' and user_id='%s'"\
                    % (C_COMMENT_TABLE, comment[1], comment[0], user_id)
        try:
            self.c.execute(count_sql)
            count = self.c.fetchall()
    
            if count[0][0] > 0:
                exec_sql = "update %s set comment_num=%d,update_time=current_timestamp\
                            where comment_id=%s and group_id=%s"\
                                %(C_COMMENT_TABLE, comment[2], comment[1], comment[0])
            else:
                exec_sql = "insert into %s (group_id,comment_id,comment_num,user_id) values('%s','%s',%d,'%s')"\
                                %(C_COMMENT_TABLE, comment[0], comment[1], comment[2], user_id)
                logging.info("collect group_id->%s and comment->%s"\
                                , comment[0], comment[1])
    
                self.c.execute(exec_sql)
                self.conn.commit()
        except sqlite3.Error as e:
            logging.error(e)
    
    def add_new_post(self, comment, user_id):
        in_sql = "insert into %s(group_id,comment_id,user_id) values('%s','%s','%s')"\
                            %(P_COMMENT_TABLE, comment[0], comment[1], user_id)
        try:
            self.c.execute(in_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(e)
    
    
    def delete_no_exist_comment(self, comment, user_id):
        up_sql = "delete from %s \
                  where group_id='%s' and comment_id='%s' and user_id='%s'"\
                            %(C_COMMENT_TABLE, comment[0], comment[1], user_id)
        try:
            self.c.execute(up_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(e)
    
    def update_comment_old(self, comment, user_id):
        up_sql = "update %s set post_num=post_num+1,post_time=current_timestamp,is_new=0\
                  where group_id='%s' and comment_id='%s' and user_id='%s'"\
                            %(C_COMMENT_TABLE, comment[0], comment[1], user_id)
        try:
            self.c.execute(up_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(e)

    def get_comment_num(self, user_id):
        res_num = 0
        try:
            self.c.execute("select count(*) from %s where is_new=1 and comment_num>=5 and user_id='%s'"\
                %(C_COMMENT_TABLE, user_id))
            res = self.c.fetchall()
            res_num = int(res[0][0])
        except sqlite3.Error as e:
            logging.error(e)

        return res_num

    def get_comment(self, user_id, start_num, limit_num):
        sql_str = "select group_id,comment_id from %s where is_new=1 and comment_num>=5 and user_id='%s'\
            order by comment_num desc limit %d,%d"\
            %(C_COMMENT_TABLE, user_id, (start_num*limit_num), limit_num)

        try:
            self.c.execute(sql_str)
            comment_ids = self.c.fetchall()
        except sqlite3.Error as e:
            logging.error(e)

        return comment_ids

    def close_sqlite3(self):
        self.conn.close()







