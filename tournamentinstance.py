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
			#Get the requested tournament
			tid = self.request.get('t_key')
			key = ndb.Key('Tournament', int(tid))
			t = key.get()
			
			if (t and user in t.owner):
				template_values = {
					'user' : user,
					't' : t,
				}
				template = JINJA_ENVIRONMENT.get_template('view/tournament.html')
				self.response.write(template.render(template_values))
				
			else:
				self.redirect('/tournaments')
		else:
			self.redirect(users.create_login_url(self.request.uri))


app = webapp2.WSGIApplication([
	('/tournament_instance', TournamentsHandler)
], debug=True)
