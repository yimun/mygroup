# -*- coding: utf-8 -*-
from models.model import Model
from dae.api.sqlstore import store
from dae.api import doubanusers


class Group(Model):

    __table__ = 'mini_group'

    __all__ = 'id, name, intro, member_count, create_time, creator_id'

    def __init__(self, id, name, intro, 
                 member_count, create_time, creator_id):
        self.id = id
        self.name = name
        self.intro = intro
        self.member_count = member_count
        self.create_time = create_time
        self.creator_id = creator_id

    def build_url(self):
        return '/group/{}/'.format(self.id)

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
    def create(cls, name, intro, creator):
        sql = 'insert into {} (name,intro,creator_id) values(%s, %s, %s)'.format(cls.__table__)
        params = (name, intro, creator)
        id = store.execute(sql,params)
        store.commit()
        # add default belong
        if not id:
            return None
        sql = 'insert into `mini_belong` (user_id, group_id) values (%s, %s)'
        params = (creator, id)
        store.execute(sql, params)
        store.commit()
        return id
    
    def delete(self):
        sql = 'delete from {} where id=%s'.format(self.__table__)
        store.execute(sql, self.id)
        store.commit()
  
    # About member
    def add_member(self, user_id):
        sql = 'insert into `mini_belong` (user_id, group_id) values (%s, %s)'
        params = (user_id, self.id)
        store.execute(sql, params)
        store.commit()

    def get_members(self):
        sql = 'select user_id from `mini_belong` where group_id=%s'
        rs = store.execute(sql, self.id)
        return [doubanusers.User(r[0]) for r in rs] if rs else None

    @classmethod
    def get_user_groups(cls, user_id):
        sql = '''select A.id, A.name, A.intro, A.member_count, A.create_time, A.creator_id
               from {} A where exists(
               select * from `mini_belong` B 
               where B.user_id=%s and A.id=B.group_id) 
               '''.format(cls.__table__)
        rs = store.execute(sql, user_id)
        return [cls(*r) for r in rs] if rs else None

    @classmethod
    def get_hot_groups(cls):
        sql = 'select {} from {} order by member_count desc limit 20'.format(cls.__all__, cls.__table__)
        rs = store.execute(sql)
        return [cls(*r) for r in rs] if rs else None

    def get_is_join(self, user_id):
        sql = 'select * from `mini_belong` where user_id=%s and group_id=%s'
        params = (user_id, self.id)
        rs = store.execute(sql, params)
        return True if rs and rs[0] else False

