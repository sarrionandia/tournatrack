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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class HubHandler(webapp2.RequestHandler):
	def get(self):
		user = tusers.get_current_user()

		#Get the requested tournament
		tid = self.request.get('t')
		key = ndb.Key('Tournament', int(tid))
		t = key.get()

		reg = t.preRegRecord().get()

		isj = reg.isJudge(user)
		ist = reg.isOpenTeam(user)
		isi = reg.isInstitution(user)

		template_values = {
			'user' : user,
			't' : t,
			'logout' : tusers.create_logout_url('/'),
			'login' : tusers.create_login_url('/hub?t=' + tid),
			'r' : reg,
			'isj' : isj,
			'ist' : ist,
			'isi' : isi,
			'regd' : (isj!=None) or (ist!=None) or (isi!=None),
		}
		template = JINJA_ENVIRONMENT.get_template('view/hub.html')
		self.response.write(template.render(template_values))



app = webapp2.WSGIApplication([
	('/hub', HubHandler)
], debug=True)
