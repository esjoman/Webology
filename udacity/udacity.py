import webapp2
import string
import cgi
import re
import os
import jinja2


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
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
    
    def write_page(self, username="", username_error="", 
                   password_error="", verify_error="", email="", 
                   email_error=""):
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
        username = self.request.get("username", "")
        password = self.request.get("password", "")
        verify = self.request.get("verify", "")
        email = self.request.get("email", "")
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
        username = self.request.get("username")
        if username and valid_username(username):
            self.render(self.template, username=username)
        else:
            self.redirect('/signup')


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
    ('/welcome', WelcomePage)
], debug=True)
