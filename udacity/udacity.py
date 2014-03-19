# 
# TODO: templating
# 

import webapp2
import string
import cgi
import re


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
home_html="""\
<html>
  <ul>
    <li><a href="/hello-udacity">Problem 1 - Hello, Udacity!</a></li>
    <li>Problem 2
      <ul>
        <li><a href="/rot13">Part 1 - ROT13</a></li>
        <li><a href="/signup">Part 2 - Signup</a></li>
      </ul>
    </li>
  <ul>
</html>
"""
rot13_html="""\
<html>
  <h2>Enter some text to ROT13:</h2>
  <form method="post">
    <textarea name="text" 
     style="height:100px;width:400px">%s</textarea>
     <br>
     <input type="submit"/>
  </form>
<html>
"""
signup_html="""\
<html>
  <head>
    <title>Signup</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>
  </head>
  <body>
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="%(username)s">
          </td>
          <td class="error">%(username_error)s</td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="">
          </td>
          <td class="error">%(password_error)s</td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="">
          </td>
          <td class="error">%(verify_error)s</td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="%(email)s">
          </td>
          <td class="error">%(email_error)s</td>
        </tr>
      </table>

      <input type="submit">
    </form>
  </body>

</html>
"""
welcome_html="""\
<html>
  <head>
    <title>Welcome</title>
  </head>
  <body>
    <h2>Welcome, %s!</h2>
  </body>
<html>
"""


class HomePage(webapp2.RequestHandler):
    def get(self):
        self.response.write(home_html)

class HelloUdacityPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, Udacity!')

class ROT13Page(webapp2.RequestHandler):
    def write_page(self, text=""):
        self.response.write(rot13_html % text)
    
    def get(self):
        self.write_page()
    
    def post(self):
        user_text = str(self.request.get("text"))
        rot13_text = self.rot13(user_text)
        self.write_page(cgi.escape(rot13_text, quote=True))
    
    def rot13(self, s):
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        rot13_lower = lowercase[13:] + lowercase[:13]
        rot13_upper = uppercase[13:] + uppercase[:13]
        trans_lower = string.maketrans(lowercase, rot13_lower)
        trans_upper = string.maketrans(uppercase, rot13_upper)
        return s.translate(trans_lower).translate(trans_upper)

class SignupPage(webapp2.RequestHandler):
    def write_page(self, username="", username_error="", 
                   password_error="", verify_error="", email="", 
                   email_error=""):
        replace = {'username': username, 
                   'username_error': username_error, 
                   'password_error': password_error,
                   'verify_error': verify_error, 
                   'email': email, 
                   'email_error': email_error}
        self.response.write(signup_html % replace)
    
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
            

class WelcomePage(webapp2.RequestHandler):
    def get(self):
        username = self.request.get("username")
        if username and valid_username(username):
            self.response.write(welcome_html % username)
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
