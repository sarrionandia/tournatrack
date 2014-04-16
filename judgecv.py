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
import os

from google.appengine.ext import ndb
import tusers
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class JudgeCVHandler(webapp2.RequestHandler):
	def get(self):
		user = tusers.get_current_user()
		
		if user:
			#Get the requested tournament
			tid = self.request.get('t')
			key = ndb.Key('Tournament', int(tid))
			t = key.get()
			j = self.request.get('j')

			if (self.request.get('j', default_value=False)):
				j_string = self.request.get('j')
				j_key = ndb.Key(urlsafe=j_string)
				tournament = j_key.parent().parent().parent().get()
				if user.key in tournament.owner:
					judge = j_key.get()
					template_values = {
						'judge': judge
					}
					template = JINJA_ENVIRONMENT.get_template('view/judgecv.html')
					self.response.write(template.render(template_values))
			
			elif (t and user.key in t.owner):
				reg = t.preRegRecord().get()
				judge = ndb.Key('RegisteredIndependentJudge', int(j), parent=reg.key)
					
				template_values = {
					'judge': judge.get()
				}
				template = JINJA_ENVIRONMENT.get_template('view/judgecv.html')
				self.response.write(template.render(template_values))
				
			else:
				self.redirect('/tournaments')
		else:
			self.redirect(tusers.create_login_url(self.request.uri))


			

app = webapp2.WSGIApplication([
	('/judgecv', JudgeCVHandler)
], debug=True)
