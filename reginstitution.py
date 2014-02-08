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
import re
import logging

from google.appengine.ext import ndb
import tusers

from wtforms import Form, BooleanField, TextField, validators

from models import Tournament, PreRegRecord, RegisteredInstitution

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class InstRegForm(Form):
	leadName = TextField('leadName', [validators.Required()])
	email = TextField('email', [validators.Email()])
	phone = TextField('phone', [validators.Required()])
	name = TextField('teamName', [validators.Required()])	

class RegHandler(webapp2.RequestHandler):
	def get(self):
		user = tusers.get_current_user()
		
		#Get the requested tournament
		tid = self.request.get('t')
		key = ndb.Key('Tournament', int(tid))
		t = key.get()
			
		reg = t.preRegRecord().get()
		
		form = InstRegForm()
					
		template_values = {
			'user' : user,
			't' : t,
			'logout' : tusers.create_logout_url('/'),
			'login' : tusers.create_login_url('/reg/team?t=' + tid),
			'r' : reg,
			'form' : form		
		}
		template = JINJA_ENVIRONMENT.get_template('view/reginstitution.html')
		self.response.write(template.render(template_values))
				

	
app = webapp2.WSGIApplication([
	('/reg/institution', RegHandler)
], debug=True)
