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


consumer_key="4pwLIKnVUmCJipfUrsPlA"
consumer_secret="GiV7yylfiAZ1P4qVBf6yWuaQ6BYHhJ25EjzEWRkFk"
app_url = "http://ptchatbot.appspot.com"
#app_url = "http://127.0.0.1:8080"

class TwitterUser(db.Model):
    user = db.UserProperty()
    twitter_id = db.StringProperty()
    twitter_access_token = db.StringProperty()
    twitter_access_token_secret = db.StringProperty()
    last_retweeted_id = db.IntegerProperty()
    last_updated = db.DateTimeProperty(auto_now_add=True)


@route('/testsend')
def testsend_get():
    html = """<form name="input" action="/testsend" method="post">
Text: <input type="text" name="msg" /> <input type="submit" value="Submit" />
</form>"""
    return html

@post("/testsend")
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
def newretweeted():
    usr_res = db.GqlQuery("SELECT * FROM TwitterUser")

    for usr in usr_res:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(usr.twitter_access_token, usr.twitter_access_token_secret)

        api = tweepy.API(auth)
        my_screen_name = api.me().screen_name
        rts = api.retweeted_by_me(since_id = usr.last_retweeted_id, count = 5)

        if len(rts) > 0:
            usr.last_retweeted_id = rts[0].id
            usr.put()
            for i, t in enumerate(reversed(rts)):
                tweet = u"@{0}: {1}".format(t.retweeted_status.user.screen_name, t.text).encode("utf-8")
                taskqueue.add(url='/send_retweeted_msg', countdown = i * 60,
                        params=dict(twid = my_screen_name, tweet = tweet))

            yield "retweeted {0}".format(len(rts))
        else:
            yield "no new retweet for " + my_screen_name


@route("/test_put")
def test_put():

    twitter_id = "PT"
    tweet = u"@{0} :{1}".format("name", u"tweet中文").encode("utf-8")
    taskqueue.add(url='/send_retweeted_msg', countdown = 10,
            params=dict(twid = twitter_id, tweet = tweet))


@post("/send_retweeted_msg")
def send_retweeted_msg():
    tweet = request.POST["tweet"]
    twitter_id = request.POST["twid"]
    msg = "{0} RT: {1}".format(twitter_id, tweet)
    addr = "linux-party@im.partych.at"
    status_code = xmpp.send_message(addr, msg)
    

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

