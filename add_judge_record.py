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
import string
import random
import datetime

from google.appengine.ext import ndb
import tusers

from models import Tournament, PerfJudgeRecord

from forms import JudgeRecordForm

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class JudgeRecordHandler(webapp2.RequestHandler):
  def get(self):
    user = tusers.get_current_user()

    if user:

      form = JudgeRecordForm()

      template_values = {
        'user' : user,
        'logout' : tusers.create_logout_url('/'),
        'form' : form
      }
      template = JINJA_ENVIRONMENT.get_template('view/add_judge_record.html')
      self.response.write(template.render(template_values))

    else:
      self.redirect(tusers.create_login_url(self.request.uri))

  def post(self):
    user = tusers.get_current_user()

    if user:

      form = JudgeRecordForm(self.request.POST)
      if (form.validate()):
        #Populate a new speaker record with the form data
        record = PerfJudgeRecord(parent=user.key)

        record.tournament = form.tournamentName.data
        record.startDate = form.startDate.data

        record.CA = form.CA.data
        record.DCA = form.DCA.data
        record.equity = form.equity.data

        record.chair = form.chair.data
        record.broke = form.broke.data
        record.outroundChair = form.outroundChair.data

        #Store whether or not there is an achievement in this record.
        if record.CA or record.DCA or record.equity or record.chair or record.broke or record.outroundChair:
          record.isAchievement = True
        else:
          record.isAchievement = False

        record.put()

        self.redirect('/myProfile')

      else:

        template_values = {
          'user' : user,
          'logout' : tusers.create_logout_url('/'),
          'form' : form
        }
        template = JINJA_ENVIRONMENT.get_template('view/add_speaker_record.html')
        self.response.write(template.render(template_values))

    else:
      self.redirect(tusers.create_login_url(self.request.uri))

app = webapp2.WSGIApplication([
  ('/myProfile/addJudgeRecord', JudgeRecordHandler)
], debug=True)
