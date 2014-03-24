from google.appengine.ext import db

class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

def get_posts(offset=0, limit=10):
    q = db.Query(Post)
    q.order('-created')  # order posts from most recent to oldest
    return list(q.run(offset=offset, limit=limit))
