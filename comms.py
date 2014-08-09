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

from sendgrid import sendgrid
from sendgrid import message

import webapp2
import jinja2
import os
import logging

import ConfigParser

from google.appengine.ext import ndb
import tusers

from models import PreRegRecord

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class RecipientsHandler(webapp2.RequestHandler):
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

        iJudges = reg.indyJudges()
        teams = reg.teams()
        institutions = reg.institutions()


        template_values = {
          'user' : user,
          't' : t,
          'logout' : tusers.create_logout_url('/'),
          'r' : reg,
          'ijudges' : iJudges,
          'jcount' : reg.totalJudgeCount(),
          'teams' : teams,
          'institutions' : institutions,
          'tcount' : reg.totalTeamCount(),
          'icount' : institutions.count(limit=500),
        }
        template = JINJA_ENVIRONMENT.get_template('view/recipients.html')
        self.response.write(template.render(template_values))

      else:
        self.redirect('/tournaments')
    else:
      self.redirect(tusers.create_login_url(self.request.uri))

class SendHandler(webapp2.RequestHandler):
  def post(self):
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

        iJudges = reg.indyJudges()
        teams = reg.teams()
        institutions = reg.institutions()

        mail_from = "Tournatrack"
        subject = t.name
        body = self.request.get('mbody')
        body += "\n******\nYou are receiving this email because you registered for the %s at http://tournatrack.appspot.com"%t.name

        logging.info(body)

        #Get the username and password from the config file
        Config = ConfigParser.ConfigParser()
        Config.read('settings.ini')

        uname = Config.get('mail', 'uname')
        pw = Config.get('mail', 'password')

        #Open connection to SendGrid
        sendGrid = sendgrid.SendGridClient(uname, pw, secure=True)

        #Create the message
        comm = message.Mail(from_email=mail_from, from_name="Tournatrack", subject=subject, text=body)

        #Add teams if necessary
        if self.request.get('teams'):
          for t in teams:
            owner = t.user.get()
            comm.add_to(owner.preferredEmail())
            comm.add_to_name(owner.full_name)

        #Add judges if necessary
        if self.request.get('judges'):
          for j in iJudges:
            owner = j.user.get()
            comm.add_to(owner.preferredEmail())
            comm.add_to_name(owner.full_name)

        #Add institutions if necessary
        if self.request.get('institutions'):
          for i in institutions:
            owner = i.user.get()
            comm.add_to(owner.preferredEmail())
            comm.add_to_name(owner.full_name)


        sendGrid.send(comm)


        template_values = {
          'user' : user,
          't' : t,
          'logout' : tusers.create_logout_url('/'),
          'r' : reg,
          'ijudges' : iJudges,
          'jcount' : reg.totalJudgeCount(),
          'teams' : teams,
          'institutions' : institutions,
          'tcount' : reg.totalTeamCount(),
          'icount' : institutions.count(limit=500),
          'mbody' : self.request.get('mbody')
        }
        template = JINJA_ENVIRONMENT.get_template('view/recipients.html')
        self.response.write(template.render(template_values))

      else:
        self.redirect('/tournaments')
    else:
      self.redirect(tusers.create_login_url(self.request.uri))


app = webapp2.WSGIApplication([
  ('/comms', RecipientsHandler),
  ('/comms/send', SendHandler)
], debug=True)
