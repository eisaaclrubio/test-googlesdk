import webapp2
import jinja2
import os
import re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
j_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

user_val = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
password_val = re.compile(r"^.{3,20}$")
email_val = re.compile(r"^[\S]+@[\S]+.[\S]+$")

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = j_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Users(db.Model):
    username = db.StringProperty(required = True)

class Signup(Handler):
    def val_usr(self, username):
        return user_val.match(username)

    def val_pas(self, password):
        return password_val.match(password)

    def val_email(self, email):
        return email_val.match(email)

    def get(self):
        self.render("sign-up.html")
    
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        ver_pass = self.request.get('verify')
        email = self.request.get('email')

        user_frase = not self.val_usr(username)
        pass_frase = not self.val_pas(password)
        if email == "":
            email_frase = False
        else:
            email_frase = not self.val_email(email)

        usrs = db.GqlQuery("SELECT * FROM Users")
        user_frase2 = False
        for usr in usrs:
            if username == usr.username:
                user_frase2 = True

        if password != ver_pass or user_frase2 or user_frase or pass_frase or email_frase:
            if password != ver_pass:
                vpass_frase = True
            else:
                vpass_frase = False

            self.render("sign-up.html", username=username, user_frase=user_frase,
                        user_frase2=user_frase2, pass_frase=pass_frase, 
                        vpass_frase=vpass_frase, email=email, email_frase=email_frase)
        else:
            a = Users(username = username)
            a.put()
            self.response.headers.add_header('Set-Cookie', 'username=%s' % str(username))
            self.redirect('/welcome')

class Welcome(Handler):
    def get(self):
        username = self.request.cookies.get('username')
        self.render("welcome.html", username = username)

app = webapp2.WSGIApplication([('/signup', Signup), ('/welcome', Welcome)], debug=True)
