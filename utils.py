# -*- coding: utf-8 -*-   

from dae.api import doubanusers
from flask import render_template
from functools import wraps
from flask import redirect


## 轮子若干

def require_login(fun):
    @wraps(fun)
    def _(*args, **kwargs):
        user = get_user()
        if not user:
            return redirect(doubanusers.create_login_url("/"))
        return fun(*args, **kwargs)
    return _

def header_render(*args,**kwargs):
    user = get_user()
    url = None
    if user:
        url = doubanusers.create_logout_url("/")
    else:
        url = doubanusers.create_login_url("/")
    return render_template(url = url, user = user, *args, **kwargs)


def get_user():
    return doubanusers.get_current_user()
