#coding:utf8
import bottle
from bottle import route, request, post, redirect, error

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
group_addr=None
app_url = None

def config_check(func):
    def __check(*args, **kwargs):
        global consumer_key, consumer_secret, group_addr, app_url
        if all(map(lambda x:x is None, (consumer_key, consumer_secret, group_addr, app_url))):
            conf_res = db.GqlQuery("SELECT * FROM AppConfig WHERE config_key = :1 ", "consumer_token")
            if conf_res.count() > 0:
                conf = conf_res[0]
                consumer_key, consumer_secret = eval(conf.config_value)
                conf_addr = db.GqlQuery("SELECT * FROM AppConfig WHERE config_key = :1 ", "group_addr")
                addr = conf_addr[0]
                group_addr = addr.config_value
                conf_url = db.GqlQuery("SELECT * FROM AppConfig WHERE config_key = :1 ", "app_url")
                url = conf_url[0]
                app_url = url.config_value
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



@route('/tasks/config')
def config():
    conf_res = db.GqlQuery("SELECT * FROM AppConfig WHERE config_key = :1 ", "consumer_token")
    if conf_res.count() > 1:
        redirect("/login")
    else:
        html = """<form name="input" action="/tasks/config" method="post">
        key: <input type="text" name="key" /> 
        secret: <input type="text" name="secret" /> 
        group_addr: <input type="text" name="group_addr" /> 
        app_url: <input type="text" name="app_url" /> 
        <input type="submit" value="Submit" /> </form>"""
        return html

@post("/tasks/config")
def config_post():
    config_key = request.POST["key"]
    config_sec = request.POST["secret"]
    config_addr = request.POST["group_addr"]
    config_url = request.POST["app_url"]

    conf_res = db.GqlQuery("SELECT * FROM AppConfig WHERE config_key = :1 ", "consumer_token")
    if conf_res.count() < 1:
        cosm_tkn = AppConfig(config_key = "consumer_token", config_value = repr((config_key, config_sec)))
        cosm_tkn.put()
        group_addr = AppConfig(config_key = "group_addr", config_value = config_addr)
        group_addr.put()

        app_url = AppConfig(config_key = "app_url", config_value = config_url)
        app_url.put()

        yield "set"


@route('/testsend')
@config_check
def testsend_get():
    html = """<form name="input" action="/testsend" method="post">
Text: <input type="text" name="msg" /> <input type="submit" value="Submit" />
</form>"""
    return html

@post("/testsend")
@config_check
def testsend_post():
    msg = request.POST["msg"]
    addr = "linux-party@im.partych.at"
    status_code = xmpp.send_message(addr, msg)
    return testsend_get()

@route('/login')
def test_login():
    user = users.get_current_user()

    if user is None:
        yield '<a href="{0}">Login</a>'.format(users.create_login_url("/login"))
    else:
        yield 'hello, ' + user.nickname() 
        yield '<a href="{0}">Logout</a>'.format(users.create_logout_url("/login"))

@route('/add_twitter')
@config_check
def add_twitter():
    user = users.get_current_user()
    if user is None:
        redirect("/login")
    else:
        session = request.environ.get('beaker.session')
        usr_res = db.GqlQuery("SELECT * FROM TwitterUser WHERE user = :1 ", user)
        request_token = session.get("request_token") 
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret, app_url + "/add_twitter")
        verifier = request.GET.get('oauth_verifier')

         #first
        if request_token is None or verifier is None:
            uri = auth.get_authorization_url()
            session["request_token"] = (auth.request_token.key, auth.request_token.secret)
            session.save()
            redirect(uri)
        else:
            session["request_token"] = None
            session.save()

            auth.set_request_token(*request_token)

            try:
                auth.get_access_token(verifier)
            except tweepy.TweepError:
                error('Error! Failed to get access token.')

            if usr_res.count() > 0:
                usr = usr_res[0]
            else:
                usr = TwitterUser(user = user, last_retweeted_id = 0)

            usr.twitter_access_token = auth.access_token.key
            usr.twitter_access_token_secret = auth.access_token.secret
            usr.twitter_id = auth.get_username()
            usr.put()

            yield "Auth Succ." + usr.twitter_id

@route('/tasks/newretweeted')
@config_check
def newretweeted():
    usr_res = db.GqlQuery("SELECT * FROM TwitterUser")

    for usr in usr_res:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(usr.twitter_access_token, usr.twitter_access_token_secret)

        api = tweepy.API(auth)
        #my_screen_name = api.me().screen_name
        rts = api.retweeted_by_me(since_id = usr.last_retweeted_id, count = 5)

        if len(rts) > 0:
            usr.last_retweeted_id = rts[0].id
            usr.put()
            for i, t in enumerate(reversed(rts)):
                tweet = u"@{0}: {1}".format(t.retweeted_status.user.screen_name, t.text).encode("utf-8")
                taskqueue.add(url='/send_retweeted_msg', countdown = i * 120,
                        params=dict(tweet = tweet))

            yield "retweeted {0}".format(len(rts))
        else:
            yield "no new retweet "


@route("/test_put")
@config_check
def test_put():

    twitter_id = "PT"
    tweet = u"@{0} :{1}".format("name", u"tweet中文").encode("utf-8")
    taskqueue.add(url='/send_retweeted_msg', countdown = 10,
            params=dict(twid = twitter_id, tweet = tweet))


@post("/send_retweeted_msg")
@config_check
def send_retweeted_msg():
    tweet = request.POST["tweet"]
    status_code = xmpp.send_message(group_addr, tweet)
    

#@post("/_ah/xmpp/message/chat/")
#def chat():
#    message = xmpp.Message(request.POST)
#    #message.reply("hi")

@post("/_ah/xmpp/subscription/subscribe/")
def subscribe():
    from_addr = request.POST["from"]
    xmpp.send_invite(from_addr)
    logging.info(request.POST["stanza"])

@post("/_ah/xmpp/subscription/subscribed/")
def subscribed():
    logging.info(request.POST["stanza"])

@post("/_ah/xmpp/subscription/unsubscribe/")
def unsubscribe():
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

