import webapp2
import jinja2
import os
import re
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
j_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = j_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    subject =  db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class FrontPage(Handler):
    def render_front(self):
        posts = db.GqlQuery("SELECT * FROM Blog "
                           "ORDER BY created DESC LIMIT 10")
        self.render("fpage.html", posts = posts)
    
    def get(self):
        self.render_front()

class FormHandler(Handler):
    def get(self):
        self.render("fhandler.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            a = Blog(subject = subject, content = content)
            a.put()
            self.redirect("/blog/%s" % str(a.key().id()))

        else:
            error = "we need both a Subject and a content!"
            self.render("fhandler.html", error = error)

class Permanlink(Handler):
    def get(self, id_element):
        key = db.Key.from_path('Blog', int(id_element))
        lastpost = db.get(key)

        if not lastpost:
            self.error(404)
            return

        self.render("permlink.html", lastpost = lastpost)

app = webapp2.WSGIApplication([('/blog', FrontPage), 
                               ('/blog/newpost', FormHandler),
                               ('/blog/([0-9]+)', Permanlink)], debug = True)