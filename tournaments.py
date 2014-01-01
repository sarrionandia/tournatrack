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

from google.appengine.api import users

from models import Tournament

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
			}
			template = JINJA_ENVIRONMENT.get_template('tournaments.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))


app = webapp2.WSGIApplication([
	('/tournaments', TournamentsHandler)
], debug=True)
