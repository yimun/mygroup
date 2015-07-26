# -*- coding: utf-8 -*-   

import sys 
from flask import Flask,request,abort
from flask import redirect, url_for,session,escape
from utils import get_user,header_render,require_login
from dae.api import doubanusers

from models.blog import Blog
from models.group import Group
from models.comment import Comment


# change default encoding to utf8
reload(sys) 
sys.setdefaultencoding('utf8') 

app = Flask(__name__)
app.config['DEBUG'] = True

@app.errorhandler(404)
def page_not_found(error):
    return header_render('404.html'), 404


@app.route('/')
@app.route('/blog/list/myfocus/')
def blog_list_myfocus():
    user = get_user()
    bloglist = None
    if user:
        bloglist = Blog.get_focus_blogs(user.id, 100)
    return header_render('blog_list.html', title="我关注的小组帖子", bloglist=bloglist)

# --------------------------------------------------------------------
@app.route('/group/create/',methods=['GET', 'POST'])
@require_login
def group_create():
    if request.method == 'POST':
        name = request.form['grp_name']
        intro = request.form['grp_intro']
        id = Group.create(name, intro, get_user().id)
        if not id:
            return header_render('group_create.html')
        return redirect(url_for('group_show',group_id = id))
    else:
        return header_render('group_create.html')

@app.route('/group/<group_id>/')
def group_show(group_id):
    group = Group.get(group_id)
    if group:
        creator = doubanusers.User(id=group.creator_id)
        blog_list = Blog.get_all_by_group(group_id)
        is_join = group.get_is_join(get_user().id)
        member_list = group.get_members()
        return header_render('group_show.html',group=group, creator = creator, 
                              blog_list = blog_list, is_join = is_join, member_list = member_list)
    else:
        abort(404)

@app.route('/group/join/<group_id>/')
def group_join(group_id):
    user = get_user()
    group = Group.get(group_id)
    if group.get_is_join(user.id):
        group.join_user(user.id, False)
    else:
        group.join_user(user.id, True)
    return redirect(url_for('group_show',group_id = group_id))
    
@app.route('/group/list/mine/')
@require_login
def group_list_mine():
    user = get_user()
    group_list = Group.get_user_groups(user.id)
    return header_render('group_list.html',title="我的小组",group_list=group_list)

@app.route('/group/list/hot/')
def group_list_hot():
    group_list = Group.get_hot_groups()
    return header_render('group_list.html',title="热门小组",group_list=group_list)

# --------------------------------------------------------------------

@app.route('/blog/create/<group_id>/',methods=['GET', 'POST'])
@require_login
def blog_create(group_id):
    group = Group.get(group_id)
    if request.method == 'POST':
        title = request.form['blog_title']
        content = request.form['blog_content']
        id = Blog.create(title, content, get_user().id, group_id)
        if not id:
            return header_render('blog_create.html', group = group)
        return redirect(url_for('blog_show',blog_id = id))
    else:
        return header_render('blog_create.html', group = group)

@app.route('/blog/list/hot/')
def blog_list_hot():
    bloglist = None
    bloglist = Blog.get_hot_blogs(100)
    return header_render('blog_list.html', title="热门帖子", bloglist=bloglist)

@app.route('/blog/list/myown/')
@require_login
def blog_list_myown():
    bloglist = None
    user = get_user()
    bloglist = Blog.get_user_post(user.id)
    return header_render('blog_list.html', title="我发布的帖子", bloglist=bloglist)

@app.route('/blog/<blog_id>/')
def blog_show(blog_id):
    blog = Blog.get(blog_id)
    user = get_user()
    if not user:
        is_join = False
    else:
        is_join = blog.get_is_join(user.id)
    comment_list = Comment.get_comments(blog_id)
    return header_render('blog_show.html', blog=blog, comment_list = comment_list, 
                         is_join = is_join)

# --------------------------------------------------------------------
@app.route('/comment/create/',methods=['POST'])
@require_login
def comment_create():
    content = request.form['content']
    blog_id = request.form['blog_id']
    id = Comment.create(blog_id, content, get_user().id)
    return redirect(url_for('blog_show',blog_id = blog_id))

@app.route('/comment/delete/<blog_id>/<comment_id>/')
@require_login
def comment_delete(blog_id, comment_id):
    comment = Comment.get(comment_id)
    comment.delete()
    return redirect(url_for('blog_show',blog_id = blog_id))




if __name__ == '__main__':
    app.run()
