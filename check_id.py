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

from google.appengine.ext import ndb
import tusers


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class IDHandler(webapp2.RequestHandler):
  def get(self):

    user = tusers.get_current_user()

    #If they're not authenticated deny the request
    if not user:
      self.error(404)
      return

    debater = None
    problem = "DebaterID not valid"

    if self.request.get('id'):
      try:
        dID = self.request.get('id')
        key = ndb.Key('TUser', int(dID))
        debater = key.get()
        problem = None
        if not debater.basic_info:
          problem = "The owner of this ID needs to add their full name and phone number before they can be registered."

      except:
        problem = "DebaterID not valid"

    template_values = {
        'problem' : problem,
        'debater' : debater
        }
    template = JINJA_ENVIRONMENT.get_template('view/json/check_id.json')
    self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
  ('/checkID', IDHandler)
], debug=True)
