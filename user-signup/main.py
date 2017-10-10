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

import webapp2
import jinja2
import os

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

class MainPage(Handler):
    def get(self):
        self.render("sign-up.html")        
    
    def post(self):
        v = self.request.get('area')
        le = len(v)
        for ch in range(0,le):
            value = v[ch]
            ascv = ord(value)
            if ascv < 78 and ascv>=65:
                v = v[:ch] + chr(ascv+13)+v[ch+1:]
            elif ascv >=78 and ascv<=90:
                v = v[:ch] + chr(ascv-13)+v[ch+1:]
            elif ascv < 110 and ascv>=97:
                v = v[:ch] + chr(ascv+13)+v[ch+1:]
            elif ascv >=110 and ascv<=122:
                v = v[:ch] + chr(ascv-13)+v[ch+1:]

        self.render("sign-up.html", v=v)


app = webapp2.WSGIApplication([('/exercises/signup', MainPage)],debug=True)
