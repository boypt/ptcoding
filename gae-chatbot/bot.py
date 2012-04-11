#coding:utf8

#stdlib
import urllib
import logging
from datetime import date, timedelta

#gae api
from google.appengine.api import xmpp
from google.appengine.api import users, taskqueue 

#Third party
import tweepy
import bottle
bottle.debug(True)
from bottle import request, post, redirect, error, get
from bottle import jinja2_view as view
from beaker.middleware import SessionMiddleware

#custom module
from DbModule import TwitterUser, AppConfig, SubscribeContacts, SavedTweets

session_opts = {
    'session.cookie_expires': True,
    'session.type': 'ext:google',
}

tzdelta = timedelta(hours=8)

consumer_key=None
consumer_secret=None
app_url = None

def get_tweet_urls_text(tweet):
    entities = tweet.entities
    text = tweet.text

    if len(entities["urls"]) > 0:
        for url in entities["urls"]:
            expanded_url = url["expanded_url"]
            beg, end = url["indices"]
            text = text[:beg] + expanded_url + text[end:]

    if entities.has_key("media"):
        for media in entities["media"]:
            expanded_url = media["expanded_url"]
            beg, end = media["indices"]
            media_url = media["media_url"]
            text = text[:beg] + expanded_url + text[end:] + " PIC:" + media_url

    return text


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
    continue_url = request.GET.get('continue_url')
    user = users.get_current_user()
    return dict(
            is_login = (user is None),
            login_url = users.create_login_url("/login" if continue_url is None else continue_url),
            logout_url = users.create_logout_url("/login"), 
            nickname = '' if user is None else user.nickname()
            )

@get('/add_twitter')
@view("add_twitter")
@config_check
def add_twitter():
    user = users.get_current_user()
    if user is None:
        redirect("/login?{0}".format(urllib.urlencode(dict(continue_url=request.url))))
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
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    twitter_user = TwitterUser.all()
    queue_cnt = 0
    for usr in twitter_user:
        auth.set_access_token(usr.twitter_access_token, usr.twitter_access_token_secret)
        api = tweepy.API(auth)
        rts = api.retweeted_by_me(since_id = usr.last_retweeted_id, include_entities = True, count = 5)

        if len(rts) > 0:
            usr.last_retweeted_id = rts[0].id
            usr.put()
            for t in reversed(rts):
                tweet_text = u"RT @{0}: {1}".format(t.retweeted_status.user.screen_name, 
                                                get_tweet_urls_text(t.retweeted_status))
                msg_text = u"via {0} ".format(t.user.screen_name) + tweet_text

                taskqueue.add(url='/tasks/send_retweeted_msg', countdown = queue_cnt * 120,
                        params=dict(tweet = msg_text))

                queue_cnt += 1

                t = SavedTweets(user = usr.user, 
                        retweet_time = t.created_at,
                        tweet_text = tweet_text.replace('\n', ''))
                t.put()

            info = "schedualed {0} tweet(s).".format(len(rts))
        else:
            info = "no new retweet "

        logging.info(info)

@post("/tasks/send_retweeted_msg")
@config_check
def send_retweeted_msg():
    tweet = request.POST["tweet"]
    for ct in SubscribeContacts.all():
        xmpp.send_message(ct.addr, tweet)

@get('/review_tweets')
@view('review_tweets')
@config_check
def review_tweets():
    page = request.GET.get('page')
    user = users.get_current_user()
    if user is None:
        redirect("/login?{0}".format(urllib.urlencode(dict(continue_url=request.url))))
    twi = TwitterUser.get_by_key_name(user.email())
    query = SavedTweets.all()
    per_page = 20

    if page is None:
        page = 0
    else:
        page = int(page) - 1

    offset = page * per_page

    # last sunday
    today = date.today()
    last_sunday = today - timedelta(days = (today.weekday() - 6) % 7)

    week_tweets_query = query.filter("user =", user).filter("retweet_time >", last_sunday).order("-retweet_time")
    tweets_count = week_tweets_query.count()
    tweets  = week_tweets_query.fetch(limit = per_page, offset = offset)
    pages = (tweets_count / per_page) + 1
    pages_links = [("/review_tweets?page={0}".format(p), str(p)) for p in range(1, pages + 1)]


    return dict(since_time = last_sunday,
                twitter_id = twi.twitter_id,
                tweets = tweets,
                tzdelta = tzdelta,
                pages_links = pages_links)


#@post("/_ah/xmpp/message/chat/")
#def chat():
#    message = xmpp.Message(request.POST)
#    #message.reply("hi")

@post("/_ah/xmpp/subscription/subscribe/")
def subscribe():
    sender_addr = request.POST["from"].split('/')[0]
    stanza = request.POST["stanza"]
    SubscribeContacts.get_or_insert(sender_addr, addr = sender_addr, stanza = stanza)
    logging.info(stanza)

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

