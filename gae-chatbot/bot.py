#coding:utf8

#stdlib
import urllib
import logging
import random
from datetime import datetime, date, timedelta
import simplejson

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
from beaker.cache import cache_regions, cache_region, region_invalidate
from beaker.util import parse_cache_config_options

#custom module
from DbModule import TwitterUser, AppConfig, SubscribeContacts, SavedTweets


cache_opts = {
    'cache.regions': 'short_term, long_term',
    'cache.short_term.type': 'ext:googlememcache',
    'cache.short_term.expire': 3600,
    'cache.long_term.type': 'ext:googlememcache',
    'cache.long_term.expire': 86400,
    }
cache_regions.update(**parse_cache_config_options(cache_opts)['cache_regions'])

consumer_key=None
consumer_secret=None
app_url = None

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_FORMAT_SHORT = "%d/%m %I:%M %p"
CSTTZ = timedelta(hours=8)

@cache_region("short_term")
def retrive_tweet_data(user, since_time, to_time):
    items_limit = 20
    week_tweets_query = SavedTweets.all().filter("user =", user).\
                                        filter("retweet_time >=", since_time).\
                                        filter("retweet_time <", to_time).\
                                        order("-retweet_time")
    tweets = week_tweets_query.fetch(limit = items_limit)
    return tweets

def get_tweet_urls_text(tweet):
    entities = tweet.entities
    tweet_text = tweet.text
    url_replaces = []
    pic_urls = []

    for url in entities["urls"]:
        url_replaces.append((url["expanded_url"], url["indices"]))

    if entities.has_key("media"):
        for media in entities["media"]:
            url_replaces.append((media["expanded_url"], media["indices"]))
            pic_urls.append(media["media_url"])

    if len(url_replaces) > 0:
        url_replaces.sort(key = lambda r:r[1][0])
        text = ''
        cur = 0
        for expanded_url, indices in url_replaces:
            beg, end = indices
            text += tweet_text[cur:beg]
            text += expanded_url
            cur = end
        if len(pic_urls) > 0:
            text += " PIC: " + " ".join(pic_urls)
    else:
        text = tweet_text

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
    return dict(key = consumer_key, secret = consumer_secret, app_url = app_url)

@post("/tasks/config")
@view("config")
def config_post():
    global consumer_key, consumer_secret, app_url
    config_key = request.POST["key"]
    config_sec = request.POST["secret"]
    config_url = request.POST["app_url"]

    AppConfig.get_or_insert("consumer_token", 
            config_key = "consumer_token", 
            config_value = repr((config_key, config_sec)))
    AppConfig.get_or_insert("app_url", config_key = "app_url", config_value = config_url)

    consumer_key, consumer_secret, app_url = config_key, config_sec, config_url

    return dict(key = consumer_key, secret = consumer_secret, app_url = app_url)


@get("/tasks/subscribe")
@view("subscribe")
def man_subscribe():
    return dict(users = SubscribeContacts.all().fetch(limit = 100))

@post("/tasks/subscribe")
@view("subscribe")
def man_subscribe_post():
    sender_addr = request.POST["addr"]
    SubscribeContacts.get_or_insert(sender_addr, addr = sender_addr, stanza = '')
    return dict(users = SubscribeContacts.all().fetch(limit = 100))

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
    for ct in SubscribeContacts.all().fetch(limit = 10):
        xmpp.send_message(ct.addr, msg)
    return dict(msg = msg.decode('utf-8'))

@get('/')
@get('/login')
@view("login")
def test_login():
    continue_url = request.GET.get('continue_url')
    user = users.get_current_user()
    return dict(
            is_logedin = (user is not None),
            login_url = users.create_login_url("/login" if continue_url is None else continue_url),
            logout_url = users.create_logout_url("/login"), 
            nickname = '' if user is None else user.nickname()
            )

@get('/twitter')
@view('twitter')
def twitter():
    user = users.get_current_user()
    if user is None:
        redirect("/login?{0}".format(urllib.urlencode(dict(continue_url=request.url))))

    twi = TwitterUser.get_by_key_name(user.email())

    return dict(is_twitter_added = twi is not None, 
            twitter_id = '' if twi is None else twi.twitter_id)


@get('/add_twitter')
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
                auth = tweepy.OAuthHandler(consumer_key, consumer_secret, request.url)
                auth_url = auth.get_authorization_url()
                session["twitter_auth"] = auth
                session.save()
                redirect(auth_url)
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

        redirect("/twitter")

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
    twitter_user = TwitterUser.all().fetch(limit = 100)
    random.shuffle(twitter_user)
    queue_cnt = 0
    for usr in twitter_user:
        auth.set_access_token(usr.twitter_access_token, usr.twitter_access_token_secret)
        api = tweepy.API(auth)
        rts = api.retweeted_by_me(since_id = usr.last_retweeted_id,
                                    include_entities = True, count = 30)

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
    for ct in SubscribeContacts.all().fetch(limit = 100):
        xmpp.send_message(ct.addr, tweet)

@get('/review_tweets')
@view('review_tweets')
@config_check
def review_tweets():
    user = users.get_current_user()
    if user is None:
        redirect("/login?{0}".format(urllib.urlencode(dict(continue_url=request.url))))

    twi = TwitterUser.get_by_key_name(user.email())
    if twi is None:
        return dict(is_twitter_missing = True, message = "You haven't link your twitter account.")

    to_time = request.GET.get('to_time')

    # last sunday
    today = date.today()
    last_sunday = today - timedelta(days = (today.weekday() - 6) % 7)

    if to_time is None:
        to_time = today + timedelta(days = 1)
    else:
        to_time = datetime.strptime(to_time, DATETIME_FORMAT)

    tweets = retrive_tweet_data(user, last_sunday, to_time)

    if request.is_ajax:
        return simplejson.dumps([dict(retweet_time = t.retweet_time.strftime(DATETIME_FORMAT),
                                    local_time = (t.retweet_time + CSTTZ).strftime(DATETIME_FORMAT_SHORT),
                                    tweet_text = t.tweet_text) for t in tweets])

    return dict(since_time = last_sunday,
                twitter_id = twi.twitter_id,
                tweets = tweets,
                datefmt = DATETIME_FORMAT,
                datefmt_short = DATETIME_FORMAT_SHORT,
                tzdelta = CSTTZ)

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

session_opts = {
    'session.cookie_expires': True,
    'session.type': 'ext:googlememcache',
}

app = SessionMiddleware(bottle.app(), session_opts)

