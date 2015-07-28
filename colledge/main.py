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
import datetime
from google.appengine.ext import ndb
from google.appengine.api import users

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class College(ndb.Model):
    name = ndb.StringProperty(required=True)

class Event(ndb.Model):
   name = ndb.StringProperty(required=True)
   school = ndb.KeyProperty(kind=College)

class Post(ndb.Model):
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    timestamp = ndb.DateTimeProperty(required=True)
    event = ndb.KeyProperty(kind=Event)

#navigate to a page to create a profile when they log in for the first time
class Profile(ndb.Model):
    email = ndb.StringProperty(required=True)
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
    school = ndb.KeyProperty(kind=College)

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('login.html')
        user = users.get_current_user()
        if user:
            self.redirect('/school')
            greeting = ('Welcome, %s! (<a href="%s" class="btn">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            greeting = ('<a href="%s"class="btn">Sign in or register</a>.' %
                        users.create_login_url(dest_url='/setup', _auth_domain=None, federated_identity=None
                        ))

        #self.response.out.write('<html><body>%s</body></html>' % greeting)
        self.response.write(template.render({"greeting": greeting}))


class SchoolHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        user_email = user.email()
        profiles = Profile.query( user_email == Profile.email ).fetch()
        profile = profiles[0]
        template = env.get_template('main.html')
        events = Event.query().fetch() #eventually add only the ones for this school using event.school == schoolkey
        user = users.get_current_user()
        greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                    (user.nickname(), users.create_logout_url('/')))
        variables = {'events': events, 'greeting': greeting, 'profile': profile }
        self.response.write(template.render(variables))

    def post(self):
        title = self.request.get('title')
        event = Event(name="title", school = ndb.Key(College, 'ucsc'))
        event.put()
        return self.redirect("/school")

class EventHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        user_email = user.email()
        profiles = Profile.query( user_email == Profile.email ).fetch()
        profile = profiles[0]
        template = env.get_template('event.html')
        posts = Post.query().fetch()
        posts.sort(key=lambda x: x.timestamp, reverse=True)
        variables = {'posts': posts, 'profile': profile }
        self.response.write(template.render(variables))

    def post(self):
        template = env.get_template('main.html')
        content = self.request.get('content')
        title = self.request.get('title')
        timestamp = self.request.get('timestamp')
        post = Post(title=title, content=content,
                    timestamp=datetime.datetime.now())
        post.put()
        return self.redirect("/event")


class SetupHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        user_email = user.email()
        if(Profile.query(Profile.email==user_email).fetch()):
            self.redirect('/school')
        else:
            template = env.get_template('setup.html')
            self.response.write(template.render())


    def post(self):
        georgetown = College(name="Georgetown", id="georgetown")
        georgetown.put()
        ucsc = College(name="UCSC", id="ucsc")
        ucsc.put()
        ucberkley = College(name="UC Berkley", id='ucberkley')
        ucberkley.put()

        user = users.get_current_user()
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        school = self.request.get('school')
        email = user.nickname() + "@gmail.com"
        if school == 'georgetown':
            college = ndb.Key(College, "georgetown")
        elif school == 'ucsc':
            college = ndb.Key(College, "ucsc")
        else:
            college = ndb.Key(College, "ucberkley")
        profile = Profile(email=email, first_name=first_name,
                          last_name=last_name, school=college)
        profile.put()
        profile_key = profile.key.urlsafe()
        #urlsafe_key = ndb.Key(urlsafe=profile_key)
        self.redirect('/success?key=%s' %profile_key )



class SuccessHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('success.html')
        key = self.request.get('key')
        urlsafe_key = ndb.Key(urlsafe=key)
        profile = urlsafe_key.get()

        '''
        user = users.get_current_user()
        user_email = user.email()
        profiles = Profile.query( user_email == Profile.email ).fetch()
        profile = profiles[0]
        '''
        variables = {'profile': profile }
        self.response.write(template.render(variables))

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('profile.html')
        user = users.get_current_user()
        user_email = user.email()
        profiles = Profile.query( user_email == Profile.email ).fetch()
        profile = profiles[0]
        variables = {'profile': profile }
        self.response.write(template.render(variables))


class AboutHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('about.html')
        user = users.get_current_user()
        user_email = user.email()
        profiles = Profile.query( user_email == Profile.email ).fetch()
        profile = profiles[0]
        variables = {'profile': profile }
        self.response.write(template.render(variables))


app = webapp2.WSGIApplication([
    ('/', LoginHandler), #login page
    ('/school', SchoolHandler), #school feed, "school.html"
    ('/profile', ProfileHandler), #your profile, "profile.html"
    ('/about', AboutHandler), #about the website, "about.html"
    ('/setup', SetupHandler), #set up your accout, "setup.html"
    ('/success', SuccessHandler), #you have successfully created your account
    ('/event', EventHandler) #your account was successfully created, "profile.html"

], debug=True)
