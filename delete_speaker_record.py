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

import logging

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class DeleteSpeakerRecordHandler(webapp2.RequestHandler):

  def post(self):
    user = tusers.get_current_user()

    if user:

      recordID = self.request.get('record')
      recordKey = ndb.Key(urlsafe = recordID)

      if recordKey.parent() == user.key:
        recordKey.delete()

      self.redirect('/myProfile')

    else:
      self.redirect(tusers.create_login_url(self.request.uri))

app = webapp2.WSGIApplication([
  ('/myProfile/deleteSpeakerRecord', DeleteSpeakerRecordHandler)
], debug=True)
