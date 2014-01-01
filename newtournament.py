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

from google.appengine.api import users

from models import Tournament

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def pin_gen(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))


class NewTournamentHandler(webapp2.RequestHandler):
		
	def get(self):
		user = users.get_current_user()
		
		if user:
			#Output the form to create a new tournament			
			template_values = {
				'user' : user,
			}
			template = JINJA_ENVIRONMENT.get_template('view/tournament_form.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))
			
	def post(self):
		user = users.get_current_user()
		
		if user:
			#Create the tournament object
			new_tournament = Tournament()
			new_tournament.name = self.request.get('tournament_name')
			new_tournament.owner.append(user)
			new_tournament.trackpin = pin_gen()
			new_tournament.put()
			#Send the user back to the tournaments page
			self.redirect('/tournaments')
		else:
			self.redirect(users.create_login_url(self.request.uri))


app = webapp2.WSGIApplication([
	('/new_tournament', NewTournamentHandler)
], debug=True)
