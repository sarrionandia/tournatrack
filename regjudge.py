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

from models import Tournament
from models import PreRegRecord
from models import RegisteredIndependentJudge

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
					
		template_values = {
			'user' : user,
			't' : t,
			'logout' : tusers.create_logout_url('/'),
			'login' : tusers.create_login_url('/reg/judge?t=' + tid),
			'r' : reg,
			'nval' : True,
			'pval' : True,
			'eval' : True
			
		}
		template = JINJA_ENVIRONMENT.get_template('view/regjudge.html')
		self.response.write(template.render(template_values))
				

	def post(self):
		user = tusers.get_current_user()
		#Get the requested tournament
		tid = self.request.get('t')
		key = ndb.Key('Tournament', int(tid))
		t = key.get()
					
		if user:
			name = self.request.get('name')
			email = self.request.get('email')
			phone = self.request.get('phone')
			cv = self.request.get('cv')
			
			
			#Validate the form inputs
			name_valid = len(name)>0
			email_valid = EMAIL_REGEX.match(email) != None
			phone_valid = len(phone)>0
			reg = t.preRegRecord().get()
			
			#If valid, create the new judge object
			if (name_valid & phone_valid & email_valid):
				
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

				judge.name = name
				judge.phone = phone
				judge.email = email
				if len(cv)>0:
					judge.cv = cv
				judge.user = user.key
				judge.put()
				
				self.redirect('/reg?t=' + tid)
			else:
				template_values = {
					'user' : user,
					't' : t,
					'logout' : tusers.create_logout_url('/'),
					'login' : tusers.create_login_url('/reg/judge?t=' + tid),
					'r' : reg,
					'nval' : name_valid,
					'pval' : phone_valid,
					'eval' : email_valid
				}
				template = JINJA_ENVIRONMENT.get_template('view/regjudge.html')
				self.response.write(template.render(template_values))
		else:
			self.redirect('/reg?t=' + tid)
		
	
app = webapp2.WSGIApplication([
	('/reg/judge', RegHandler)
], debug=True)
