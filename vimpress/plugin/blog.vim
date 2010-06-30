" Copyright (C) 2007 Adrien Friggeri.
" Copyright (C) 2010 BOYPT
"
" This program is free software; you can redistribute it and/or modify
" it under the terms of the GNU General Public License as published by
" the Free Software Foundation; either version 2, or (at your option)
" any later version.
"
" This program is distributed in the hope that it will be useful,
" but WITHOUT ANY WARRANTY; without even the implied warranty of
" MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
" GNU General Public License for more details.
"
" You should have received a copy of the GNU General Public License
" along with this program; if not, write to the Free Software Foundation,
" Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.  
" 
" Maintainer:	Adrien Friggeri <adrien@friggeri.net>
"               BOYPT <pentie@gmail.com>
" URL:		http://www.friggeri.net/projets/vimblog/
"           http://pigeond.net/blog/2009/05/07/vimpress-again/
"           http://pigeond.net/git/?p=vimpress.git
"           http://apt-blog.net
" Version:	1.0
" Last Change:  2010 June 27
"
" Commands :
" ":BlogList [<count>]"
"   Lists articles in the blog, defaultly show recent 10, arg to specify.
" ":BlogNew"
"   Opens page to write new article
" ":BlogOpen <id>"
"   Opens the article <id> for edition
" ":BlogPub"
"   Publish to the blog
" ":BlogSave"
"   Saves the article as draft.
" ":BlogUpload <file>"
"   Upload media file to blog. Appends img element after cursor.
"
" Configuration : 
"   Edit the "Settings" section (starts at line 51).
"
" Usage : 
"   Just fill in the blanks, do not modify the highlighted parts and everything
"   should be ok.

if !has("python")
    finish
endif

command! -nargs=? BlogList exec('py blog_list_posts(<f-args>)')
command! -nargs=0 BlogNew exec("py blog_new_post()")
command! -nargs=0 BlogPub exec("py blog_send_post(1)")
command! -nargs=0 BlogSave exec("py blog_send_post(0)")
command! -nargs=1 BlogOpen exec('py blog_open_post(<f-args>)')
command! -nargs=1 -complete=file BlogUpload exec('py blog_upload_media(<f-args>)')
python <<EOF
# -*- coding: utf-8 -*-
import urllib , urllib2 , vim , xml.dom.minidom , xmlrpclib , sys , string , re, os, mimetypes

#####################
#      Settings     #
#####################

blog_username = 'user'
blog_password = 'pass'
blog_url = 'http://local.blog/xmlrpc.php'

#####################
# Do not edit below #
#####################

handler = xmlrpclib.ServerProxy(blog_url).metaWeblog
edit_mode = True

def __exception_check(func):
    def __check(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except xmlrpclib.Fault, e:
            sys.stderr.write("xmlrpc error: %s" % e.faultString.encode("utf-8"))
        except xmlrpclib.ProtocolError, e:
            sys.stderr.write("xmlrpc error: %s %s" % (e.url, e.errmsg))
        except IOError, e:
            sys.stderr.write("network error: %s" % e)

    return __check

def blog_edit_on(switch = True):
    global edit_mode
    if edit_mode != switch:
        edit_mode = switch
        for i in ["i","a","s","o","I","A","S","O"]:
            if switch:
                vim.command('unmap %s' % i)
            else:
                vim.command("map %s <nop>" % i)

@__exception_check
def blog_send_post(publish):

    def get_line(what):
        start = 0
        while not vim.current.buffer[start].startswith('"'+what):
            start +=1
        return start

    def get_meta(what): 
        start = get_line(what)
        end = start + 1
        while not vim.current.buffer[end][0] == '"':
            end +=1
        return " ".join(vim.current.buffer[start:end]).split(":")[1].strip()
        
    strid = get_meta("StrID")
    title = get_meta("Title")
    slug = get_meta("Slug").replace(" ", "-")
    cats = [i.strip() for i in get_meta("Cats").split(",")]
    tags = get_meta("Tags")
  
    text_start = 0
    while not vim.current.buffer[text_start] == "\"========== Content ==========":
        text_start +=1
    text_start +=1
    text = '\n'.join(vim.current.buffer[text_start:])

    content = text

    post = dict(title = title, description = content,
            categories = cats, mt_keywords = tags,
            wp_slug = slug)

    if strid == '':
        strid = handler.newPost('', blog_username,
            blog_password, post, publish)
        vim.current.buffer[get_line("StrID")] = "\"StrID : %s" % strid
        notify = "Blog %s.   ID=%s" % ("Published" if publish else "Saved", strid)
    else:
        handler.editPost(strid, blog_username,
            blog_password, post, publish)
        notify = "Blog Edited. %s.   ID=%s" %  ("Published" if publish else "Saved", strid)

    sys.stdout.write(notify)
    vim.command('set nomodified')


@__exception_check
def blog_new_post():

    def blog_get_cats():
        l = handler.getCategories('', blog_username, blog_password)
        return ", ".join([i["description"].encode("utf-8") for i in l])

    del vim.current.buffer[:]
    blog_edit_on(True)
    vim.command("set syntax=blogsyntax")

    vim.current.buffer[0] =   "\"=========== Meta ============\n"
    vim.current.buffer.append("\"StrID : ")
    vim.current.buffer.append("\"Title : ")
    vim.current.buffer.append("\"Slug  : ")
    vim.current.buffer.append("\"Cats  : %s" % blog_get_cats())
    vim.current.buffer.append("\"Tags  : ")
    vim.current.buffer.append("\"========== Content ==========\n")
    vim.current.buffer.append("\n")

    vim.current.window.cursor = (len(vim.current.buffer), 0)
    vim.command('set nomodified')
    vim.command('set textwidth=0')

@__exception_check
def blog_open_post(post_id):
    post = handler.getPost(post_id, blog_username, blog_password)
    blog_edit_on(True)
    vim.command("set syntax=blogsyntax")

    del vim.current.buffer[:]
    vim.current.buffer[0] =   "\"=========== Meta ============\n"
    vim.current.buffer.append("\"StrID : "+str(post_id))
    vim.current.buffer.append("\"Title : "+(post["title"]).encode("utf-8"))
    vim.current.buffer.append("\"Slug  : "+(post["wp_slug"]).encode("utf-8"))
    vim.current.buffer.append("\"Cats  : "+",".join(post["categories"]).encode("utf-8"))
    vim.current.buffer.append("\"Tags  : "+(post["mt_keywords"]).encode("utf-8"))
    vim.current.buffer.append("\"========== Content ==========\n")

    content = (post["description"]).encode("utf-8")
    for line in content.split('\n'):
        vim.current.buffer.append(line)
    text_start = 0

    while not vim.current.buffer[text_start] == "\"========== Content ==========":
        text_start +=1
    text_start +=1

    vim.current.window.cursor = (text_start+1, 0)
    vim.command('set nomodified')
    vim.command('set textwidth=0')
    vim.command('unmap <enter>')

def blog_list_edit():
    row,col = vim.current.window.cursor
    id = vim.current.buffer[row-1].split()[0]
    blog_open_post(int(id))

@__exception_check
def blog_list_posts(count = "10"):
#    lessthan = handler.getRecentPosts('',blog_username, blog_password,1)[0]["postid"]
#    size = len(lessthan)
    allposts = handler.getRecentPosts('',blog_username, blog_password,int(count))
    del vim.current.buffer[:]
    vim.command("set syntax=blogsyntax")
    vim.current.buffer[0] = "\"====== List of Posts ========="
    for p in allposts:
        #vim.current.buffer.append(("".zfill(size-len(p["postid"])).replace("0", " ")+p["postid"])+"\t"+(p["title"]).encode("utf-8"))
        title = "%(postid)s\t%(title)s" % p
        vim.current.buffer.append(title.encode('utf8'))
        vim.command('set nomodified')
    blog_edit_on(False)
    vim.current.window.cursor = (2, 0)
    vim.command('map <enter> :py blog_list_edit()<cr>')

@__exception_check
def blog_upload_media(file_path):
    if not os.path.exists(file_path):
        sys.stderr.write("File not existed: %s" % file_path)
        return

    name = os.path.basename(file_path)
    type = mimetypes.guess_type(file_path)[0]
    with open(file_path, 'r') as f:
        bits = xmlrpclib.Binary(f.read())
    ret = handler.newMediaObject(1, blog_username, blog_password, 
            dict(name = name, type = type, bits = bits))
    img = "<img src=\"%s\" />" % ret["url"]
    row = vim.current.window.cursor[0]
    vim.current.buffer[row - 1] += img



