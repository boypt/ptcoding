from google.appengine.ext import db
#from beaker.cache import cache_region

class TwitterUser(db.Model):
    user = db.UserProperty()
    twitter_id = db.StringProperty()
    twitter_access_token = db.StringProperty()
    twitter_access_token_secret = db.StringProperty()
    last_retweeted_id = db.IntegerProperty()
    last_updated = db.DateTimeProperty(auto_now_add=True)

    #@cache_region("", "twitteruser")
#    @classmethod
#    def get_by_key_name(cls, *args, **kwargs):
#        super(TwitterUser, cls).get_by_key_name(*args, **kwargs)

class AppConfig(db.Model):
    config_key = db.StringProperty()
    config_value = db.StringProperty()

    #@cache_region("long_term", "app_config")
#    @classmethod
#    def get_by_key_name(cls, *args, **kwargs):
#        super(AppConfig, cls).get_by_key_name(*args, **kwargs)

class SubscribeContacts(db.Model):
    addr = db.StringProperty()
    stanza = db.StringProperty()
    add_time = db.DateTimeProperty(auto_now_add=True)

class SavedTweets(db.Model):
    tweet_id = db.IntegerProperty()
    pushed_flag = db.BooleanProperty()
    user = db.UserProperty()
    retweet_time = db.DateTimeProperty(auto_now_add=True)
    tweet_text = db.TextProperty()

