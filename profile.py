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
import logging

from google.appengine.ext import ndb
import tusers

from models import PerfSpeakerRecord

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class ProfileHandler(webapp2.RequestHandler):
  def get(self):
    user = tusers.get_current_user()

    profile_id = self.request.get('d')
    display_user = None
    is_self = False

    if profile_id:
      #Get the associated account
      requested_user = ndb.Key('TUser', int(profile_id)).get()

      #Check if the profile is public
      if requested_user and requested_user.public_profile:
        display_user = requested_user
      else:
        self.redirect('/')
        return

    elif user:
      requested_user = user
      is_self = True

      name = user.full_name
      current_institution = user.current_institution

      if (not name):
        self.redirect('/update_profile')
        return
    else:
      self.redirect('/')
      return

    #Find all speaker records
    speaker_q = PerfSpeakerRecord.query(ancestor=requested_user.key).order(-PerfSpeakerRecord.startDate)

    if speaker_q.count(limit=1) > 0:

      #Calculate average speaker points
      sumSpeaks = 0
      nSpeakerRecords = 0
      for result in speaker_q:
        sumSpeaks += result.averageSpeaks
        nSpeakerRecords += 1
        averageSpeaks = sumSpeaks / nSpeakerRecords

      #Adjust limits for graph
      nGraph = 5
      if self.request.get('nGraph'):
        nGraph = int(self.request.get('nGraph'))

      #Find all tournaments won
      won_q = speaker_q.filter(PerfSpeakerRecord.isWin == True).order(-PerfSpeakerRecord.startDate)

      #Find all tournaments broken
      break_q = speaker_q.filter(PerfSpeakerRecord.isBreak == True).order(-PerfSpeakerRecord.startDate)

      template_values = {
        'user' : user,
        'logout' : tusers.create_logout_url('/'),
        'average_speaks' : averageSpeaks,
        'win_count' : won_q.count(limit=1000),
        'break_count' : break_q.count(limit=1000),
        'wins' : won_q,
        'breaks' : break_q,
        'speaker_records' : speaker_q,
        'last_five' : speaker_q.fetch(nGraph),
        'own_profile' : is_self,
        'profile' : display_user,
        'nGraph' : nGraph
      }
    else:
      template_values = {
      'user' : user,
      'logout' : tusers.create_logout_url('/'),
      'empty' : True
      }
    template = JINJA_ENVIRONMENT.get_template('view/profile.html')
    self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
  ('/myProfile', ProfileHandler)
], debug=True)
