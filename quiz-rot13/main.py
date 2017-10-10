# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -*- coding: utf-8 -*-

import webapp2
import jinja2
import os
import re

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

class Rot13(Handler):
    def get(self):
        self.render("rot13.html")        
    
    def post(self):
        v = self.request.get('text')
        #le = len(v)
        #for ch in range(0,le):
            #value = v[ch]
            #ascv = ord(value)
            #if ascv < 78 and ascv>=65:
               #v = v[:ch] + chr(ascv+13)+v[ch+1:]
            #elif ascv >=78 and ascv<=90:
                #v = v[:ch] + chr(ascv-13)+v[ch+1:]
            #elif ascv < 110 and ascv>=97:
                #v = v[:ch] + chr(ascv+13)+v[ch+1:]
            #elif ascv >=110 and ascv<=122:
                #v = v[:ch] + chr(ascv-13)+v[ch+1:]
        rot13 = ''
        if v:
            rot13 = v.encode('rot13')
        self.render("rot13.html", v=rot13)

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

        if password != ver_pass or user_frase or pass_frase or email_frase:
            if password != ver_pass:
                vpass_frase = True
            else:
                vpass_frase = False
            self.render("sign-up.html", username=username, user_frase=user_frase,
                        pass_frase=pass_frase, vpass_frase=vpass_frase,
                        email=email, email_frase=email_frase)
        else:
            self.redirect('/exercises/welcome?username=' + username)

class Welcome(Handler):
    def get(self):
        username = self.request.get('username')
        self.render("welcome.html", username = username)

app = webapp2.WSGIApplication([('/exercises/quiz-rot13', Rot13), ('/exercises/signup', Signup),
