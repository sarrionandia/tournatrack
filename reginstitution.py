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

from wtforms import Form, TextField, validators

from models import RegisteredInstitution, InstitutionTeam, InstitutionJudge

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

MAX_REG = 20

class InstRegForm(Form):
	leadName = TextField('leadName', [validators.Required()])
	email = TextField('email', [validators.Email()])
	phone = TextField('phone', [validators.Required()])
	name = TextField('name', [validators.Required()])	

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

			form = InstRegForm(self.request.POST)
			if (form.validate()):
				
				#If we are updating an existing registration, update it.
				if 'instkey' in self.request.arguments():
					instkey = (self.request.get('instkey'))
					inst = ndb.Key(urlsafe=instkey).get()
					
					#Check they own it
					if inst.user != user.key:
						self.redirect('/reg?t=' + tid)
				
				#Otherwise, make a new institution registration
				else:
					inst = RegisteredInstitution(parent=reg.key)
				
				inst.leadName = form.leadName.data
				inst.phone = form.phone.data
				inst.email = form.email.data
				inst.name = form.name.data
				inst.user = user.key
				
				inst.put()
				
				#Add teams and judges
				if 'nTeams' in self.request.arguments():
					nTeams = int(self.request.get('nTeams'))
					if nTeams > MAX_REG:
						nTeams = MAX_REG
					for i in range(nTeams):
						team = InstitutionTeam(parent=inst.key)
						team.put()
						
				if 'nJudges' in self.request.arguments():
					nJudges = int(self.request.get('nJudges'))
					if nJudges > MAX_REG:
						nJudges = MAX_REG
					for i in range(nJudges):
						judge = InstitutionJudge(parent=inst.key)
						judge.put()
					
				self.redirect('/reg?t=' + tid)
				
			#If the form is invalid, show it again with errors.
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
				template = JINJA_ENVIRONMENT.get_template('view/reginstitution.html')
				self.response.write(template.render(template_values))
			
			
		else:
			self.redirect('/reg?t=' + tid)
		
	
app = webapp2.WSGIApplication([
	('/reg/institution', RegHandler)
], debug=True)
