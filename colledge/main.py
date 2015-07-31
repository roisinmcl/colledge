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
from google.appengine.api import images
from google.appengine.ext import ndb
from google.appengine.api import users

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

def get_logged_in_user():
    user = users.get_current_user()
    user_email = user.email()
    profiles = Profile.query( user_email == Profile.email ).fetch()
    profile = profiles[0]
    return profile

class College(ndb.Model):
    name = ndb.StringProperty(required=True)

class Event(ndb.Model):
   name = ndb.StringProperty(required=True)
   school = ndb.KeyProperty(kind=College)

class Profile(ndb.Model):
   email = ndb.StringProperty(required=True)
   first_name = ndb.StringProperty(required=True)
   last_name = ndb.StringProperty(required=True)
   school = ndb.KeyProperty(kind=College)
   img = ndb.BlobProperty()
   bio = ndb.StringProperty()

class Post(ndb.Model):
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    img = ndb.BlobProperty()
    timestamp = ndb.DateTimeProperty(required=True)
    event = ndb.KeyProperty(kind=Event)
    profile = ndb.KeyProperty(kind=Profile)

class Comment(ndb.Model):
    content = ndb.StringProperty(required=True)
    profile = ndb.KeyProperty(kind=Profile)
    post = ndb.KeyProperty(kind=Post)
    timestamp = ndb.DateTimeProperty(required=True)

#navigate to a page to create a profile when they log in for the first time

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

        profile = get_logged_in_user()
        '''
        user = users.get_current_user()
        user_email = user.email()
        profiles = Profile.query( user_email == Profile.email ).fetch()
        profile = profiles[0]
        '''
        template = env.get_template('main.html')
        events = Event.query( Event.school == profile.school ).fetch() # added search query
        user = users.get_current_user()
        greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                    (profile.first_name, users.create_logout_url('/')))
        logout = users.create_logout_url('/')
        variables = {'events': events, 'greeting': greeting, 'profile': profile, 'logout': logout }
        self.response.write(template.render(variables))

    def post(self):
        profile = get_logged_in_user()
        title = self.request.get('title')
        event = Event(name=title, school = profile.school)
        event.put()
        self.redirect("/school")

class EventHandler(webapp2.RequestHandler):
    def get(self):
        profile = get_logged_in_user()
        template = env.get_template('event.html')
        key = self.request.get('key')
        urlsafe_key = ndb.Key(urlsafe=key)
        event = urlsafe_key.get()
        posts = Post.query( Post.event == event.key ).fetch() # this line query added
        posts.sort(key=lambda x: x.timestamp, reverse=True)
        logout = users.create_logout_url('/')
        variables = {'posts': posts, 'profile': profile, 'event': event, "logout": logout }
        self.response.write(template.render(variables))

    def post(self):
        profile = get_logged_in_user()
        content = self.request.get('content')
        title = self.request.get('title')
        timestamp = self.request.get('timestamp')
        img = self.request.get('img') or None
        key = self.request.get('key')

        event_key = ndb.Key(urlsafe=key) #im working on this line
        #profile = event_key.get()

        post = Post(title=title,
                    content=content,
                    img=img,
                    timestamp=datetime.datetime.now(),
                    event=event_key, profile=profile.key)
        post.put()
        return self.redirect("/event?key=%s" %key)


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
        ucberkeley = College(name="UC Berkeley", id='ucberkeley')
        ucberkeley.put()
        ucdavis = College(name="UC Davis", id='ucdavis')
        ucdavis.put()
        columbia = College(name="Columbia", id='columbia')
        columbia.put()
        stanford = College(name="Stanford", id='stanford')
        stanford.put()
        harvard = College(name="Harvard", id='harvard')
        harvard.put()
        sjsu = College(name="San Jose State Univeristy", id='sjsu')
        sjsu.put()
        scripps = College(name="Scripps College", id='scripps')
        scripps.put()
        calpoly = College(name="Caly Poly", id='calpoly')
        calpoly.put()
        usc = College(name="USC", id='usc')
        usc.put()


        user = users.get_current_user()
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        school = self.request.get('school')
        email = user.email()
        if school == 'georgetown':
            college = ndb.Key(College, "georgetown")
        elif school == 'ucsc':
            college = ndb.Key(College, "ucsc")
        elif school == 'ucdavis':
            college = ndb.Key(College, "ucdavis")
        elif school == 'columbia':
            college = ndb.Key(College, "columbia")
        elif school == 'stanford':
            college = ndb.Key(College, "stanford")
        elif school == 'harvard':
            college = ndb.Key(College, "harvard")
        elif school == 'sjsu':
            college = ndb.Key(College, "sjsu")
        elif school == 'scripps':
            college = ndb.Key(College, "scripps")
        elif school == 'calpoly':
            college = ndb.Key(College, "calpoly")
        elif school == 'usc':
            college = ndb.Key(College, "usc")
        else:
            college = ndb.Key(College, "ucberkeley")

        profile = Profile(email=email, first_name=first_name,
                          last_name=last_name, school=college)
        profile.put()
        profile_key = profile.key.urlsafe()
        #urlsafe_key = ndb.Key(urlsafe=profile_key)
        #profiles = Profile.query( user_email == Profile.email ).fetch()
        #profile = profiles[0]
        self.redirect('/success?key=%s' %profile_key )



class SuccessHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('success.html')
        key = self.request.get('key')
        urlsafe_key = ndb.Key(urlsafe=key)
        profile = urlsafe_key.get()
        user = users.get_current_user()
        user_email = user.email()
        profiles = Profile.query( user_email == Profile.email ).fetch()
        if len(profiles) > 0:
            profile_object = profiles[0]
        logout = users.create_logout_url('/')
        variables = {'profile': profile, 'logout': logout }
        self.response.write(template.render(variables))

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('profile.html')
        logout = users.create_logout_url('/')
        profile = get_logged_in_user()
        #user = users.get_current_user()
        #user_email = user.email()
        #profiles = Profile.query( user_email == Profile.email ).fetch()
        #profile = profiles[0]
        variables = {'profile': profile, 'logout':logout }
        self.response.write(template.render(variables))
    def post(self):
        profile = get_logged_in_user()
        profile.name = "User name"
        profile.img = self.request.get('img')
        profile.put()
        self.redirect('/profile')

class AboutHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('about.html')
        profile = get_logged_in_user()
        logout = users.create_logout_url('/')
        variables = {'profile': profile, 'logout': logout }
        self.response.write(template.render(variables))

class ImageHandler(webapp2.RequestHandler):
    def get(self):
        post_id = self.request.get('post_id')
        post_id_key = ndb.Key(urlsafe=post_id)
        post_model = post_id_key.get()
        self.response.write(post_model.img)

class OtherProfileHander(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('otherprofile.html')
        key = self.request.get('key')
        #self.response.write(key)
        profile_key = ndb.Key(urlsafe=key)
        profile = profile_key.get()
        variables = {'profile': profile}
        self.response.write(template.render(variables))

class CommentHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('comment.html')
        key = self.request.get('key')
        #self.response.write(key)
        post_key = ndb.Key(urlsafe=key)
        post = post_key.get()
        comments = Comment.query(Comment.post == post.key).fetch()
        comments.sort(key=lambda x: x.timestamp)
        variables = {'post': post, 'comments': comments}
        self.response.write(template.render(variables))


    def post(self):
        urlsafe_post = self.request.get('key')
        post_key = ndb.Key(urlsafe=urlsafe_post)
        post = post_key.get()
        profile = get_logged_in_user()
        content = self.request.get('content')
        comment = Comment(content=content, profile=profile.key,
                          post=post.key, timestamp=datetime.datetime.now())
        comment.put()
        self.redirect("/comment?key=%s" %urlsafe_post )


class BioHandler(webapp2.RequestHandler):
    def post(self):
        profile = get_logged_in_user()
        profile.bio = self.request.get('bio')
        profile.put()
        self.redirect('/profile')



app = webapp2.WSGIApplication([
    ('/', LoginHandler), #login page
    ('/school', SchoolHandler), #school feed, "school.html"
    ('/profile', ProfileHandler,), #your profile, "profile.html"
    ('/about', AboutHandler), #about the website, "about.html"
    ('/setup', SetupHandler), #set up your accout, "setup.html"
    ('/success', SuccessHandler), #you have successfully created your account
    ('/event', EventHandler), #your account was successfully created, "profile.html"
    ('/img', ImageHandler),
    ('/otherprofile', OtherProfileHander),
    ('/comment', CommentHandler),
    ('/bio', BioHandler)

], debug=True)
