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

from models import RegisteredOpenTeam
from forms import TeamForm

EMAIL_REGEX = re.compile('^[_.0-9a-z-]+@([0-9a-z][0-9a-z-]+.)+[a-z]{2,4}$')

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
		
		form = TeamForm()
					
		template_values = {
			'user' : user,
			't' : t,
			'logout' : tusers.create_logout_url('/'),
			'login' : tusers.create_login_url('/reg/team?t=' + tid),
			'r' : reg,
			'form' : form		
		}
		template = JINJA_ENVIRONMENT.get_template('view/regteam.html')
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

			form = TeamForm(self.request.POST)
			if (form.validate()):
				
				#If we are updating an existing registration, update it.
				if 'teamkey' in self.request.arguments():
					teamkey = (self.request.get('teamkey'))
					team = ndb.Key(urlsafe=teamkey).get()
					
					#Check they own it
					if team.user != user.key:
						self.redirect('/reg?t=' + tid)
				
				#Otherwise, make a new team registration
				else:
					team = RegisteredOpenTeam(parent=reg.key)
				
				team.leadName = form.leadName.data
				team.phone = form.phone.data
				team.email = form.email.data
				team.teamName = form.teamName.data
				team.sp1Name = form.sp1Name.data
				team.sp2Name = form.sp2Name.data
				team.sp1ESL = form.sp1ESL.data
				team.sp2ESL = form.sp2ESL.data
				team.sp1Novice = form.sp1Novice.data
				team.sp2Novice = form.sp2Novice.data
				team.leadname = form.leadName.data
				team.user = user.key
				
				team.put()
				
				self.redirect('/reg?t=' + tid)
			else:
				logging.info('invalid form')
				template_values = {
					'user' : user,
					't' : t,
					'logout' : tusers.create_logout_url('/'),
					'login' : tusers.create_login_url('/reg/team?t=' + tid),
					'r' : reg,
					'form' : form		
				}
				template = JINJA_ENVIRONMENT.get_template('view/regteam.html')
				self.response.write(template.render(template_values))
			
			
		else:
			self.redirect('/reg?t=' + tid)
		
	
app = webapp2.WSGIApplication([
	('/reg/team', RegHandler)
], debug=True)
