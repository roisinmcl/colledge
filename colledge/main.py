#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
import webapp2
import jinja2
from google.appengine.api import users

#global variable which uses FileSystemLoader to load templates folder
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

#Login
class LoginHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('login.html')
        user = users.get_current_user()
        if user:
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/'))

        #self.response.out.write('<html><body>%s</body></html>' % greeting)
        self.response.write(greeting)

#Homepage
class HomeHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('home.html')
        self.response.write('This is the home page')

#Profile
class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('profile.html')
        self.response.write('This is a profile page')

#College
class CollegeHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('college.html')
        self.response.write('This is a college')

app = webapp2.WSGIApplication([
    ('/', LoginHandler),
    ('/home', HomeHandler),
    ('/profile', ProfileHandler),
    ('/college', CollegeHandler)
], debug=True)
