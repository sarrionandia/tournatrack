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

from wtforms import Form, TextField, TextAreaField, validators

from models import RegisteredIndependentJudge, Attending
from forms import JudgeForm

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class RegHandler(webapp2.RequestHandler):
	def get(self):
		user = tusers.get_current_user()
		
		#Get the requested tournament
		tid = self.request.get('t')
		key = ndb.Key('Tournament', int(tid))
		t = key.get()
			
		reg = t.preRegRecord().get()

		form = JudgeForm()
					
		template_values = {
			'user' : user,
			't' : t,
			'logout' : tusers.create_logout_url('/'),
			'login' : tusers.create_login_url('/reg/judge?t=' + tid),
			'r' : reg,
			'form' : form,
		}
		template = JINJA_ENVIRONMENT.get_template('view/regjudge.html')
		self.response.write(template.render(template_values))
				

	def post(self):
		user = tusers.get_current_user()
		#Get the requested tournament
		tid = self.request.get('t')
		key = ndb.Key('Tournament', int(tid))
		t = key.get()
		reg = t.preRegRecord().get()

					
		if user:

			#Check they haven't registered already
			if reg.isRegistered(user):
				self.redirect('/reg?t=' + tid)
				return

			form = JudgeForm(self.request.POST)

			#If valid, create the new judge object
			if (form.validate()):
				
				#Check if we are updating an existing judge
				if not self.request.get('j'):
					judge = RegisteredIndependentJudge(parent=reg.key)
					judge.user = user.key

				else:
					judge = ndb.Key('Tournament', int(tid), 'PreRegRecord', reg.key.id(), 'RegisteredIndependentJudge', int(self.request.get('j'))).get()

				#Check we are authorised
				if not ((judge.user == user.key) or (user.key in t.owner)):
					judge = None
					self.redirect('/')

				judge.name = form.name.data
				judge.phone = form.phone.data
				judge.email = form.email.data
				judge.cv = form.cv.data

				judge.put()

				#Add an attendance record
				attending = Attending(parent=user.key)
				attending.role = "Institution"
				attending.tournament = t.key
				attending.put()

				
				self.redirect('/reg?t=' + tid)
			else:
				template_values = {
					'user' : user,
					't' : t,
					'logout' : tusers.create_logout_url('/'),
					'login' : tusers.create_login_url('/reg/judge?t=' + tid),
					'r' : reg,
					'form' : form,
				}
				template = JINJA_ENVIRONMENT.get_template('view/regjudge.html')
				self.response.write(template.render(template_values))
		else:
			self.redirect('/reg?t=' + tid)
		
	
app = webapp2.WSGIApplication([
	('/reg/judge', RegHandler)
], debug=True)
