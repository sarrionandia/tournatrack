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
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from models import Tournament
from models import Institution

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class InstitutionHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		#Get the requested tournament
		tid = self.request.get('t')
		t_key = ndb.Key('Tournament', int(tid))
		t = t_key.get()
				
		if (user and user in t.owner):
			#Get the institution in question
			rid = self.request.get('r')
			r_key = ndb.Key('Tournament', int(tid), 'Room', int(rid))
			#Unceremoniously delete it
			r_key.delete()
			
			#Send the user back to the institution list
			self.redirect('/room?t=' + str(t_key.id()))
						
		else:
			self.redirect(users.create_login_url(self.request.uri))
	

app = webapp2.WSGIApplication([
	('/del_r', InstitutionHandler)
], debug=True)
