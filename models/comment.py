# -*- coding: utf-8 -*-
from models.model import Model
from models.blog import Blog
from dae.api.sqlstore import store
from dae.api import doubanusers



class Comment(Model):

    __table__ = 'mini_comment'

    __all__ = 'id, blog_id, content, create_time, creator_id'

    def __init__(self, id, blog_id, content, 
                 create_time, creator_id):
        self.id = id
        self.blog_id = blog_id
        self.content = content
        self.create_time = create_time
        self.creator_id = creator_id

    @classmethod
    def get(cls, id):
        sql = 'select {} from {} where id=%s'.format(cls.__all__, cls.__table__)
        rs = store.execute(sql, id)
        return cls(*rs[0]) if rs and rs[0] else None

    @classmethod
    def get_all(cls):
        sql = 'select {} from {}'.format(cls.__all__, cls.__table__)
        rs = store.execute(sql)
        return [cls(*r) for r in rs] if rs else None

    @classmethod
    def create(cls, blog_id, content, creator_id):
        sql = 'insert into {} (blog_id,content,creator_id) values(%s, %s, %s)'.format(cls.__table__)
        params = (blog_id, content, creator_id)
        id = store.execute(sql,params)
        store.commit()
        if id:
            blog = Blog.get(blog_id)
            blog.add_comment_count(1)
        return id

    def delete(self):
        sql = 'delete from {} where id=%s'.format(self.__table__)
        store.execute(sql, self.id)
        store.commit()
        blog = Blog.get(self.blog_id)
        blog.add_comment_count(-1)

    @classmethod
    def get_comments(cls, blog_id):
        sql = 'select {} from {} where blog_id=%s'.format(cls.__all__, cls.__table__)
        rs = store.execute(sql, blog_id)
        return [cls(*r) for r in rs] if rs else None

    def get_creator(self):
        creator = doubanusers.User(self.creator_id)
        return creator

