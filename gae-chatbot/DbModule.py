from google.appengine.ext import db

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

