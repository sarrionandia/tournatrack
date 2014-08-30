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

import logging

from google.appengine.ext import ndb
import tusers

from forms import TeamForm
from reginstitution import InstRegForm

from wtforms import Form, BooleanField, TextField, validators

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class OpenDetailsHandler(webapp2.RequestHandler):
  def get(self):
    user = tusers.get_current_user()

    #Get the requested tournament
    tid = self.request.get('t')
    key = ndb.Key('Tournament', int(tid))
    t = key.get()

    reg = t.preRegRecord().get()

    ist = reg.isOpenTeam(user)

    # If they are already registered as a team, pre-populate the
    # modify teams form
    if (ist):
      form = TeamForm()
      form.teamName.data = ist.teamName
      form.sp1Name.data = ist.speaker1()
      form.sp2Name.data = ist.speaker2()
      form.sp1Novice.data = ist.sp1Novice
      form.sp2Novice.data = ist.sp2Novice
      form.sp1ESL.data = ist.sp1ESL
      form.sp2ESL.data = ist.sp2ESL

      if ist.sp1Key:
        form.sp1Key.data = ist.sp1Key.id()
      if ist.sp2Key:
        form.sp2Key.data = ist.sp2Key.id()

    else:
      self.redirect('/reg?t=' + tid)
      return

    template_values = {
      'user' : user,
      't' : t,
      'logout' : tusers.create_logout_url('/'),
      'login' : tusers.create_login_url('/reg?t=' + tid),
      'r' : reg,
      'ist' : ist,
      'form' : form,
    }
    template = JINJA_ENVIRONMENT.get_template('view/update_open_details.html')
    self.response.write(template.render(template_values))

  def post(self):
    user = tusers.get_current_user()
    #Get the requested tournament
    tid = self.request.get('t')
    key = ndb.Key('Tournament', int(tid))
    t = key.get()
    reg = t.preRegRecord().get()

    team = reg.isOpenTeam(user)

    if team:
      form = TeamForm(self.request.POST)

      #Check for debaterID links
      if form.sp1Key.data:
        team.linkSpeaker(1, form.sp1Key.data)
      else:
        team.sp1Key = None
        team.sp1Name = None
      if form.sp2Key.data:
        team.linkSpeaker(2, form.sp2Key.data)
      else:
        team.sp2Key = None
        team.sp2Name = None


      team.teamName = form.teamName.data
      team.sp1Name = form.sp1Name.data
      team.sp2Name = form.sp2Name.data
      team.sp1ESL = form.sp1ESL.data
      team.sp2ESL = form.sp2ESL.data
      team.sp1Novice = form.sp1Novice.data
      team.sp2Novice = form.sp2Novice.data




      team.put()
      self.redirect('/hub?t=' + tid)


    else:
      self.redirect('/reg?t=' + tid)
      return


app = webapp2.WSGIApplication([
  ('/reg/update_open_details', OpenDetailsHandler)
], debug=True)
