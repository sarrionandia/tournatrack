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

from models import Tournament, PerfSpeakerRecord

from forms import SpeakerRecordForm

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class SpeakerRecordHandler(webapp2.RequestHandler):
  def get(self):
    user = tusers.get_current_user()

    if user:

      form = SpeakerRecordForm()

      template_values = {
        'user' : user,
        'logout' : tusers.create_logout_url('/'),
        'form' : form
      }
      template = JINJA_ENVIRONMENT.get_template('view/add_speaker_record.html')
      self.response.write(template.render(template_values))

    else:
      self.redirect(tusers.create_login_url(self.request.uri))

  def post(self):
    user = tusers.get_current_user()

    if user:

      form = SpeakerRecordForm(self.request.POST)
      if (form.validate()):
        #Populate a new speaker record with the form data
        record = PerfSpeakerRecord(parent=user.key)

        record.tournament = form.tournamentName.data
        record.startDate = form.startDate.data
        record.teamName = form.teamName.data

        record.teamRank = form.teamRank.data
        record.averageSpeaks = float(form.averageSpeaks.data)
        record.speakerRank = form.speakerRank.data

        record.champion = form.champion.data
        record.finalist = form.finalist.data
        record.semifinalist = form.semifinalist.data
        record.quarterfinalist = form.quarterfinalist.data
        record.octofinalist = form.octofinalist.data
        record.doubleoctofinalist = form.doubleoctofinalist.data

        record.ESLBreak = form.eslBreak.data
        record.ESLChampion = form.eslChampion.data
        record.EFLBreak = form.eflBreak.data
        record.EFLChampion = form.eflChampion.data

        record.NoviceBreak = form.noviceBreak.data
        record.NoviceChampion = form.noviceChampion.data

        #Check if this is a breaking record
        if record.finalist or record.semifinalist or record.quarterfinalist or record.octofinalist or record.doubleoctofinalist or record.NoviceBreak or record.ESLBreak or record.EFLBreak:
          record.isBreak = True
        else:
          record.isBreak = False

        #Check if this is a winning record
        if record.champion or record.NoviceChampion or record.ESLChampion or record.EFLChampion:
          record.isWin = True
        else:
          record.isWin = False

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
  ('/myProfile/addSpeakerRecord', SpeakerRecordHandler)
], debug=True)
