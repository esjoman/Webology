import webapp2
import string
import cgi

home_html="""\
<html>
  <ul>
    <li><a href="/hello-udacity">Problem 1 - Hello, Udacity!</a></li>
    <li><a href="/rot13">Problem 2 - ROT13</a></li>
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


app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/hello-udacity', HelloUdacityPage),
    ('/rot13', ROT13Page)
], debug=True)
