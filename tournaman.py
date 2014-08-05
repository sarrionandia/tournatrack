# Copyright 2014 Roberto Brian Sarrionandia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
import jinja2
import os

from google.appengine.ext import ndb
import tusers

from models import PreRegRecord

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class TournamanHandler(webapp2.RequestHandler):
  def get(self):
    user = tusers.get_current_user()

    if user:
      #Get the requested tournament
      tid = self.request.get('t')
      key = ndb.Key('Tournament', int(tid))
      t = key.get()

      if (t and user.key in t.owner):
        reg = t.preRegRecord().get()
        if (reg == None):
          reg = PreRegRecord(parent=key)
          reg.open = False
          reg.put()

        template_values = {
          'user' : user,
          't' : t,
          'logout' : tusers.create_logout_url('/'),
          'r' : reg
        }
        template = JINJA_ENVIRONMENT.get_template('view/tournaman.html')
        self.response.write(template.render(template_values))

      else:
        self.redirect('/tournaments')
    else:
      self.redirect(tusers.create_login_url(self.request.uri))

class TournamanTeamsHandler(webapp2.RequestHandler):
  def get(self):
    user = tusers.get_current_user()

    if user:
      #Get the requested tournament
      tid = self.request.get('t')
      key = ndb.Key('Tournament', int(tid))
      t = key.get()

      if (t and user.key in t.owner):
        reg = t.preRegRecord().get()
        if (reg == None):
          reg = PreRegRecord(parent=key)
          reg.open = False
          reg.put()


        template_values = {
          'user' : user,
          't' : t,
          'logout' : tusers.create_logout_url('/'),
          'r' : reg,
          'teams' : reg.teams(),
          'institutions' : reg.institutions()
        }
        template = JINJA_ENVIRONMENT.get_template('view/tabexport/tournaman.csv')
        self.response.headers['Content-Type'] = 'text/csv'
        self.response.write(template.render(template_values))

      else:
        self.redirect('/tournaments')
    else:
      self.redirect(tusers.create_login_url(self.request.uri))

class TournamanJudgesHandler(webapp2.RequestHandler):
  def get(self):
    user = tusers.get_current_user()

    if user:
      #Get the requested tournament
      tid = self.request.get('t')
      key = ndb.Key('Tournament', int(tid))
      t = key.get()

      if (t and user.key in t.owner):
        reg = t.preRegRecord().get()
        if (reg == None):
          reg = PreRegRecord(parent=key)
          reg.open = False
          reg.put()


        template_values = {
          'user' : user,
          't' : t,
          'logout' : tusers.create_logout_url('/'),
          'r' : reg,
          'i_judges' : reg.indyJudges(),
          'institutions' : reg.institutions()
        }
        template = JINJA_ENVIRONMENT.get_template('view/tabexport/tournaman_j.csv')
        self.response.headers['Content-Type'] = 'text/csv'
        self.response.write(template.render(template_values))

      else:
        self.redirect('/tournaments')
    else:
      self.redirect(tusers.create_login_url(self.request.uri))

app = webapp2.WSGIApplication([
  ('/tab/tournaman', TournamanHandler),
  ('/tab/tournaman/teams.csv', TournamanTeamsHandler),
  ('/tab/tournaman/judges.csv', TournamanJudgesHandler)
], debug=True)
