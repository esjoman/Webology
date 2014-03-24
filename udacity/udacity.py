import webapp2
import string
import cgi
import re
import os
import jinja2
import models.Blog as Blog


USER_RE = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
PASS_RE = re.compile(r'^.{3,20}$')
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
JINJA_ENV = jinja2.Environment(autoescape=True, 
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')))


class RequestWrangler(webapp2.RequestHandler):
    """
    Extends webapp2's RequestHandler to serve as a base class for
    rendering templates and writing out responses
    """
    def render(self, template, **kwargs):
        t = JINJA_ENV.get_template(template)
        self.response.write(t.render(kwargs))


class HomePage(RequestWrangler):
    template = 'index.html'
    
    def get(self):
        self.render(self.template)


class HelloUdacityPage(RequestWrangler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, Udacity!')


class ROT13Page(RequestWrangler):
    template = 'rot13.html'
    
    def get(self):
        self.render(self.template, text='')
    
    def post(self):
        user_text = str(self.request.get('text'))
        rot13_text = self.rot13(user_text)
        self.render(self.template, text=rot13_text)
    
    def rot13(self, s):
        lc = string.ascii_lowercase
        uc = string.ascii_uppercase
        trans_lower = string.maketrans(lc, lc[13:] + lc[:13])
        trans_upper = string.maketrans(uc, uc[13:] + uc[:13])
        return s.translate(trans_lower).translate(trans_upper)


class SignupPage(RequestWrangler):
    template = 'signup.html'
    
    def write_page(self, username='', username_error='', 
                   password_error='', verify_error='', email='', 
                   email_error=''):
        replace = {'username': username, 
                   'username_error': username_error, 
                   'password_error': password_error,
                   'verify_error': verify_error, 
                   'email': email, 
                   'email_error': email_error}
        self.render(self.template, **replace)
    
    def get(self):
        self.write_page()
    
    def post(self):
        username = self.request.get('username', '')
        password = self.request.get('password', '')
        verify = self.request.get('verify', '')
        email = self.request.get('email', '')
        kwargs = {'username': username, 'email': email}
        if not (username and valid_username(username)):
            kwargs['username_error'] = "That's not a valid username."
        if not (password and valid_password(password)):
            kwargs['password_error'] = "That wasn't a valid password."
        elif verify != password:
            kwargs['verify_error'] = "Your passwords didn't match."
        if email and not valid_email(email):
            kwargs['email_error'] = "That's not a valid email."
        if len(kwargs) == 2:  # if no errors in forms
            self.redirect('/welcome?username=%s' % username)
        else:
            self.write_page(**kwargs)  # display errors


class WelcomePage(RequestWrangler):
    template = 'welcome.html'
    
    def get(self):
        username = self.request.get('username')
        if username and valid_username(username):
            self.render(self.template, username=username)
        else:
            self.redirect('/signup')


class BlogPage(RequestWrangler):
    template = 'blog.html'
    
    def get(self):
        offset = self.request.get('o', '')
        if offset.isdigit() and int(offset) >= 0:
            offset = int(offset)
        else:
            offset = 0
        posts = Blog.get_posts(offset=offset)
        self.render(self.template, posts=posts, offset=offset)


class NewPostPage(RequestWrangler):
    template = 'newpost.html'
    
    def write_page(self, title='', content='', error=''):
        self.render(self.template, 
                    title=title, 
                    content=content, 
                    error=error)
    
    def get(self):
        self.write_page()
    
    def post(self):
        title = self.request.get('subject', '')
        content = self.request.get('content', '')
        if title and content:
            post = Blog.Post(title=title, content=content)
            key = post.put()
            self.redirect('/blog/%d' % key.id())
        else:
            error = 'Enter in both a title and content.'
            self.write_page(title=title, content=content, error=error)


class BlogPostPage(RequestWrangler):
    template = 'blogpost.html'
    
    def get(self, entity_id):
        entity_id = int(entity_id)
        if entity_id == 0:  # passing in 0 breaks datastore tsk tsk :(
            self.abort(404)
        post = Blog.Post.get_by_id(entity_id)
        if post:
            self.render(self.template, post=post)
        else:
            self.abort(404)


def valid_username(s):
    return bool(USER_RE.match(s))
    
def valid_password(s):
    return bool(PASS_RE.match(s))

def valid_email(s):
    return bool(EMAIL_RE.match(s))

app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/hello-udacity', HelloUdacityPage),
    ('/rot13', ROT13Page),
    ('/signup', SignupPage),
    ('/welcome', WelcomePage),
    ('/blog', BlogPage),
    ('/blog/newpost', NewPostPage),
    (r'/blog/(\d+)', BlogPostPage)
], debug=True)
