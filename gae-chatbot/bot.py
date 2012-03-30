#coding:utf8
import bottle
from bottle import request, post, redirect, error, get
from bottle import jinja2_view as view

from google.appengine.api import xmpp

import logging
import tweepy

bottle.debug(True)

from beaker.middleware import SessionMiddleware
from google.appengine.ext import db
from google.appengine.api import users, taskqueue 

session_opts = {
    'session.cookie_expires': True,
    'session.type': 'ext:google',
}


consumer_key=None
consumer_secret=None
app_url = None

def config_check(func):
    def __check(*args, **kwargs):
        global consumer_key, consumer_secret, app_url
        if all(map(lambda x:x is None, (consumer_key, consumer_secret, app_url))):
            app_conf = AppConfig.get_by_key_name("consumer_token")
            app_addr = AppConfig.get_by_key_name("app_url")
            if app_conf is not None and app_addr is not None:
                consumer_key, consumer_secret = eval(app_conf.config_value)
                app_url = app_addr.config_value
                return func(*args, **kwargs)
            else:
                redirect("/tasks/config")
        else:
            return func(*args, **kwargs)

    return __check


class TwitterUser(db.Model):
    user = db.UserProperty()
    twitter_id = db.StringProperty()
    twitter_access_token = db.StringProperty()
    twitter_access_token_secret = db.StringProperty()
    last_retweeted_id = db.IntegerProperty()
    last_updated = db.DateTimeProperty(auto_now_add=True)

class AppConfig(db.Model):
    config_key = db.StringProperty()
    config_value = db.StringProperty()

class SubscribeContacts(db.Model):
    addr = db.StringProperty()
    stanza = db.StringProperty()
    add_time = db.DateTimeProperty(auto_now_add=True)

@get('/tasks/config')
@view("config")
def config():
    return {}

@post("/tasks/config")
@view("config")
def config_post():
    config_key = request.POST["key"]
    config_sec = request.POST["secret"]
    config_url = request.POST["app_url"]

    AppConfig.get_or_insert("consumer_token", 
            config_key = "consumer_token", 
            config_value = repr((config_key, config_sec)))
    AppConfig.get_or_insert("app_url", config_key = "app_url", config_value = config_url)

    return {}


@get("/tasks/subscribe")
@view("subscribe")
def man_subscribe():
    return dict(users = list(SubscribeContacts.all()))

@post("/tasks/subscribe")
@view("subscribe")
def man_subscribe_post():
    sender_addr = request.POST["addr"]
    SubscribeContacts.get_or_insert(sender_addr, addr = sender_addr, stanza = '')
    return dict(users = list(SubscribeContacts.all()))

@get("/send_direct")
@view("send_direct")
@config_check
def send_direct():
    return {}

@post("/send_direct")
@view("send_direct")
@config_check
def send_direct_post():
    msg = request.POST["msg"]
    for ct in SubscribeContacts.all():
        xmpp.send_message(ct.addr, msg)
    return dict(msg = msg.decode('utf-8'))

@get('/login')
@view("login")
def test_login():
    user = users.get_current_user()
    return dict(
            is_login = (user is None),
            login_url = users.create_login_url("/login"),
            logout_url = users.create_logout_url("/login"),
            nickname = '' if user is None else user.nickname()
            )

@get('/add_twitter')
@view("add_twitter")
@config_check
def add_twitter():
    user = users.get_current_user()
    if user is None:
        redirect("/login")
    else:
        session = request.environ.get('beaker.session')
        auth = session.get("twitter_auth") 
        verifier = request.GET.get('oauth_verifier')

        if auth is not None and auth.request_token is None:
            auth = None

        twi = TwitterUser.get_by_key_name(user.email())

        auth_url = ''
        if twi is None:

             #first
            if auth is None or verifier is None:
                auth = tweepy.OAuthHandler(consumer_key, consumer_secret, app_url + "/add_twitter")
                auth_url = auth.get_authorization_url()
                session["twitter_auth"] = auth
                session.save()
            else:
                try:
                    auth.get_access_token(verifier)
                except tweepy.TweepError:
                    error('Error! Failed to get access token.')

                twi = TwitterUser.get_or_insert(user.email(), 
                        user = user,
                        last_retweeted_id = 0,
                        twitter_access_token = auth.access_token.key,
                        twitter_access_token_secret = auth.access_token.secret,
                        twitter_id = auth.get_username())

                session["twitter_auth"] = None
                session.save()

        return dict(is_twitter_added = twi is not None, 
                    auth_url = auth_url,
                    twitter_id = '' if twi is None else twi.twitter_id,
                    remove_url = "/remove_twitter")

@get("/remove_twitter")
@view("message")
def remove_twitter():
    user = users.get_current_user()
    if user is None:
        redirect("/login")
    else:
        twi = TwitterUser.get_by_key_name(user.email())
        if twi is not None:
            twi.delete()
            msg = "deleted."
        else:
            msg = "not auth."

        return dict(message = msg)

@get('/tasks/newretweeted')
@config_check
def newretweeted():
    usr_res = TwitterUser.all()
    queue_cnt = 0
    for usr in usr_res:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(usr.twitter_access_token, usr.twitter_access_token_secret)

        api = tweepy.API(auth)
        #my_screen_name = api.me().screen_name
        rts = api.retweeted_by_me(since_id = usr.last_retweeted_id, count = 5)

        if len(rts) > 0:
            usr.last_retweeted_id = rts[0].id
            usr.put()
            for t in reversed(rts):
                tweet = u"via {0} RT @{1}: {2}".format(t.user.screen_name, 
                        t.retweeted_status.user.screen_name,
                        t.retweeted_status.text)
                taskqueue.add(url='/tasks/send_retweeted_msg', countdown = queue_cnt * 120,
                        params=dict(tweet = tweet))
                queue_cnt += 1

            yield "retweeted {0}".format(len(rts))
        else:
            yield "no new retweet "

@post("/tasks/send_retweeted_msg")
@config_check
def send_retweeted_msg():
    tweet = request.POST["tweet"]
    for ct in SubscribeContacts.all():
        xmpp.send_message(ct.addr, tweet)

#@post("/_ah/xmpp/message/chat/")
#def chat():
#    message = xmpp.Message(request.POST)
#    #message.reply("hi")

@post("/_ah/xmpp/subscription/subscribe/")
def subscribe():
    sender_addr = request.POST["from"].split('/')[0]
    stanza = request.POST["stanza"]
    ct = SubscribeContacts.get_or_insert(sender_addr)
    ct.addr = sender_addr
    ct.stanza = stanza
    ct.put()

@post("/_ah/xmpp/subscription/subscribed/")
def subscribed():
    logging.info(request.POST["stanza"])

@post("/_ah/xmpp/subscription/unsubscribe/")
def unsubscribe():
    sender_addr = request.POST["from"].split('/')[0]
    ct = SubscribeContacts.get_by_key_name(sender_addr)
    ct.delete()
    logging.info(request.POST["stanza"])

@post("/_ah/xmpp/subscription/unsubscribed/")
def unsubscribed():
    logging.info(request.POST["stanza"])

@post("/_ah/xmpp/error/")
def xmpp_error():
    error_sender = request.POST['from']
    error_stanza = request.POST['stanza']
    logging.error('XMPP error received from %s (%s)', error_sender, error_stanza)


app = SessionMiddleware(bottle.app(), session_opts)

