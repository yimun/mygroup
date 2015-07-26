# -*- coding: utf-8 -*-
from model import Model
from dae.api.sqlstore import store
from dae.api import doubanusers

from group import Group


class Blog(Model):

    __table__ = 'mini_blog'

    __all__ = 'id, title, content, comment_count, create_time, creator_id, group_id'

    def __init__(self, id, title, content, 
                 comment_count, create_time, creator_id, group_id):
        self.id = id
        self.title = title
        self.content = content
        self.comment_count = comment_count
        self.create_time = create_time
        self.creator_id = creator_id
        self.group_id = group_id

    def build_url(self):
        return '/blog/{}/'.format(self.id)

    @classmethod
    def get(cls, id):
        sql = 'select {all} from {table} where id=%s'.format(
            all = cls.__all__, table = cls.__table__)
        rs = store.execute(sql, id)
        return cls(*rs[0]) if rs and rs[0] else None

    @classmethod
    def get_all(cls):
        sql = 'select {all} from {table}'.format(
            all = cls.__all__, table = cls.__table__)
        rs = store.execute(sql)
        return [cls(*r) for r in rs] if rs else None

    @classmethod
    def create(cls, title, content, creator_id, group_id):
        sql = 'insert into {} (title,content,creator_id,group_id) values(%s, %s, %s, %s)'.format(cls.__table__)
        params = (title, content, creator_id, group_id)
        id = store.execute(sql,params)
        store.commit()
        return id

    def delete(self):
        sql = 'delete from {} where id=%s'.format(self.__table__)
        store.execute(sql, self.id)
        store.commit()

    @classmethod
    def get_all_by_group(cls, group_id):
        sql = 'select {all} from {table} where group_id=%s\
        order by create_time desc limit 50'.format(
            all = cls.__all__, table = cls.__table__)
        rs = store.execute(sql, group_id)
        return [cls(*r) for r in rs] if rs else None

    def get_author(self):
        creator = doubanusers.User(self.creator_id)
        return creator

    def get_group(self):
        group = Group.get(self.group_id)
        return group

    @classmethod
    def get_focus_blogs(cls, user_id, limit_count):
        sql ='''
            SELECT B.id, B.title, B.content, B.comment_count, B.create_time, B.creator_id, B.group_id
            FROM  `mini_blog` B
            WHERE EXISTS (

            SELECT * 
            FROM  `mini_belong` C
            WHERE C.user_id =%s
            AND C.group_id = B.group_id
            )
            ORDER BY B.create_time DESC 
            LIMIT %s 
            '''
        params = (user_id, limit_count)
        rs = store.execute(sql, params)
        return [cls(*r) for r in rs] if rs else None

    @classmethod
    def get_hot_blogs(cls, limit):
        sql = 'select {all} from {table} order by comment_count desc limit %s'.format(
            all = cls.__all__, table = cls.__table__)
        rs = store.execute(sql, limit)
        return [cls(*r) for r in rs] if rs else None

    @classmethod
    def get_user_post(cls, user_id):
        sql = 'select {all} from {table} where creator_id=%s order by create_time desc'.format(
            all = cls.__all__, table = cls.__table__)
        rs = store.execute(sql, user_id)
        return [cls(*r) for r in rs] if rs else None

    def get_is_join(self, user_id):
        sql = 'select * from `mini_belong` where user_id=%s and group_id=%s'
        params = (user_id, self.group_id)
        rs = store.execute(sql, params)
        return True if rs and rs[0] else False

    def add_comment_count(self, val):
        sql = 'update {} set comment_count=%s where id=%s'.format(self.__table__)
        params = (int(self.comment_count) + val, self.id)
        id = store.execute(sql,params)
        store.commit()
