import webapp2
import jinja2
import os
import re
import random
import hashlib
import hmac
from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
j_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

secret = '$%&393njdk,2688u>n3kndjfAEJ<DI/ODOJKD'

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = j_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header('Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie',
            '%s=; Path=/' % ('user_id'))

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and Users.by_id(int(uid))

#############################################################
##################### DataBase ##############################
#############################################################

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class Users(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return Users.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = Users.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return Users(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

#############################################################
###################### Signup ###############################
#############################################################

user_val = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
password_val = re.compile(r"^.{3,20}$")
email_val = re.compile(r"^[\S]+@[\S]+.[\S]+$")

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
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.ver_pass = self.request.get('verify')
        self.email = self.request.get('email')

        user_frase = not self.val_usr(self.username)
        pass_frase = not self.val_pas(self.password)
        if self.email == "":
            email_frase = False
        else:
            email_frase = not self.val_email(self.email)

        if self.password != self.ver_pass or user_frase or pass_frase or email_frase:
            if self.password != self.ver_pass:
                vpass_frase = True
            else:
                vpass_frase = False

            self.render("sign-up.html", username=self.username, user_frase=user_frase, 
                pass_frase=pass_frase, vpass_frase=vpass_frase, email=self.email, 
                email_frase=email_frase)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        u = Users.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('sign-up.html', user_frase2 = True, user_frase=False)
        else:
            u = Users.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/welcome')

class Login(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        u = Users.login(self.username, self.password)
        if u:
            self.login(u)
            self.redirect('/welcome')
        else:
            msg = "Invalid username"
            self.render('login.html', msg = msg, username = self.username)

class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/signup')
        

class Welcome(Handler):
    def get(self):
        if self.user:
            self.render("welcome.html", username = self.user.name)
        else:
            self.redirect('/signup')

app = webapp2.WSGIApplication([('/signup', Register), ('/welcome', Welcome), 
                               ('/login', Login), ('/logout', Logout)], debug=True)
