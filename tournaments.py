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
from google.appengine.api import users

from models import Tournament

def pin_gen(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class TournamentsHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		
		if user:
			
			#Get a list of tournaments that the user owns
			q = Tournament.query(Tournament.owner == user)
			
			template_values = {
				'user' : user,
				'tournaments' : q,
				'logout' : users.create_logout_url('/'),
			}
			template = JINJA_ENVIRONMENT.get_template('view/tournaments.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

	#Create a new tournament object
	def post(self):
		user = users.get_current_user()

		if user:
			#Check if we are modifying a tournament or making a new one
			if self.request.get('id'):
				new_tournament = ndb.Key('Tournament', int(self.request.get('id'))).get()
			else:
				new_tournament = Tournament()
			new_tournament.name = self.request.get('name')
			new_tournament.owner.append(user)
			new_tournament.trackpin = pin_gen()
						
			dates_valid = True
			
			try:
				new_tournament.start = datetime.datetime.strptime(self.request.get('start'), '%Y-%m-%d').date()
				new_tournament.end = datetime.datetime.strptime(self.request.get('end'), '%Y-%m-%d').date()
			except ValueError:
				dates_valid = False
				
			if (dates_valid and len(new_tournament.name) > 5):
				new_tournament.put()
			#Send the user back to the tournaments page
			self.redirect('/tournaments')
			
			#Reserve the list of tournaments
			q = Tournament.query(Tournament.owner == user)
			
			template_values = {
				'user' : user,
				'tournaments' : q,
				'logout' : users.create_logout_url('/'),
			}
			template = JINJA_ENVIRONMENT.get_template('view/tournaments.html')
			self.response.write(template.render(template_values))
			
		else:
			self.redirect(users.create_login_url(self.request.uri))
	

app = webapp2.WSGIApplication([
	('/tournaments', TournamentsHandler)
], debug=True)
